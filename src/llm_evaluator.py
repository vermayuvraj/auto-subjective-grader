import sys
import os
import warnings
import mimetypes
import re
import time
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import os
import json
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

import google.auth
from google_cloud_auth import get_google_auth_credentials, resolve_google_cloud_project_id

# Hide a known runtime-version deprecation warning from google.api_core.
# This keeps CLI output clean while the project remains on Python 3.10.
warnings.filterwarnings(
    "ignore",
    message=r".*Google will stop supporting.*google\.api_core.*",
    category=FutureWarning,
    module=r"google\.api_core\._python_version_support",
)

from google import genai
from google.genai import types

from evaluation_core import (
    load_ocr_pages,
    load_diagram_image,
    base_name_from_pdf,
    load_rubric,
)
from formula_evaluator import load_formula_page, score_formula_sets

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


def _default_adc_path() -> Optional[str]:
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            return None
        return os.path.join(appdata, "gcloud", "application_default_credentials.json")

    return os.path.join(os.path.expanduser("~"), ".config", "gcloud", "application_default_credentials.json")


def _should_attempt_adc_project_resolution() -> bool:
    explicit_credentials = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if explicit_credentials:
        return os.path.exists(explicit_credentials)

    adc_path = _default_adc_path()
    if adc_path and os.path.exists(adc_path):
        return True

    return bool(
        os.environ.get("K_SERVICE")
        or os.environ.get("FUNCTION_TARGET")
        or os.environ.get("GAE_ENV")
    )


@dataclass
class LlmEvalConfig:
    ocr_root: str = "results/ocr"
    diagram_root: str = "results/diagrams"
    formula_root: str = "results/formulas"
    rubric_path: str = "rubric.json"
    model_name: str = "gemini-2.5-flash"
    default_location: str = "global"


