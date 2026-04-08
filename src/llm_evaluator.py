import sys
import os
import warnings
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import os
import json
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

from PIL import Image

# Hide a known runtime-version deprecation warning from google.api_core.
# This keeps CLI output clean while the project remains on Python 3.10.
warnings.filterwarnings(
    "ignore",
    message=r".*Google will stop supporting.*google\.api_core.*",
    category=FutureWarning,
    module=r"google\.api_core\._python_version_support",
)

import google.generativeai as genai

from evaluation_core import (
    load_ocr_pages,
    load_diagram_image,
    base_name_from_pdf,
    load_rubric,
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def _strip_optional_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _load_env_file_if_present(env_path: str) -> None:
    """
    Load simple environment variables from a local .env file.

    Supports both:
      KEY=value
      $env:KEY=value
    """
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            key = None
            value = None

            if line.startswith("$env:") and "=" in line:
                key, value = line[5:].split("=", 1)
            elif line.startswith("export ") and "=" in line:
                key, value = line[7:].split("=", 1)
            elif "=" in line:
                key, value = line.split("=", 1)

            if not key:
                continue

            key = key.strip()
            value = _strip_optional_quotes(value)
            if key and key not in os.environ:
                os.environ[key] = value


def _load_local_env_files() -> None:
    seen_paths = set()
    for env_path in (
        os.path.join(os.getcwd(), ".env"),
        os.path.join(PROJECT_ROOT, ".env"),
    ):
        norm_path = os.path.abspath(env_path)
        if norm_path in seen_paths:
            continue
        seen_paths.add(norm_path)
        _load_env_file_if_present(norm_path)


@dataclass
class LlmEvalConfig:
    ocr_root: str = "results/ocr"
    diagram_root: str = "results/diagrams"
    rubric_path: str = "rubric.json"
    model_name: str = "gemini-2.5-flash"
    api_key_env: str = "GEMINI_API_KEY"


class LlmEvaluator:
    def __init__(self, config: LlmEvalConfig):
        self.config = config
        self.rubric = load_rubric(config.rubric_path)

        _load_local_env_files()
        api_key = os.environ.get(config.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"Environment variable {config.api_key_env} is not set. "
                "Please set your Gemini API key before running LLM evaluation."
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(config.model_name)

    def _get_rubric_for_question(self, qid: int) -> Dict[str, Any]:
        key = str(qid)
        if key not in self.rubric:
            raise KeyError(f"Question id {qid} not found in rubric.")
        return self.rubric[key]

    def _compute_component_max(self, rubric_for_q: Dict[str, Any]) -> Dict[str, float]:
        """
        Compute max text and diagram marks based on rubric weights.
        """
        max_marks = float(rubric_for_q.get("max_marks", 10.0))
        text_w = float(rubric_for_q.get("text_weight", 0.7))
        diagram_w = float(rubric_for_q.get("diagram_weight", 0.3))

        total_w = text_w + diagram_w
        if total_w <= 0:
            # default all marks to text if weights are invalid
            return {
                "max_marks": max_marks,
                "text_max": max_marks,
                "diagram_max": 0.0,
                "text_weight": 1.0,
                "diagram_weight": 0.0,
            }

        text_max = max_marks * text_w / total_w
        diagram_max = max_marks * diagram_w / total_w

        return {
            "max_marks": max_marks,
            "text_max": text_max,
            "diagram_max": diagram_max,
            "text_weight": text_w,
            "diagram_weight": diagram_w,
        }

    def _build_llm_prompt(
        self,
        qid: int,
        ideal_text: str,
        student_text: str,
        rubric_for_q: Dict[str, Any],
        text_max: float,
        diagram_max: float,
        has_ideal_diagram: bool,
        has_student_diagram: bool,
    ) -> str:
        """
        Build a text prompt for Gemini. We send ideal + student diagrams as images.
        The model is asked to produce text_score and diagram_score separately.
        """
        rubric_json = json.dumps(rubric_for_q, ensure_ascii=False, indent=2)

        diagram_info = (
            "Two images will be provided: the FIRST is the IDEAL diagram, "
            "the SECOND is the STUDENT's diagram. Use them to judge the diagram score."
            if (has_ideal_diagram and has_student_diagram)
            else "No diagrams or only one diagram image may be provided; "
                 "if the student's diagram is missing or clearly poor, the diagram_score should be low or zero."
        )

        prompt = f"""
You are grading a student's answer to a question.

You are given:
1. The ideal reference answer (teacher's solution) text.
2. The student's answer text.
3. Optionally, diagram images (ideal + student) if provided.
4. A rubric JSON describing how to allocate marks for this question.

Question ID: {qid}

Rubric (JSON):
{rubric_json}

Maximum marks for this question: {text_max + diagram_max}
Maximum marks for TEXT only: {text_max}
Maximum marks for DIAGRAM only: {diagram_max}

{diagram_info}

Ideal answer text:
\"\"\"{ideal_text}\"\"\"

Student answer text:
\"\"\"{student_text}\"\"\"

Instructions:
- First, evaluate ONLY the student's TEXT (ignoring diagrams). Compare it with the ideal text in terms of
  factual correctness, completeness, relevance, clarity, and coverage of key points.
- Give a numeric text_score between 0 and {text_max} based on how strong the student's text is.
- Second, evaluate ONLY the student's DIAGRAM (if available) compared to the ideal diagram and the rubric.
  Consider structure, correctness of components, labels, and clarity.
- Give a numeric diagram_score between 0 and {diagram_max}. If the student did not draw a diagram or it is
  completely incorrect, diagram_score should be 0 or very close to 0.
- The final score for this question is score = text_score + diagram_score, but it must NOT exceed {text_max + diagram_max}.
- Be relatively strict: only very high-quality answers should receive scores close to these maxima.

Return ONLY a strict JSON object with the following keys:
- "text_score": number between 0 and {text_max}
- "diagram_score": number between 0 and {diagram_max}
- "score": number between 0 and {text_max + diagram_max} (normally text_score + diagram_score)
- "max_marks": {text_max + diagram_max}
- "feedback": a short, specific feedback string for the student (one paragraph).

Do not include any extra keys. Do not include explanations outside the JSON.
"""
        return prompt

    def _call_gemini(
        self,
        prompt: str,
        ideal_diagram_path: Optional[str],
        student_diagram_path: Optional[str],
    ) -> Dict[str, Any]:
        """
        Call Gemini with text prompt + optional ideal & student diagram images.
        Expect a JSON object in the response text.
        """
        parts: List[Any] = [prompt]

        # Attach images if available.
        # If both exist, FIRST = ideal, SECOND = student.
        if ideal_diagram_path and os.path.exists(ideal_diagram_path):
            try:
                img_ideal = Image.open(ideal_diagram_path)
                parts.append(img_ideal)
            except Exception:
                pass

        if student_diagram_path and os.path.exists(student_diagram_path):
            try:
                img_student = Image.open(student_diagram_path)
                parts.append(img_student)
            except Exception:
                pass

        response = self.model.generate_content(parts)
        raw = response.text

        # Extract JSON from possible surrounding text/fences
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError(f"LLM response did not contain a JSON object:\n{raw}")

        json_str = raw[start : end + 1]
        data = json.loads(json_str)
        return data

    def evaluate_student(
        self,
        ideal_pdf_path: str,
        student_pdf_path: str,
    ) -> Dict[str, Any]:
        """
        Evaluate one student answer sheet against the ideal using Gemini.

        Returns a dict:
        {
          "student_base": "...",
          "total_score": ...,
          "max_total": ...,
          "percentage": ...,
          "questions": [
            {
              "question_id": int,
              "score": float,
              "max_marks": float,
              "text_similarity": float or None,
              "diagram_similarity": float or None,
              "feedback": str,
            }, ...
          ]
        }
        """
        ideal_base = base_name_from_pdf(ideal_pdf_path)
        student_base = base_name_from_pdf(student_pdf_path)

        ideal_ocr = load_ocr_pages(ideal_base, self.config.ocr_root)
        student_ocr = load_ocr_pages(student_base, self.config.ocr_root)

        results: List[Dict[str, Any]] = []
        total_score = 0.0
        max_total = 0.0

        for page_no, ideal_page_data in sorted(ideal_ocr.items()):
            qid = page_no
            rubric_for_q = self._get_rubric_for_question(qid)
            comp_max = self._compute_component_max(rubric_for_q)
            max_marks = comp_max["max_marks"]
            text_max = comp_max["text_max"]
            diagram_max = comp_max["diagram_max"]

            max_total += max_marks

            student_page_data = student_ocr.get(page_no)
            if not student_page_data:
                # No answer for this question
                results.append(
                    {
                        "question_id": qid,
                        "score": 0.0,
                        "max_marks": max_marks,
                        "text_similarity": 0.0,
                        "diagram_similarity": 0.0,
                        "feedback": "No answer detected for this question.",
                    }
                )
                continue

            ideal_text = ideal_page_data.get("text", "")
            student_text = student_page_data.get("text", "")

            # Diagram paths (if exist)
            ideal_diag_path = os.path.join(
                self.config.diagram_root,
                f"{ideal_base}_page{page_no}_diagram.png",
            )
            student_diag_path = os.path.join(
                self.config.diagram_root,
                f"{student_base}_page{page_no}_diagram.png",
            )
            has_ideal_diagram = os.path.exists(ideal_diag_path)
            has_student_diagram = os.path.exists(student_diag_path)

            prompt = self._build_llm_prompt(
                qid=qid,
                ideal_text=ideal_text,
                student_text=student_text,
                rubric_for_q=rubric_for_q,
                text_max=text_max,
                diagram_max=diagram_max,
                has_ideal_diagram=has_ideal_diagram,
                has_student_diagram=has_student_diagram,
            )

            try:
                data = self._call_gemini(prompt, ideal_diag_path, student_diag_path)

                # Extract scores with safety
                text_score = float(data.get("text_score", 0.0))
                diagram_score = float(data.get("diagram_score", 0.0))
                score = float(data.get("score", text_score + diagram_score))
                feedback = str(data.get("feedback", "")).strip()

                # Clamp to valid ranges
                if text_max > 0:
                    text_score = max(0.0, min(text_max, text_score))
                else:
                    text_score = 0.0

                if diagram_max > 0:
                    diagram_score = max(0.0, min(diagram_max, diagram_score))
                else:
                    diagram_score = 0.0

                score = text_score + diagram_score
                score = max(0.0, min(max_marks, score))

            except Exception as e:
                # On any LLM failure, fall back to zero score with error feedback
                text_score = 0.0
                diagram_score = 0.0
                score = 0.0
                feedback = f"Automatic LLM grading failed: {e}"

            total_score += score

            # Convert to similarity-style fractions (0..1) for compatibility
            text_sim = (text_score / text_max) if text_max > 0 else None
            diagram_sim = (diagram_score / diagram_max) if diagram_max > 0 else None

            results.append(
                {
                    "question_id": qid,
                    "score": score,
                    "max_marks": max_marks,
                    "text_similarity": text_sim,
                    "diagram_similarity": diagram_sim,
                    "feedback": feedback,
                }
            )

        percentage = (total_score / max_total * 100.0) if max_total > 0 else 0.0

        return {
            "student_base": student_base,
            "total_score": total_score,
            "max_total": max_total,
            "percentage": percentage,
            "questions": results,
        }
