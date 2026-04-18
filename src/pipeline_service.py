import json
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Optional, Tuple

if TYPE_CHECKING:
    import diagram_extractor
    import evaluation_core
    import formula_pipeline
    import llm_evaluator
    import ocr_pipeline
    import report_generator

ProgressCallback = Callable[[int, int, str], None]

_READER_CACHE_LOCK = threading.Lock()
_EASYOCR_READER_CACHE: Dict[Tuple[Tuple[str, ...], bool], Any] = {}
_FORMULA_READER: Any = None
_EVALUATOR_CACHE: Dict[Tuple[str, str, str, str, str], Any] = {}


@dataclass
class PipelineServiceConfig:
    poppler_path: Optional[str] = None
    dpi: int = 300
    use_gpu: bool = True
    languages: List[str] = None
    google_vision_language_hints: List[str] = None
    rubric_path: str = "rubric.json"
    ocr_root: str = "results/ocr"
    diagram_root: str = "results/diagrams"
    formula_root: str = "results/formulas"
    formula_crop_root: str = "results/formula_crops"
    eval_sbert_root: str = "results/eval"
    report_sbert_root: str = "results/reports"
    eval_llm_root: str = "results/eval_llm"
    report_llm_root: str = "results/reports_llm"
    ocr_workers: Optional[int] = None
    diagram_workers: Optional[int] = None
    formula_workers: Optional[int] = None
    sbert_eval_workers: Optional[int] = None
    llm_eval_workers: Optional[int] = None
    report_workers: Optional[int] = None
    enable_formula_autoskip: bool = True


class ProgressTracker:
    def __init__(self, total_steps: int, callback: Optional[ProgressCallback]) -> None:
        self.total_steps = max(total_steps, 1)
        self.current_step = 0
        self._callback = callback
        self._lock = threading.Lock()

    def emit(self, message: str) -> None:
        with self._lock:
            current_step = self.current_step
            total_steps = self.total_steps
        _notify(self._callback, current_step, total_steps, message)

    def set_total_steps(self, total_steps: int, message: Optional[str] = None) -> None:
        with self._lock:
            self.total_steps = max(total_steps, 1)
            current_step = self.current_step
        if message is not None:
            _notify(self._callback, current_step, self.total_steps, message)

    def advance(self, message: str, step_count: int = 1) -> None:
        with self._lock:
            self.current_step += step_count
            current_step = self.current_step
            total_steps = self.total_steps
        _notify(self._callback, current_step, total_steps, message)


def _notify(
    callback: Optional[ProgressCallback],
    current_step: int,
    total_steps: int,
    message: str,
) -> None:
    if callback is not None:
        callback(current_step, total_steps, message)


def _get_easyocr_reader(ocr_cfg: Any):
    import ocr_pipeline

    cache_key = (tuple(ocr_cfg.languages or ["en"]), bool(ocr_cfg.use_gpu))
    with _READER_CACHE_LOCK:
        if cache_key not in _EASYOCR_READER_CACHE:
            _EASYOCR_READER_CACHE[cache_key] = ocr_pipeline.build_easyocr_reader(ocr_cfg)
        return _EASYOCR_READER_CACHE[cache_key]


def _get_formula_reader():
    import formula_pipeline

    global _FORMULA_READER
    with _READER_CACHE_LOCK:
        if _FORMULA_READER is None:
            _FORMULA_READER = formula_pipeline.build_formula_reader()
        return _FORMULA_READER


def _rubric_signature(rubric_dict: Dict[str, Any]) -> str:
    return json.dumps(rubric_dict, ensure_ascii=False, sort_keys=True)


def _get_evaluator(
    engine: str,
    rubric_signature: str,
    eval_dir: str,
    config: PipelineServiceConfig,
):
    if engine == "SBERT":
        import evaluation_core

        cache_key = (
            "SBERT",
            rubric_signature,
            config.ocr_root,
            config.diagram_root,
            config.formula_root,
        )
        with _READER_CACHE_LOCK:
            if cache_key not in _EVALUATOR_CACHE:
                eval_cfg = evaluation_core.EvalConfig(
                    ocr_root=config.ocr_root,
                    diagram_root=config.diagram_root,
                    formula_root=config.formula_root,
                    rubric_path=config.rubric_path,
                )
                _EVALUATOR_CACHE[cache_key] = evaluation_core.Evaluator(eval_cfg)
            return _EVALUATOR_CACHE[cache_key]

    import llm_evaluator

    cache_key = (
        "LLM",
        rubric_signature,
        config.ocr_root,
        config.diagram_root,
        config.formula_root,
    )
    with _READER_CACHE_LOCK:
        if cache_key not in _EVALUATOR_CACHE:
            llm_cfg = llm_evaluator.LlmEvalConfig(
                ocr_root=config.ocr_root,
                diagram_root=config.diagram_root,
                formula_root=config.formula_root,
                rubric_path=config.rubric_path,
            )
            _EVALUATOR_CACHE[cache_key] = llm_evaluator.LlmEvaluator(llm_cfg)
        return _EVALUATOR_CACHE[cache_key]