class LlmEvaluator:
    def __init__(self, config: LlmEvalConfig):
        self.config = config
        self.rubric = load_rubric(config.rubric_path)

        _load_local_env_files()
        project_id = self._resolve_vertex_project_id()
        if not project_id:
            raise RuntimeError(
                "Vertex AI is not configured for Gemini evaluation. Set GOOGLE_CLOUD_PROJECT "
                "(or VERTEX_AI_PROJECT / GCLOUD_PROJECT) or configure Application Default "
                "Credentials with a default project before running LLM evaluation."
            )

        location = (
            os.environ.get("VERTEX_AI_LOCATION")
            or os.environ.get("GOOGLE_CLOUD_LOCATION")
            or config.default_location
        )

        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", location)

        self.project_id = project_id
        self.location = location
        self.credentials = get_google_auth_credentials()
        self.client = genai.Client(
            vertexai=True,
            credentials=self.credentials,
            project=project_id,
            location=location,
            http_options=types.HttpOptions(api_version="v1"),
        )

    def _resolve_vertex_project_id(self) -> Optional[str]:
        project_id = resolve_google_cloud_project_id()
        if project_id:
            return project_id

        if not _should_attempt_adc_project_resolution():
            return None

        try:
            _, project_id = google.auth.default()
        except Exception:
            return None

        return project_id.strip() if project_id else None

    def _get_rubric_for_question(self, qid: int) -> Dict[str, Any]:
        key = str(qid)
        if key not in self.rubric:
            raise KeyError(f"Question id {qid} not found in rubric.")
        return self.rubric[key]

    def _compute_component_max(self, rubric_for_q: Dict[str, Any]) -> Dict[str, float]:
        """
        Compute max text, diagram, and formula marks based on rubric weights.
        """
        max_marks = float(rubric_for_q.get("max_marks", 10.0))
        text_w = float(rubric_for_q.get("text_weight", 0.7))
        diagram_w = float(rubric_for_q.get("diagram_weight", 0.3))
        formula_w = float(rubric_for_q.get("formula_weight", 0.0))

        total_w = text_w + diagram_w + formula_w
        if total_w <= 0:
            # default all marks to text if weights are invalid
            return {
                "max_marks": max_marks,
                "text_max": max_marks,
                "diagram_max": 0.0,
                "formula_max": 0.0,
                "text_weight": 1.0,
                "diagram_weight": 0.0,
                "formula_weight": 0.0,
            }

        text_max = max_marks * text_w / total_w
        diagram_max = max_marks * diagram_w / total_w
        formula_max = max_marks * formula_w / total_w

        return {
            "max_marks": max_marks,
            "text_max": text_max,
            "diagram_max": diagram_max,
            "formula_max": formula_max,
            "text_weight": text_w,
            "diagram_weight": diagram_w,
            "formula_weight": formula_w,
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

    def _image_part_from_path(self, image_path: Optional[str]) -> Optional[types.Part]:
        if not image_path or not os.path.exists(image_path):
            return None

        mime_type, _ = mimetypes.guess_type(image_path)
        resolved_mime_type = mime_type or "image/png"

        with open(image_path, "rb") as image_file:
            return types.Part.from_bytes(data=image_file.read(), mime_type=resolved_mime_type)

    def _call_vertex_ai(
        self,
        prompt: str,
        ideal_diagram_path: Optional[str],
        student_diagram_path: Optional[str],
    ) -> Dict[str, Any]:
        """
        Call Gemini on Vertex AI with text prompt + optional ideal & student diagram images.
        Expect a JSON object in the response body.
        """
        parts: List[Any] = [prompt]

        # Attach images if available.
        # If both exist, FIRST = ideal, SECOND = student.
        ideal_part = self._image_part_from_path(ideal_diagram_path)
        if ideal_part is not None:
            parts.append(ideal_part)

        student_part = self._image_part_from_path(student_diagram_path)
        if student_part is not None:
            parts.append(student_part)

        response = self.client.models.generate_content(
            model=self.config.model_name,
            contents=parts,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "required": [
                        "text_score",
                        "diagram_score",
                        "score",
                        "max_marks",
                        "feedback",
                    ],
                    "properties": {
                        "text_score": {"type": "NUMBER"},
                        "diagram_score": {"type": "NUMBER"},
                        "score": {"type": "NUMBER"},
                        "max_marks": {"type": "NUMBER"},
                        "feedback": {"type": "STRING"},
                    },
                },
            ),
        )

        if response.parsed:
            if isinstance(response.parsed, dict):
                return response.parsed
            return json.loads(json.dumps(response.parsed))

        raw = response.text or ""
        if not raw.strip():
            raise ValueError("Vertex AI returned an empty response.")
        return json.loads(raw)

    def _is_retryable_vertex_error(self, error: Exception) -> bool:
        message = str(error).upper()
        return any(
            token in message
            for token in (
                "RESOURCE_EXHAUSTED",
                "429",
                "TOO MANY REQUEST",
                "SERVICE UNAVAILABLE",
                "503",
            )
        )

    def _extract_retry_delay_seconds(self, error: Exception, attempt: int) -> float:
        message = str(error)
        patterns = (
            r"retry in\s+([0-9]+(?:\.[0-9]+)?)s",
            r"seconds:\s*([0-9]+(?:\.[0-9]+)?)",
        )
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return min(float(match.group(1)), 60.0)

        return min(15.0 * attempt, 60.0)

    def _call_vertex_ai_with_retry(
        self,
        prompt: str,
        ideal_diagram_path: Optional[str],
        student_diagram_path: Optional[str],
    ) -> Dict[str, Any]:
        last_error: Optional[Exception] = None
        for attempt in range(1, 5):
            try:
                return self._call_vertex_ai(prompt, ideal_diagram_path, student_diagram_path)
            except Exception as error:  # pragma: no cover - retry path depends on external API behavior
                last_error = error
                if not self._is_retryable_vertex_error(error) or attempt == 4:
                    raise
                time.sleep(self._extract_retry_delay_seconds(error, attempt))

        if last_error is not None:
            raise last_error
        raise RuntimeError("Vertex AI request failed without an explicit error.")

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
              "formula_similarity": float or None,
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
            formula_max = comp_max["formula_max"]

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
                        "formula_similarity": 0.0,
                        "feedback": "No answer detected for this question.",
                    }
                )
                continue

            ideal_text = ideal_page_data.get("text", "")
            student_text = student_page_data.get("text", "")
            ideal_formulas = load_formula_page(ideal_base, page_no, self.config.formula_root)
            student_formulas = load_formula_page(student_base, page_no, self.config.formula_root)

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
                data = self._call_vertex_ai_with_retry(prompt, ideal_diag_path, student_diag_path)

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

            formula_similarity = None
            formula_feedback = ""
            formula_score = 0.0
            if formula_max > 0:
                formula_similarity, formula_feedback = score_formula_sets(
                    ideal_formulas,
                    student_formulas,
                )
                if formula_similarity is not None:
                    formula_score = max(0.0, min(formula_max, formula_similarity * formula_max))

            score = max(0.0, min(max_marks, score + formula_score))

            total_score += score

            # Convert to similarity-style fractions (0..1) for compatibility
            text_sim = (text_score / text_max) if text_max > 0 else None
            diagram_sim = (diagram_score / diagram_max) if diagram_max > 0 else None
            combined_feedback = feedback.strip()
            if formula_similarity is not None and formula_feedback:
                combined_feedback = (
                    f"{combined_feedback} Formula check: {formula_feedback}".strip()
                    if combined_feedback
                    else f"Formula check: {formula_feedback}"
                )

            results.append(
                {
                    "question_id": qid,
                    "score": score,
                    "max_marks": max_marks,
                    "text_similarity": text_sim,
                    "diagram_similarity": diagram_sim,
                    "formula_similarity": formula_similarity,
                    "feedback": combined_feedback or feedback,
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
