import json
import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import diagram_extractor
import evaluation_core
import formula_pipeline
import llm_evaluator
import ocr_pipeline
import report_generator


ProgressCallback = Callable[[int, int, str], None]


@dataclass
class PipelineServiceConfig:
    poppler_path: Optional[str] = None
    dpi: int = 300
    use_gpu: bool = True
    languages: List[str] = None
    rubric_path: str = "rubric.json"
    ocr_root: str = "results/ocr"
    diagram_root: str = "results/diagrams"
    formula_root: str = "results/formulas"
    formula_crop_root: str = "results/formula_crops"
    eval_sbert_root: str = "results/eval"
    report_sbert_root: str = "results/reports"
    eval_llm_root: str = "results/eval_llm"
    report_llm_root: str = "results/reports_llm"


def _notify(
    callback: Optional[ProgressCallback],
    current_step: int,
    total_steps: int,
    message: str,
) -> None:
    if callback is not None:
        callback(current_step, total_steps, message)


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
    formula_cfg = formula_pipeline.FormulaConfig(
        dpi=config.dpi,
        poppler_path=config.poppler_path,
        ocr_root=config.ocr_root,
        output_root=config.formula_root,
        crop_root=config.formula_crop_root,
    )

    ocr_pipeline.ensure_dir(config.ocr_root)
    os.makedirs(config.diagram_root, exist_ok=True)
    os.makedirs(config.formula_root, exist_ok=True)
    os.makedirs(config.formula_crop_root, exist_ok=True)

    if engine == "SBERT":
        eval_cfg = evaluation_core.EvalConfig(
            ocr_root=config.ocr_root,
            diagram_root=config.diagram_root,
            formula_root=config.formula_root,
            rubric_path=config.rubric_path,
        )
        report_cfg = report_generator.ReportConfig(
            eval_root=config.eval_sbert_root,
            report_root=config.report_sbert_root,
        )
        evaluator = evaluation_core.Evaluator(eval_cfg)
        eval_dir = config.eval_sbert_root
        report_dir = config.report_sbert_root
    else:
        llm_cfg = llm_evaluator.LlmEvalConfig(
            ocr_root=config.ocr_root,
            diagram_root=config.diagram_root,
            rubric_path=config.rubric_path,
        )
        report_cfg = report_generator.ReportConfig(
            eval_root=config.eval_llm_root,
            report_root=config.report_llm_root,
        )
        evaluator = llm_evaluator.LlmEvaluator(llm_cfg)
        eval_dir = config.eval_llm_root
        report_dir = config.report_llm_root

    os.makedirs(eval_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)

    reader = None
    formula_reader = None
    if ocr_backend == "easyocr":
        reader = ocr_pipeline.build_easyocr_reader(ocr_cfg)
        ocr_label = "EasyOCR"
    else:
        ocr_label = "Azure Document Intelligence"

    if engine == "SBERT":
        formula_reader = formula_pipeline.build_formula_reader()

    num_students = len(student_pdf_paths)
    total_steps = (3 + 5 * num_students) if engine == "SBERT" else (2 + 4 * num_students)
    current_step = 0

    _notify(progress_callback, current_step, total_steps, f"Running OCR on ideal answer sheet with {ocr_label}...")
    ocr_pipeline.ocr_pdf(ideal_pdf_path, ocr_cfg, reader)
    current_step += 1

    for spdf in student_pdf_paths:
        _notify(progress_callback, current_step, total_steps, f"Running OCR on {os.path.basename(spdf)} with {ocr_label}...")
        ocr_pipeline.ocr_pdf(spdf, ocr_cfg, reader)
        current_step += 1

    if engine == "SBERT":
        _notify(progress_callback, current_step, total_steps, "Extracting formulas for ideal answer sheet...")
        formula_pipeline.extract_formulas_for_pdf(
            ideal_pdf_path,
            formula_cfg,
            formula_reader,
        )
        current_step += 1

        for spdf in student_pdf_paths:
            _notify(progress_callback, current_step, total_steps, f"Extracting formulas for {os.path.basename(spdf)}...")
            formula_pipeline.extract_formulas_for_pdf(
                spdf,
                formula_cfg,
                formula_reader,
            )
            current_step += 1

    _notify(progress_callback, current_step, total_steps, "Extracting diagrams for ideal answer sheet...")
    diagram_extractor.extract_diagrams_for_pdf(ideal_pdf_path, diagram_cfg)
    current_step += 1

    for spdf in student_pdf_paths:
        _notify(progress_callback, current_step, total_steps, f"Extracting diagrams for {os.path.basename(spdf)}...")
        diagram_extractor.extract_diagrams_for_pdf(spdf, diagram_cfg)
        current_step += 1

    all_results: List[Dict[str, Any]] = []
    for spdf in student_pdf_paths:
        student_name = os.path.splitext(os.path.basename(spdf))[0]
        engine_prefix = "[SBERT]" if engine == "SBERT" else "[Gemini LLM]"
        _notify(progress_callback, current_step, total_steps, f"{engine_prefix} Evaluating {student_name}...")

        result = evaluator.evaluate_student(ideal_pdf_path, spdf)
        all_results.append(result)
        current_step += 1
        _notify(progress_callback, current_step, total_steps, f"Generating report for {student_name}...")

        json_path = os.path.join(eval_dir, f"{result['student_base']}_eval.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        report_generator.generate_pdf_from_result(result, report_cfg)
        current_step += 1

    _notify(progress_callback, total_steps, total_steps, "All evaluations complete.")

    elapsed = time.perf_counter() - started_at
    return all_results, eval_dir, report_dir, elapsed