def _safe_worker_count(preferred: Optional[int], item_count: int, fallback: int) -> int:
    if item_count <= 0:
        return 0
    if preferred is not None:
        return max(1, min(preferred, item_count))
    return max(1, min(fallback, item_count))


def _run_stage_parallel(
    items: Iterable[Any],
    worker_count: int,
    fn: Callable[[Any], Any],
    on_done: Callable[[Any, Any], None],
) -> None:
    item_list = list(items)
    if not item_list:
        return

    if worker_count <= 1:
        for item in item_list:
            result = fn(item)
            on_done(item, result)
        return

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = {executor.submit(fn, item): item for item in item_list}
        for future in as_completed(futures):
            item = futures[future]
            result = future.result()
            on_done(item, result)


def _base_name(pdf_path: str) -> str:
    return os.path.splitext(os.path.basename(pdf_path))[0]


def _build_formula_plan(
    pdf_paths: List[str],
    formula_cfg: Any,
    rubric_dict: Dict[str, Any],
    enable_formula_autoskip: bool,
) -> Tuple[Dict[str, Any], int, str]:
    import formula_pipeline

    if not enable_formula_autoskip:
        return (
            {
                pdf_path: formula_pipeline.FormulaDetectionResult(
                    needs_formula=True,
                    candidate_pages=None,
                    reason="Formula auto-skip disabled; checking all pages.",
                    rubric_hint=True,
                )
                for pdf_path in pdf_paths
            },
            len(pdf_paths),
            "Formula parsing forced for all documents.",
        )

    plan: Dict[str, Any] = {}
    candidate_docs = 0
    explanations: List[str] = []

    for pdf_path in pdf_paths:
        result = formula_pipeline.detect_formula_pages_for_pdf(
            pdf_path,
            formula_cfg,
            rubric_dict=rubric_dict,
        )
        plan[pdf_path] = result
        if result.needs_formula:
            candidate_docs += 1
            explanations.append(f"{_base_name(pdf_path)}: {result.reason}")

    if candidate_docs == 0:
        return plan, 0, "Formula parsing not needed for this batch; continuing to diagram extraction."

    return (
        plan,
        candidate_docs,
        f"Formula parsing will run for {candidate_docs} document(s).",
    )


