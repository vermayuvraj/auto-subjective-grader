"""
Step 4: Report Generation (JSON -> PDF per student)

- Reads evaluation JSON files from results/eval/ (SBERT)
  or results/eval_llm/ (LLM), depending on how ReportConfig is used.
- Each JSON should look like the output from:
    - evaluation_core.Evaluator (SBERT) or
    - llm_evaluator.LlmEvaluator (LLM):

    {
      "student_base": "Student_A",
      "total_score": ...,
      "max_total": ...,
      "percentage": ...,
      "questions": [
        {
          "question_id": 1,
          "score": ...,
          "max_marks": ...,
          "text_similarity": ... or null,
          "diagram_similarity": ... or null,
          "feedback": "..."
        },
        ...
      ]
    }

- Generates one PDF report per student in results/reports/ or results/reports_llm/.

Also provides:
    - ReportConfig
    - generate_pdf_from_result(result, cfg)

which are used by the Streamlit app.
"""

import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional

from fpdf import FPDF


# ---------- Config ----------

@dataclass
class ReportConfig:
    eval_root: str = "results/eval"
    report_root: str = "results/reports"


UNICODE_FONT_FAMILY = "DejaVuSans"


def _find_font_path(font_name: str) -> Optional[str]:
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu") / font_name,
        Path("/usr/local/share/fonts") / font_name,
        Path("C:/Windows/Fonts") / font_name,
        Path("C:/ProgramData/anaconda3/Lib/site-packages/matplotlib/mpl-data/fonts/ttf") / font_name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def _register_unicode_fonts(pdf: FPDF) -> str:
    regular = _find_font_path("DejaVuSans.ttf")
    if not regular:
        return "Arial"

    bold = _find_font_path("DejaVuSans-Bold.ttf")
    italic = _find_font_path("DejaVuSans-Oblique.ttf")

    pdf.add_font(UNICODE_FONT_FAMILY, "", regular)
    pdf.add_font(UNICODE_FONT_FAMILY, "B", bold or regular)
    pdf.add_font(UNICODE_FONT_FAMILY, "I", italic or regular)
    return UNICODE_FONT_FAMILY


def _safe_text(value: Any, fallback_family: str) -> str:
    text = "" if value is None else str(value)
    if fallback_family != "Arial":
        return text
    return (
        text.encode("latin-1", errors="replace")
        .decode("latin-1")
        .replace("?", "-")
    )


# ---------- PDF helper ----------

class ReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.font_family_name = _register_unicode_fonts(self)

    def header(self):
        self.set_font(self.font_family_name, "B", 16)
        self.cell(0, 10, "Automated Answer Sheet Evaluation", ln=1, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_family_name, "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_pdf_from_result(result: Dict[str, Any], cfg: ReportConfig) -> str:
    """
    Given one evaluation result dict (from JSON or Evaluator),
    generate a PDF report and return its path.
    """
    os.makedirs(cfg.report_root, exist_ok=True)
    filename = f"{result['student_base']}_report.pdf"
    path = os.path.join(cfg.report_root, filename)

    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ----- Summary -----
    pdf.set_font(pdf.font_family_name, "", 12)
    pdf.cell(0, 8, _safe_text(f"Student: {result['student_base']}", pdf.font_family_name), ln=1)
    pdf.cell(
        0,
        8,
        _safe_text(f"Total Score: {result['total_score']:.2f} / {result['max_total']:.2f}", pdf.font_family_name),
        ln=1,
    )
    pdf.cell(0, 8, _safe_text(f"Percentage: {result['percentage']:.2f}%", pdf.font_family_name), ln=1)
    pdf.ln(4)

    # ----- Per-question detail -----
    for q in result["questions"]:
        pdf.set_font(pdf.font_family_name, "B", 12)
        pdf.cell(
            0,
            8,
            _safe_text(f"Q{q['question_id']}: {q['score']:.2f} / {q['max_marks']:.2f}", pdf.font_family_name),
            ln=1,
        )

        # ---- Safe similarity display ----
        pdf.set_font(pdf.font_family_name, "", 11)

        txt_sim = q.get("text_similarity", None)
        diag_sim = q.get("diagram_similarity", None)
        formula_sim = q.get("formula_similarity", None)

        # Text similarity
        if isinstance(txt_sim, (int, float)):
            pdf.cell(0, 6, _safe_text(f"Text similarity: {txt_sim:.3f}", pdf.font_family_name), ln=1)
        else:
            pdf.cell(0, 6, _safe_text("Text similarity: N/A (LLM evaluation)", pdf.font_family_name), ln=1)

        # Diagram similarity
        if isinstance(diag_sim, (int, float)):
            pdf.cell(0, 6, _safe_text(f"Diagram similarity: {diag_sim:.3f}", pdf.font_family_name), ln=1)
        else:
            pdf.cell(0, 6, _safe_text("Diagram similarity: N/A (LLM evaluation)", pdf.font_family_name), ln=1)

        # Formula similarity
        if isinstance(formula_sim, (int, float)):
            pdf.cell(0, 6, _safe_text(f"Formula similarity: {formula_sim:.3f}", pdf.font_family_name), ln=1)
        else:
            pdf.cell(0, 6, _safe_text("Formula similarity: N/A", pdf.font_family_name), ln=1)

        # Feedback
        pdf.multi_cell(0, 6, _safe_text("Feedback: " + q.get("feedback", ""), pdf.font_family_name))
        pdf.ln(2)

    pdf.output(path)
    return path


# ---------- CLI: read all JSONs and build PDFs ----------

if __name__ == "__main__":
    """
    Usage:

        # For SBERT results
        python -m src.report_generator

    This will:
      - Look in results/eval/ for *_eval.json files
      - Generate one PDF per JSON in results/reports/

    You can also change ReportConfig(eval_root=..., report_root=...)
    to generate LLM reports from results/eval_llm -> results/reports_llm.
    """
    cfg = ReportConfig()

    if not os.path.isdir(cfg.eval_root):
        print(f"[ERROR] Evaluation JSON folder not found: {cfg.eval_root}")
        raise SystemExit(1)

    os.makedirs(cfg.report_root, exist_ok=True)

    for fname in sorted(os.listdir(cfg.eval_root)):
        if not fname.endswith("_eval.json"):
            continue

        json_path = os.path.join(cfg.eval_root, fname)
        with open(json_path, "r", encoding="utf-8") as f:
            result = json.load(f)

        print(f"Generating PDF for {result['student_base']}...")
        pdf_path = generate_pdf_from_result(result, cfg)
        print(f"  -> {pdf_path}")

    print("\n[INFO] All reports generated.")
