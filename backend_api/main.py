from __future__ import annotations

import json
import logging
import os
import shutil
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.append(str(SRC_ROOT))

from backend_api.content import RESOURCE_ITEMS, TEAM_MEMBERS
from backend_api.run_artifact_store import RunArtifactStore
from backend_api.settings import load_settings

if TYPE_CHECKING:
    from pipeline_service import PipelineServiceConfig


SETTINGS = load_settings(PROJECT_ROOT)
POPPLER_BIN = SETTINGS.poppler_path
API_RUNS_ROOT = SETTINGS.api_runs_root
README_PATH = SETTINGS.readme_path
RUN_ARTIFACT_STORE = RunArtifactStore(
    bucket_name=SETTINGS.api_runs_bucket,
    prefix=SETTINGS.api_runs_prefix,
)

JOB_CACHE: Dict[str, Dict[str, Any]] = {}
JOB_CACHE_LOCK = threading.Lock()
PIPELINE_RUN_LOCK = threading.Lock()
LOGGER = logging.getLogger(__name__)
UPLOAD_SESSION_PREFIX = "_upload_sessions"


app = FastAPI(
    title="Automated Subjective Grader API",
    version="2.0.0",
    description="FastAPI backend for the product-grade answer sheet evaluation website.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS.allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_pipeline_service():
    from pipeline_service import PipelineServiceConfig, run_pipeline

    return PipelineServiceConfig, run_pipeline


def _save_upload_file(upload: UploadFile, target_path: Path) -> Path:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("wb") as f:
        shutil.copyfileobj(upload.file, f)
    return target_path


def _summary_rows(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ordered = sorted(results, key=lambda row: row["percentage"], reverse=True)
    rows: List[Dict[str, Any]] = []
    for rank, row in enumerate(ordered, start=1):
        rows.append(
            {
                "rank": rank,
                "student": row["student_base"],
                "total_score": round(row["total_score"], 2),
                "max_score": round(row["max_total"], 2),
                "percentage": round(row["percentage"], 2),
            }
        )
    return rows


def _run_root(run_id: str) -> Path:
    return API_RUNS_ROOT / run_id


def _run_meta_path(run_id: str) -> Path:
    return _run_root(run_id) / "run_meta.json"


def _write_json_atomic(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")
    with temp_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    temp_path.replace(path)


def _upload_session_root(session_id: str) -> Path:
    return API_RUNS_ROOT / UPLOAD_SESSION_PREFIX / session_id


def _upload_session_meta_path(session_id: str) -> Path:
    return _upload_session_root(session_id) / "session_meta.json"


def _create_upload_session_meta(session_id: str) -> Dict[str, Any]:
    created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    meta = {
        "session_id": session_id,
        "created_at": created_at,
        "ideal_pdf": None,
        "rubric_json": None,
        "student_pdfs": [],
    }
    _persist_upload_session_meta(session_id, meta)
    return meta


def _persist_upload_session_meta(session_id: str, meta: Dict[str, Any]) -> None:
    _write_json_atomic(_upload_session_meta_path(session_id), meta)
    if RUN_ARTIFACT_STORE.enabled:
        RUN_ARTIFACT_STORE.save_json_blob(meta, UPLOAD_SESSION_PREFIX, session_id, "session_meta.json")


def _load_upload_session_meta(session_id: str) -> Dict[str, Any]:
    meta_path = _upload_session_meta_path(session_id)
    if meta_path.exists():
        with meta_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    if RUN_ARTIFACT_STORE.enabled:
        meta = RUN_ARTIFACT_STORE.load_json_blob(UPLOAD_SESSION_PREFIX, session_id, "session_meta.json")
        if meta is not None:
            _write_json_atomic(meta_path, meta)
            return meta

    raise HTTPException(status_code=404, detail="Upload session not found.")


def _store_upload_session_file(session_id: str, kind: str, upload: UploadFile) -> Dict[str, str]:
    original_name = Path(upload.filename or f"{kind}.bin").name
    stored_name = f"{kind}-{uuid.uuid4().hex[:8]}-{original_name}"
    content_type = upload.content_type or "application/octet-stream"
    file_bytes = upload.file.read()

    session_file_path = _upload_session_root(session_id) / "files" / stored_name
    session_file_path.parent.mkdir(parents=True, exist_ok=True)
    session_file_path.write_bytes(file_bytes)

    if RUN_ARTIFACT_STORE.enabled:
        blob_name = RUN_ARTIFACT_STORE.upload_bytes(
            file_bytes,
            UPLOAD_SESSION_PREFIX,
            session_id,
            "files",
            stored_name,
            content_type=content_type,
        )
        if not blob_name:
            raise HTTPException(
                status_code=500,
                detail="Unable to store the uploaded file in durable session storage.",
            )

    return {
        "kind": kind,
        "original_name": original_name,
        "stored_name": stored_name,
        "content_type": content_type,
        "uploaded_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


def _materialize_upload_session_file(session_id: str, file_ref: Dict[str, str], destination: Path) -> Path:
    source_path = _upload_session_root(session_id) / "files" / file_ref["stored_name"]
    if source_path.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination)
        return destination

    if RUN_ARTIFACT_STORE.enabled:
        downloaded = RUN_ARTIFACT_STORE.download_blob_to_file(
            destination,
            UPLOAD_SESSION_PREFIX,
            session_id,
            "files",
            file_ref["stored_name"],
        )
        if downloaded:
            return destination

    raise HTTPException(status_code=404, detail=f"Session file {file_ref['original_name']} is missing.")


def _load_run_meta(run_id: str) -> Dict[str, Any]:
    if run_id in JOB_CACHE:
        return JOB_CACHE[run_id]

    meta_path = _run_meta_path(run_id)
    if meta_path.exists():
        with meta_path.open("r", encoding="utf-8") as f:
            meta = json.load(f)
        with JOB_CACHE_LOCK:
            JOB_CACHE[run_id] = meta
        return meta

    meta = RUN_ARTIFACT_STORE.load_run_meta(run_id)
    if meta is not None:
        _write_json_atomic(meta_path, meta)
        with JOB_CACHE_LOCK:
            JOB_CACHE[run_id] = meta
        return meta

    raise HTTPException(status_code=404, detail="Run not found.")


def _persist_job_meta(run_id: str, meta: Dict[str, Any], sync_remote: bool = False) -> None:
    with JOB_CACHE_LOCK:
        JOB_CACHE[run_id] = meta
    _write_json_atomic(_run_meta_path(run_id), meta)
    if sync_remote or RUN_ARTIFACT_STORE.enabled:
        RUN_ARTIFACT_STORE.save_run_meta(run_id, meta)


def _sync_remote_reports(run_id: str, report_dir_value: Optional[str]) -> None:
    if not report_dir_value or not RUN_ARTIFACT_STORE.enabled:
        return
    RUN_ARTIFACT_STORE.upload_reports(run_id, Path(report_dir_value))


def _append_event(meta: Dict[str, Any], message: str) -> None:
    events = list(meta.get("events", []))
    events.append(
        {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "message": message,
        }
    )
    meta["events"] = events[-50:]


def _update_job(run_id: str, **changes: Any) -> Dict[str, Any]:
    meta = _load_run_meta(run_id).copy()
    for key, value in changes.items():
        meta[key] = value
    _persist_job_meta(run_id, meta)
    return meta


def _validate_inputs(
    engine: str,
    ocr_backend: str,
    azure_endpoint: Optional[str],
    azure_key: Optional[str],
) -> Tuple[str, str]:
    engine = engine.upper()
    if engine not in {"SBERT", "LLM"}:
        raise HTTPException(status_code=400, detail="Engine must be SBERT or LLM.")

    ocr_backend = ocr_backend.lower()
    if ocr_backend not in {"easyocr", "azure", "google_vision"}:
        raise HTTPException(
            status_code=400,
            detail="OCR backend must be easyocr, google_vision, or azure.",
        )

    has_server_managed_azure = bool(SETTINGS.azure_endpoint and SETTINGS.azure_key)
    if ocr_backend == "azure" and (not azure_endpoint or not azure_key) and not has_server_managed_azure:
        raise HTTPException(
            status_code=400,
            detail="Azure handwritten OCR requires both azure_endpoint and azure_key.",
        )
    return engine, ocr_backend


def _coerce_hosted_ocr_backend(
    ocr_backend: str,
    azure_endpoint: Optional[str],
    azure_key: Optional[str],
) -> Tuple[str, Optional[str]]:
    is_cloud_run = bool(os.getenv("K_SERVICE"))

    if is_cloud_run and ocr_backend == "easyocr":
        return (
            "google_vision",
            "EasyOCR was requested on the hosted backend, so the run was switched to Google Vision AI for production stability.",
        )

    return ocr_backend, None


def _prepare_run_inputs_from_upload_session(
    session_id: str,
    engine: str,
    ocr_backend: str,
    azure_endpoint: Optional[str],
    azure_key: Optional[str],
) -> Tuple[
    str,
    Dict[str, Any],
    str,
    List[str],
    PipelineServiceConfig,
    Dict[str, str],
    Dict[str, Any],
]:
    PipelineServiceConfig, _ = _load_pipeline_service()
    engine, ocr_backend = _validate_inputs(engine, ocr_backend, azure_endpoint, azure_key)
    ocr_backend, hosted_override_message = _coerce_hosted_ocr_backend(
        ocr_backend,
        azure_endpoint,
        azure_key,
    )

    session_meta = _load_upload_session_meta(session_id)
    ideal_ref = session_meta.get("ideal_pdf")
    rubric_ref = session_meta.get("rubric_json")
    student_refs = session_meta.get("student_pdfs", [])

    if not ideal_ref or not rubric_ref or not student_refs:
        raise HTTPException(
            status_code=400,
            detail="Upload session is incomplete. Upload the ideal PDF, rubric JSON, and at least one student PDF before starting the job.",
        )

    run_id = session_id
    run_root = _run_root(run_id)
    ideal_dir = run_root / "uploads" / "ideal"
    students_dir = run_root / "uploads" / "students"
    rubric_dir = run_root / "uploads" / "rubric"
    outputs_dir = run_root / "outputs"

    ideal_pdf_path = _materialize_upload_session_file(
        session_id,
        ideal_ref,
        ideal_dir / ideal_ref["original_name"],
    )

    rubric_path = _materialize_upload_session_file(
        session_id,
        rubric_ref,
        rubric_dir / rubric_ref["original_name"],
    )
    try:
        with rubric_path.open("r", encoding="utf-8") as rubric_file:
            rubric_dict = json.load(rubric_file)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid rubric JSON: {exc}") from exc

    _write_json_atomic(run_root / "rubric.json", rubric_dict)

    student_paths = [
        str(
            _materialize_upload_session_file(
                session_id,
                student_ref,
                students_dir / student_ref["original_name"],
            )
        )
        for student_ref in student_refs
    ]

    service_config = PipelineServiceConfig(
        poppler_path=POPPLER_BIN,
        dpi=300,
        use_gpu=SETTINGS.easyocr_use_gpu,
        languages=["en"],
        google_vision_language_hints=SETTINGS.google_vision_language_hints,
        rubric_path=str(run_root / "rubric.json"),
        ocr_root=str(outputs_dir / "ocr"),
        diagram_root=str(outputs_dir / "diagrams"),
        formula_root=str(outputs_dir / "formulas"),
        formula_crop_root=str(outputs_dir / "formula_crops"),
        eval_sbert_root=str(outputs_dir / "eval"),
        report_sbert_root=str(outputs_dir / "reports"),
        eval_llm_root=str(outputs_dir / "eval_llm"),
        report_llm_root=str(outputs_dir / "reports_llm"),
    )

    azure_settings = {
        "endpoint": azure_endpoint or SETTINGS.azure_endpoint or "",
        "key": azure_key or SETTINGS.azure_key or "",
    }
    return (
        run_id,
        rubric_dict,
        str(ideal_pdf_path),
        student_paths,
        service_config,
        azure_settings,
        {
            "engine": engine,
            "ocr_backend": ocr_backend,
            "hosted_override_message": hosted_override_message,
        },
    )


def _prepare_run_inputs(
    ideal_pdf: UploadFile,
    rubric_json: UploadFile,
    student_pdfs: List[UploadFile],
    engine: str,
    ocr_backend: str,
    azure_endpoint: Optional[str],
    azure_key: Optional[str],
) -> Tuple[
    str,
    Dict[str, Any],
    str,
    List[str],
    PipelineServiceConfig,
    Dict[str, str],
    Dict[str, Any],
]:
    PipelineServiceConfig, _ = _load_pipeline_service()
    engine, ocr_backend = _validate_inputs(engine, ocr_backend, azure_endpoint, azure_key)
    ocr_backend, hosted_override_message = _coerce_hosted_ocr_backend(
        ocr_backend,
        azure_endpoint,
        azure_key,
    )

    try:
        rubric_dict = json.load(rubric_json.file)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid rubric JSON: {exc}") from exc

    run_id = datetime.now().strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:8]
    run_root = _run_root(run_id)
    ideal_dir = run_root / "uploads" / "ideal"
    students_dir = run_root / "uploads" / "students"
    outputs_dir = run_root / "outputs"

    ideal_pdf_path = _save_upload_file(ideal_pdf, ideal_dir / ideal_pdf.filename)
    student_paths = [
        str(_save_upload_file(student_pdf, students_dir / student_pdf.filename))
        for student_pdf in student_pdfs
    ]

    service_config = PipelineServiceConfig(
        poppler_path=POPPLER_BIN,
        dpi=300,
        use_gpu=SETTINGS.easyocr_use_gpu,
        languages=["en"],
        google_vision_language_hints=SETTINGS.google_vision_language_hints,
        rubric_path=str(run_root / "rubric.json"),
        ocr_root=str(outputs_dir / "ocr"),
        diagram_root=str(outputs_dir / "diagrams"),
        formula_root=str(outputs_dir / "formulas"),
        formula_crop_root=str(outputs_dir / "formula_crops"),
        eval_sbert_root=str(outputs_dir / "eval"),
        report_sbert_root=str(outputs_dir / "reports"),
        eval_llm_root=str(outputs_dir / "eval_llm"),
        report_llm_root=str(outputs_dir / "reports_llm"),
    )

    azure_settings = {
        "endpoint": azure_endpoint or SETTINGS.azure_endpoint or "",
        "key": azure_key or SETTINGS.azure_key or "",
    }
    return (
        run_id,
        rubric_dict,
        str(ideal_pdf_path),
        student_paths,
        service_config,
        azure_settings,
        {
            "engine": engine,
            "ocr_backend": ocr_backend,
            "hosted_override_message": hosted_override_message,
        },
    )


def _build_reports(run_id: str, rows: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return [
        {
            "student": row["student"],
            "download_url": f"/api/runs/{run_id}/reports/{row['student']}_report.pdf",
        }
        for row in rows
    ]


def _create_initial_meta(
    run_id: str,
    engine: str,
    ocr_backend: str,
    student_count: int,
) -> Dict[str, Any]:
    created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    meta = {
        "run_id": run_id,
        "status": "queued",
        "engine": engine,
        "ocr_backend": ocr_backend,
        "student_count": student_count,
        "created_at": created_at,
        "started_at": None,
        "completed_at": None,
        "current_step": 0,
        "total_steps": 0,
        "progress_percent": 0,
        "message": "Queued. Waiting for execution slot.",
        "events": [
            {
                "timestamp": created_at,
                "message": "Job created and queued for execution.",
            }
        ],
        "elapsed_seconds": None,
        "eval_dir": None,
        "report_dir": None,
        "summary_rows": [],
        "reports": [],
        "results": [],
        "error": None,
    }
    _persist_job_meta(run_id, meta)
    return meta


def _job_progress_callback(run_id: str):
    def callback(current_step: int, total_steps: int, message: str) -> None:
        meta = _load_run_meta(run_id).copy()
        meta["current_step"] = current_step
        meta["total_steps"] = total_steps
        meta["progress_percent"] = int((current_step / max(total_steps, 1)) * 100)
        meta["message"] = message
        _append_event(meta, message)
        _persist_job_meta(run_id, meta)

    return callback


def _execute_job(
    run_id: str,
    rubric_dict: Dict[str, Any],
    ideal_pdf_path: str,
    student_paths: List[str],
    service_config: PipelineServiceConfig,
    engine: str,
    ocr_backend: str,
    azure_settings: Dict[str, str],
) -> None:
    with PIPELINE_RUN_LOCK:
        meta = _load_run_meta(run_id).copy()
        meta["status"] = "running"
        meta["started_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        meta["message"] = "Pipeline is now running."
        _append_event(meta, "Execution started.")
        _persist_job_meta(run_id, meta)

        try:
            _, run_pipeline = _load_pipeline_service()
            results, eval_dir, report_dir, elapsed = run_pipeline(
                ideal_pdf_path=ideal_pdf_path,
                student_pdf_paths=student_paths,
                rubric_dict=rubric_dict,
                engine=engine,
                ocr_backend=ocr_backend,
                config=service_config,
                azure_settings=azure_settings,
                progress_callback=_job_progress_callback(run_id),
            )

            rows = _summary_rows(results)
            meta = _load_run_meta(run_id).copy()
            meta.update(
                {
                    "status": "completed",
                    "completed_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                    "elapsed_seconds": elapsed,
                    "eval_dir": eval_dir,
                    "report_dir": report_dir,
                    "summary_rows": rows,
                    "reports": _build_reports(run_id, rows),
                    "results": results,
                    "message": "Evaluation completed successfully.",
                    "current_step": meta.get("total_steps", 0),
                    "progress_percent": 100,
                    "error": None,
                }
            )
            _append_event(meta, "Evaluation completed successfully.")
            _sync_remote_reports(run_id, meta.get("report_dir"))
            _persist_job_meta(run_id, meta, sync_remote=True)

        except Exception as exc:
            meta = _load_run_meta(run_id).copy()
            meta.update(
                {
                    "status": "failed",
                    "completed_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                    "message": "Evaluation failed.",
                    "error": str(exc),
                }
            )
            _append_event(meta, f"Evaluation failed: {exc}")
            _persist_job_meta(run_id, meta, sync_remote=True)


def _list_run_summaries() -> List[Dict[str, Any]]:
    API_RUNS_ROOT.mkdir(parents=True, exist_ok=True)
    runs_by_id: Dict[str, Dict[str, Any]] = {}
    for meta in RUN_ARTIFACT_STORE.list_run_metas():
        run_id = meta.get("run_id")
        if run_id:
            runs_by_id[run_id] = meta

    runs: List[Dict[str, Any]] = []
    for meta_file in API_RUNS_ROOT.glob("*/run_meta.json"):
        try:
            with meta_file.open("r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            continue
        run_id = meta.get("run_id")
        if run_id:
            runs_by_id[run_id] = meta

    for meta in runs_by_id.values():
        rows = meta.get("summary_rows", [])
        top_student = rows[0]["student"] if rows else None
        top_percentage = rows[0]["percentage"] if rows else None
        runs.append(
            {
                "run_id": meta.get("run_id"),
                "status": meta.get("status"),
                "engine": meta.get("engine"),
                "ocr_backend": meta.get("ocr_backend"),
                "student_count": meta.get("student_count", 0),
                "created_at": meta.get("created_at"),
                "completed_at": meta.get("completed_at"),
                "elapsed_seconds": meta.get("elapsed_seconds"),
                "progress_percent": meta.get("progress_percent", 0),
                "message": meta.get("message"),
                "top_student": top_student,
                "top_percentage": top_percentage,
            }
        )

    runs.sort(key=lambda item: item.get("created_at") or "", reverse=True)
    return runs


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root_health() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "auto-subjective-grader-api",
    }


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/team")
def get_team() -> List[Dict[str, str]]:
    return TEAM_MEMBERS


@app.get("/api/resources")
def get_resources() -> List[Dict[str, str]]:
    return RESOURCE_ITEMS


@app.get("/api/documentation")
def get_documentation() -> Dict[str, str]:
    if README_PATH.exists():
        content = README_PATH.read_text(encoding="utf-8")
    else:
        content = "# Documentation\n\nREADME.md not found."
    return {"content": content}


@app.get("/api/runtime-config")
def get_runtime_config() -> Dict[str, Any]:
    return {
        "azure_configured": bool(SETTINGS.azure_endpoint and SETTINGS.azure_key),
        "google_vision_supported": True,
        "gemini_configured": SETTINGS.gemini_configured,
        "durable_run_storage": RUN_ARTIFACT_STORE.enabled,
        "allowed_origins": SETTINGS.allowed_origins,
    }


@app.get("/api/research-paper")
def research_paper() -> Dict[str, Any]:
    return {
        "available": False,
        "message": "Research paper upload/serving will be connected here later.",
    }


@app.get("/api/jobs")
def list_jobs() -> List[Dict[str, Any]]:
    return _list_run_summaries()


@app.get("/api/jobs/{run_id}")
def get_job(run_id: str) -> Dict[str, Any]:
    return _load_run_meta(run_id)


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> Dict[str, Any]:
    return _load_run_meta(run_id)


@app.get("/api/runs/{run_id}/reports/{report_name}")
def download_report(run_id: str, report_name: str):
    if Path(report_name).name != report_name:
        raise HTTPException(status_code=400, detail="Invalid report name.")

    meta = _load_run_meta(run_id)
    report_dir_value = meta.get("report_dir")
    if not report_dir_value:
        raise HTTPException(status_code=404, detail="Report directory not available yet.")

    report_dir = Path(report_dir_value)
    target = (report_dir / report_name).resolve()
    if not str(target).startswith(str(report_dir.resolve())) or not target.exists():
        remote_report = RUN_ARTIFACT_STORE.load_report_bytes(run_id, report_name)
        if remote_report is None:
            raise HTTPException(status_code=404, detail="Report not found.")
        return Response(
            content=remote_report,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{report_name}"'},
        )
    return FileResponse(path=target, filename=target.name, media_type="application/pdf")


@app.post("/api/jobs")
def create_job(
    ideal_pdf: UploadFile = File(...),
    rubric_json: UploadFile = File(...),
    student_pdfs: List[UploadFile] = File(...),
    engine: str = Form("SBERT"),
    ocr_backend: str = Form("easyocr"),
    azure_endpoint: Optional[str] = Form(None),
    azure_key: Optional[str] = Form(None),
) -> Dict[str, Any]:
    (
        run_id,
        rubric_dict,
        ideal_pdf_path,
        student_paths,
        service_config,
        azure_settings,
        execution_settings,
    ) = _prepare_run_inputs(
        ideal_pdf=ideal_pdf,
        rubric_json=rubric_json,
        student_pdfs=student_pdfs,
        engine=engine,
        ocr_backend=ocr_backend,
        azure_endpoint=azure_endpoint,
        azure_key=azure_key,
    )

    meta = _create_initial_meta(
        run_id,
        execution_settings["engine"],
        execution_settings["ocr_backend"],
        len(student_paths),
    )
    if execution_settings["hosted_override_message"]:
        meta["message"] = execution_settings["hosted_override_message"]
        _append_event(meta, execution_settings["hosted_override_message"])
        _persist_job_meta(run_id, meta)

    worker = threading.Thread(
        target=_execute_job,
        args=(
            run_id,
            rubric_dict,
            ideal_pdf_path,
            student_paths,
            service_config,
            execution_settings["engine"],
            execution_settings["ocr_backend"],
            azure_settings,
        ),
        daemon=True,
    )
    worker.start()
    return meta


@app.post("/api/upload-sessions")
def create_upload_session() -> Dict[str, str]:
    session_id = datetime.now().strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:8]
    _create_upload_session_meta(session_id)
    return {"session_id": session_id}


@app.post("/api/upload-sessions/{session_id}/files")
def upload_session_file(
    session_id: str,
    kind: str = Form(...),
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    if kind not in {"ideal_pdf", "rubric_json", "student_pdf"}:
        raise HTTPException(status_code=400, detail="File kind must be ideal_pdf, rubric_json, or student_pdf.")

    session_meta = _load_upload_session_meta(session_id)
    file_ref = _store_upload_session_file(session_id, kind, file)

    if kind == "student_pdf":
        session_meta["student_pdfs"] = [*session_meta.get("student_pdfs", []), file_ref]
    else:
        session_meta[kind] = file_ref

    _persist_upload_session_meta(session_id, session_meta)
    return {
        "session_id": session_id,
        "kind": kind,
        "file": file_ref,
        "student_count": len(session_meta.get("student_pdfs", [])),
    }


@app.post("/api/upload-sessions/{session_id}/jobs")
def create_job_from_upload_session(
    session_id: str,
    engine: str = Form("SBERT"),
    ocr_backend: str = Form("easyocr"),
    azure_endpoint: Optional[str] = Form(None),
    azure_key: Optional[str] = Form(None),
) -> Dict[str, Any]:
    (
        run_id,
        rubric_dict,
        ideal_pdf_path,
        student_paths,
        service_config,
        azure_settings,
        execution_settings,
    ) = _prepare_run_inputs_from_upload_session(
        session_id=session_id,
        engine=engine,
        ocr_backend=ocr_backend,
        azure_endpoint=azure_endpoint,
        azure_key=azure_key,
    )

    meta = _create_initial_meta(
        run_id,
        execution_settings["engine"],
        execution_settings["ocr_backend"],
        len(student_paths),
    )
    if execution_settings["hosted_override_message"]:
        meta["message"] = execution_settings["hosted_override_message"]
        _append_event(meta, execution_settings["hosted_override_message"])
        _persist_job_meta(run_id, meta)

    worker = threading.Thread(
        target=_execute_job,
        args=(
            run_id,
            rubric_dict,
            ideal_pdf_path,
            student_paths,
            service_config,
            execution_settings["engine"],
            execution_settings["ocr_backend"],
            azure_settings,
        ),
        daemon=True,
    )
    worker.start()
    return meta


@app.post("/api/evaluate")
def evaluate_sync(
    ideal_pdf: UploadFile = File(...),
    rubric_json: UploadFile = File(...),
    student_pdfs: List[UploadFile] = File(...),
    engine: str = Form("SBERT"),
    ocr_backend: str = Form("easyocr"),
    azure_endpoint: Optional[str] = Form(None),
    azure_key: Optional[str] = Form(None),
) -> Dict[str, Any]:
    (
        run_id,
        rubric_dict,
        ideal_pdf_path,
        student_paths,
        service_config,
        azure_settings,
        execution_settings,
    ) = _prepare_run_inputs(
        ideal_pdf=ideal_pdf,
        rubric_json=rubric_json,
        student_pdfs=student_pdfs,
        engine=engine,
        ocr_backend=ocr_backend,
        azure_endpoint=azure_endpoint,
        azure_key=azure_key,
    )

    rows_meta = _create_initial_meta(
        run_id,
        execution_settings["engine"],
        execution_settings["ocr_backend"],
        len(student_paths),
    )
    rows_meta["status"] = "running"
    rows_meta["started_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    rows_meta["message"] = "Synchronous evaluation started."
    _append_event(rows_meta, "Synchronous evaluation started.")
    if execution_settings["hosted_override_message"]:
        rows_meta["message"] = execution_settings["hosted_override_message"]
        _append_event(rows_meta, execution_settings["hosted_override_message"])
    _persist_job_meta(run_id, rows_meta)

    _, run_pipeline = _load_pipeline_service()
    results, eval_dir, report_dir, elapsed = run_pipeline(
        ideal_pdf_path=ideal_pdf_path,
        student_pdf_paths=student_paths,
        rubric_dict=rubric_dict,
        engine=execution_settings["engine"],
        ocr_backend=execution_settings["ocr_backend"],
        config=service_config,
        azure_settings=azure_settings,
        progress_callback=_job_progress_callback(run_id),
    )

    rows = _summary_rows(results)
    meta = _load_run_meta(run_id).copy()
    meta.update(
        {
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "elapsed_seconds": elapsed,
            "eval_dir": eval_dir,
            "report_dir": report_dir,
            "summary_rows": rows,
            "reports": _build_reports(run_id, rows),
            "results": results,
            "message": "Synchronous evaluation completed successfully.",
            "progress_percent": 100,
            "error": None,
        }
    )
    _append_event(meta, "Synchronous evaluation completed successfully.")
    _sync_remote_reports(run_id, meta.get("report_dir"))
    _persist_job_meta(run_id, meta, sync_remote=True)

    return meta