def run_pipeline(
    ideal_pdf_path: str,
    student_pdf_paths: List[str],
    rubric_dict: Dict[str, Any],
    engine: str,
    ocr_backend: str,
    config: PipelineServiceConfig,
    azure_settings: Optional[Dict[str, str]] = None,
    progress_callback: Optional[ProgressCallback] = None,
) -> Tuple[List[Dict[str, Any]], str, str, float]:
    import diagram_extractor
    import formula_pipeline
    import ocr_pipeline
    import report_generator

    started_at = time.perf_counter()
    azure_settings = azure_settings or {}
    languages = config.languages or ["en"]

    with open(config.rubric_path, "w", encoding="utf-8") as f:
        json.dump(rubric_dict, f, ensure_ascii=False, indent=2)

    ocr_cfg = ocr_pipeline.OCRConfig(
        dpi=config.dpi,
        poppler_path=config.poppler_path,
        languages=languages,
        use_gpu=config.use_gpu,
        output_root=config.ocr_root,
        backend=ocr_backend,
        google_vision_language_hints=config.google_vision_language_hints,
        azure_document_intelligence_endpoint=azure_settings.get("endpoint"),
        azure_document_intelligence_key=azure_settings.get("key"),
    )
    diagram_cfg = diagram_extractor.DiagramConfig(
        dpi=config.dpi,
        poppler_path=config.poppler_path,
        output_root=config.diagram_root,
        min_area_ratio=0.003,
        min_center_y_ratio=0.45,
    )

    ocr_pipeline.ensure_dir(config.ocr_root)
    os.makedirs(config.diagram_root, exist_ok=True)
    os.makedirs(config.formula_root, exist_ok=True)
    os.makedirs(config.formula_crop_root, exist_ok=True)

    formula_cfg = formula_pipeline.FormulaConfig(
        dpi=config.dpi,
        poppler_path=config.poppler_path,
        ocr_root=config.ocr_root,
        output_root=config.formula_root,
        crop_root=config.formula_crop_root,
    )

    rubric_signature = _rubric_signature(rubric_dict)

    if engine == "SBERT":
        report_cfg = report_generator.ReportConfig(
            eval_root=config.eval_sbert_root,
            report_root=config.report_sbert_root,
        )
        eval_dir = config.eval_sbert_root
        report_dir = config.report_sbert_root
    else:
        report_cfg = report_generator.ReportConfig(
            eval_root=config.eval_llm_root,
            report_root=config.report_llm_root,
        )
        eval_dir = config.eval_llm_root
        report_dir = config.report_llm_root

    evaluator = _get_evaluator(engine, rubric_signature, eval_dir, config)

    os.makedirs(eval_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)

    reader = None
    if ocr_backend == "easyocr":
        reader = _get_easyocr_reader(ocr_cfg)
        ocr_label = "EasyOCR"
    elif ocr_backend == "google_vision":
        ocr_label = "Google Vision AI"
    else:
        ocr_label = "Azure Document Intelligence"

    doc_paths = [ideal_pdf_path, *student_pdf_paths]
    num_students = len(student_pdf_paths)
    max_total_steps = (len(doc_paths) * 3) + (2 * num_students)
    tracker = ProgressTracker(max_total_steps, progress_callback)
    tracker.emit("Input validation complete. Preparing OCR, formula, diagram, and evaluation stages...")

    ocr_workers = _safe_worker_count(
        config.ocr_workers,
        len(doc_paths),
        1 if ocr_backend == "easyocr" and config.use_gpu else 4,
    )
    tracker.emit(f"Running OCR across {len(doc_paths)} document(s) with {ocr_label}...")

    def ocr_task(pdf_path: str) -> str:
        ocr_pipeline.ocr_pdf(pdf_path, ocr_cfg, reader)
        return pdf_path

    def on_ocr_done(pdf_path: str, _: Any) -> None:
        tracker.advance(f"Completed OCR for {_base_name(pdf_path)} with {ocr_label}.")

    _run_stage_parallel(doc_paths, ocr_workers, ocr_task, on_ocr_done)

    formula_plan, formula_doc_count, formula_message = _build_formula_plan(
        doc_paths,
        formula_cfg,
        rubric_dict,
        enable_formula_autoskip=config.enable_formula_autoskip,
    )
    adjusted_total_steps = (len(doc_paths) * 2) + formula_doc_count + (2 * num_students)
    tracker.set_total_steps(adjusted_total_steps, formula_message)

    formula_docs = [pdf_path for pdf_path in doc_paths if formula_plan[pdf_path].needs_formula]
    formula_workers = _safe_worker_count(
        config.formula_workers,
        len(formula_docs),
        1 if config.use_gpu else 2,
    )
    if formula_docs:
        formula_reader = _get_formula_reader()
        tracker.emit(f"Extracting formulas for {len(formula_docs)} document(s)...")

        def formula_task(pdf_path: str) -> Dict[int, str]:
            detection_result = formula_plan[pdf_path]
            return formula_pipeline.extract_formulas_for_pdf(
                pdf_path,
                formula_cfg,
                formula_reader,
                candidate_pages=detection_result.candidate_pages,
            )

        def on_formula_done(pdf_path: str, _: Any) -> None:
            tracker.advance(f"Completed formula parsing for {_base_name(pdf_path)}.")

        _run_stage_parallel(formula_docs, formula_workers, formula_task, on_formula_done)

    diagram_workers = _safe_worker_count(config.diagram_workers, len(doc_paths), 4)
    tracker.emit(f"Extracting diagrams across {len(doc_paths)} document(s)...")

    def diagram_task(pdf_path: str) -> Dict[int, Optional[str]]:
        return diagram_extractor.extract_diagrams_for_pdf(pdf_path, diagram_cfg)

    def on_diagram_done(pdf_path: str, _: Any) -> None:
        tracker.advance(f"Completed diagram extraction for {_base_name(pdf_path)}.")

    _run_stage_parallel(doc_paths, diagram_workers, diagram_task, on_diagram_done)

    if engine == "SBERT":
        evaluation_workers = _safe_worker_count(
            config.sbert_eval_workers,
            num_students,
            1 if config.use_gpu else 2,
        )
    else:
        evaluation_workers = _safe_worker_count(config.llm_eval_workers, num_students, 3)

    tracker.emit(f"Evaluating {num_students} student answer sheet(s) with {engine}...")
    result_map: Dict[str, Dict[str, Any]] = {}
    result_lock = threading.Lock()

    def evaluation_task(pdf_path: str) -> Dict[str, Any]:
        return evaluator.evaluate_student(ideal_pdf_path, pdf_path)

    def on_evaluation_done(pdf_path: str, result: Dict[str, Any]) -> None:
        with result_lock:
            result_map[pdf_path] = result
        engine_prefix = "[SBERT]" if engine == "SBERT" else "[Gemini Vertex AI]"
        tracker.advance(f"{engine_prefix} Evaluated {_base_name(pdf_path)}.")

    _run_stage_parallel(student_pdf_paths, evaluation_workers, evaluation_task, on_evaluation_done)

    all_results = [result_map[pdf_path] for pdf_path in student_pdf_paths]
    report_workers = _safe_worker_count(config.report_workers, len(all_results), 4)
    tracker.emit(f"Generating reports for {len(all_results)} student answer sheet(s)...")

    def report_task(result: Dict[str, Any]) -> str:
        json_path = os.path.join(eval_dir, f"{result['student_base']}_eval.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        report_generator.generate_pdf_from_result(result, report_cfg)
        return result["student_base"]

    def on_report_done(_: Dict[str, Any], student_name: str) -> None:
        tracker.advance(f"Generated JSON and PDF report for {student_name}.")

    _run_stage_parallel(all_results, report_workers, report_task, on_report_done)

    tracker.set_total_steps(max(tracker.total_steps, tracker.current_step))
    tracker.emit("All evaluations complete.")

    elapsed = time.perf_counter() - started_at
    return all_results, eval_dir, report_dir, elapsed
