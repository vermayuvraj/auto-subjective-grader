from __future__ import annotations

import json
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
from fastapi.responses import FileResponse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.append(str(SRC_ROOT))

from backend_api.content import RESOURCE_ITEMS, TEAM_MEMBERS
from backend_api.settings import load_settings

if TYPE_CHECKING:
    from pipeline_service import PipelineServiceConfig


SETTINGS = load_settings(PROJECT_ROOT)
POPPLER_BIN = SETTINGS.poppler_path
API_RUNS_ROOT = SETTINGS.api_runs_root
README_PATH = SETTINGS.readme_path

JOB_CACHE: Dict[str, Dict[str, Any]] = {}
JOB_CACHE_LOCK = threading.Lock()
PIPELINE_RUN_LOCK = threading.Lock()


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


def _load_run_meta(run_id: str) -> Dict[str, Any]:
    if run_id in JOB_CACHE:
        return JOB_CACHE[run_id]

    meta_path = _run_meta_path(run_id)
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Run not found.")

    with meta_path.open("r", encoding="utf-8") as f:
        meta = json.load(f)
    with JOB_CACHE_LOCK:
        JOB_CACHE[run_id] = meta
    return meta


def _persist_job_meta(run_id: str, meta: Dict[str, Any]) -> None:
    with JOB_CACHE_LOCK:
        JOB_CACHE[run_id] = meta
    _write_json_atomic(_run_meta_path(run_id), meta)


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
            _persist_job_meta(run_id, meta)

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
            _persist_job_meta(run_id, meta)


def _list_run_summaries() -> List[Dict[str, Any]]:
    API_RUNS_ROOT.mkdir(parents=True, exist_ok=True)
    runs: List[Dict[str, Any]] = []
    for meta_file in API_RUNS_ROOT.glob("*/run_meta.json"):
        try:
            with meta_file.open("r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            continue

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
        "gemini_configured": SETTINGS.gemini_api_key_present,
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
    meta = _load_run_meta(run_id)
    report_dir_value = meta.get("report_dir")
    if not report_dir_value:
        raise HTTPException(status_code=404, detail="Report directory not available yet.")

    report_dir = Path(report_dir_value)
    target = (report_dir / report_name).resolve()
    if not str(target).startswith(str(report_dir.resolve())) or not target.exists():
        raise HTTPException(status_code=404, detail="Report not found.")
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
    _persist_job_meta(run_id, meta)

    return meta
