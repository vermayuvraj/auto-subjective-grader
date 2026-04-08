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
from typing import Dict, Any

from fpdf import FPDF


# ---------- Config ----------

@dataclass
class ReportConfig:
    eval_root: str = "results/eval"
    report_root: str = "results/reports"


# ---------- PDF helper ----------

class ReportPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Automated Answer Sheet Evaluation", ln=1, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
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
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Student: {result['student_base']}", ln=1)
    pdf.cell(
        0,
        8,
        f"Total Score: {result['total_score']:.2f} / {result['max_total']:.2f}",
        ln=1,
    )
    pdf.cell(0, 8, f"Percentage: {result['percentage']:.2f}%", ln=1)
    pdf.ln(4)

    # ----- Per-question detail -----
    for q in result["questions"]:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(
            0,
            8,
            f"Q{q['question_id']}: {q['score']:.2f} / {q['max_marks']:.2f}",
            ln=1,
        )

        # ---- Safe similarity display ----
        pdf.set_font("Arial", "", 11)

        txt_sim = q.get("text_similarity", None)
        diag_sim = q.get("diagram_similarity", None)
        formula_sim = q.get("formula_similarity", None)

        # Text similarity
        if isinstance(txt_sim, (int, float)):
            pdf.cell(0, 6, f"Text similarity: {txt_sim:.3f}", ln=1)
        else:
            pdf.cell(0, 6, "Text similarity: N/A (LLM evaluation)", ln=1)

        # Diagram similarity
        if isinstance(diag_sim, (int, float)):
            pdf.cell(0, 6, f"Diagram similarity: {diag_sim:.3f}", ln=1)
        else:
            pdf.cell(0, 6, "Diagram similarity: N/A (LLM evaluation)", ln=1)

        # Formula similarity
        if isinstance(formula_sim, (int, float)):
            pdf.cell(0, 6, f"Formula similarity: {formula_sim:.3f}", ln=1)
        else:
            pdf.cell(0, 6, "Formula similarity: N/A", ln=1)

        # Feedback
        pdf.multi_cell(0, 6, "Feedback: " + q.get("feedback", ""))
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
