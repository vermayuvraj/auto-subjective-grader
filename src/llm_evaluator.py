import sys
import os
import warnings
import mimetypes
import re
import time
import threading
import cv2
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

import evaluation_core
from evaluation_core import (
    load_ocr_pages,
    load_diagram_image,
    base_name_from_pdf,
    load_rubric,
    build_question_answer_map,
    _question_keyword_map_from_rubric,
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

        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        os.environ["GOOGLE_CLOUD_LOCATION"] = location

        self.project_id = project_id
        self.location = location
        self.credentials = get_google_auth_credentials()
        self._thread_local = threading.local()
        self._fallback_lock = threading.Lock()
        self._fallback_evaluator = None
        self.client = self._build_vertex_client(self.credentials)
        self._thread_local.client = self.client
        self._thread_local.credentials = self.credentials

    def _build_vertex_client(self, credentials=None):
        return genai.Client(
            vertexai=True,
            credentials=credentials or self.credentials,
            project=self.project_id,
            location=self.location,
            http_options=types.HttpOptions(api_version="v1"),
        )

    def _get_thread_client(self):
        client = getattr(self._thread_local, "client", None)
        if client is not None:
            return client

        credentials = get_google_auth_credentials()
        client = self._build_vertex_client(credentials)
        self._thread_local.client = client
        self._thread_local.credentials = credentials
        return client

    def _refresh_vertex_client(self) -> None:
        credentials = get_google_auth_credentials()
        client = self._build_vertex_client(credentials)
        self.credentials = credentials
        self.client = client
        self._thread_local.credentials = credentials
        self._thread_local.client = client

    def _get_fallback_evaluator(self):
        if self._fallback_evaluator is not None:
            return self._fallback_evaluator

        with self._fallback_lock:
            if self._fallback_evaluator is None:
                fallback_cfg = evaluation_core.EvalConfig(
                    ocr_root=self.config.ocr_root,
                    diagram_root=self.config.diagram_root,
                    formula_root=self.config.formula_root,
                    rubric_path=self.config.rubric_path,
                )
                self._fallback_evaluator = evaluation_core.Evaluator(fallback_cfg)
        return self._fallback_evaluator

    def _summarize_llm_error(self, error: Exception) -> str:
        message = str(error).strip()
        if not message:
            return "Gemini evaluation temporarily failed."
        compact = re.sub(r"\s+", " ", message)
        if len(compact) > 220:
            compact = compact[:217].rstrip() + "..."
        return compact

    def _fallback_question_result(
        self,
        qid: int,
        ideal_text: str,
        student_text: str,
        ideal_diag_path: Optional[str],
        student_diag_path: Optional[str],
        ideal_formulas: List[Dict[str, Any]],
        student_formulas: List[Dict[str, Any]],
        llm_error: Exception,
    ) -> Dict[str, Any]:
        fallback_evaluator = self._get_fallback_evaluator()
        ideal_diagram = None
        student_diagram = None
        if ideal_diag_path and os.path.exists(ideal_diag_path):
            ideal_diagram = cv2.imread(ideal_diag_path)
        if student_diag_path and os.path.exists(student_diag_path):
            student_diagram = cv2.imread(student_diag_path)

        fallback_result = fallback_evaluator.evaluate_question(
            qid=qid,
            ideal_text=ideal_text,
            student_text=student_text,
            ideal_diagram=ideal_diagram,
            student_diagram=student_diagram,
            ideal_formulas=ideal_formulas,
            student_formulas=student_formulas,
        )

        fallback_feedback = fallback_result.feedback.strip()
        error_note = self._summarize_llm_error(llm_error)
        combined_feedback = (
            f"{fallback_feedback} Gemini fallback used because the Vertex AI request failed: {error_note}"
            if fallback_feedback
            else f"Gemini fallback used because the Vertex AI request failed: {error_note}"
        )

        return {
            "question_id": qid,
            "score": float(fallback_result.score),
            "max_marks": float(fallback_result.max_marks),
            "text_similarity": fallback_result.text_similarity,
            "diagram_similarity": fallback_result.diagram_similarity,
            "formula_similarity": fallback_result.formula_similarity,
            "feedback": combined_feedback,
        }

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
        holistic_scoring: bool,
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

        holistic_note = (
            "Treat OCR noise, spelling mistakes, and handwriting distortions generously. "
            "Focus on whether the student has expressed the correct idea for the question, "
            "not on exact token matches."
            if holistic_scoring
            else "Grade strictly against the rubric and the ideal answer."
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
- {holistic_note}
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

        client = self._get_thread_client()
        response = client.models.generate_content(
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

    def _is_auth_vertex_error(self, error: Exception) -> bool:
        message = str(error).upper()
        return any(
            token in message
            for token in (
                "401",
                "UNAUTHENTICATED",
                "ACCESS_TOKEN_TYPE_UNSUPPORTED",
                "INVALID AUTHENTICATION CREDENTIALS",
                "EXPECTED OAUTH 2 ACCESS TOKEN",
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
                if self._is_auth_vertex_error(error) and attempt < 3:
                    self._refresh_vertex_client()
                    time.sleep(min(2.0 * attempt, 5.0))
                    continue
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
        known_qids = sorted(int(qid) for qid in self.rubric.keys())
        question_keywords = _question_keyword_map_from_rubric(self.rubric)
        ideal_answers = build_question_answer_map(
            ideal_base,
            self.config.ocr_root,
            known_qids,
            allow_loose_numeric_markers=False,
            question_keywords=question_keywords,
            continue_unmarked_pages=True,
        )
        student_answers = build_question_answer_map(
            student_base,
            self.config.ocr_root,
            known_qids,
            allow_loose_numeric_markers=False,
            question_keywords=question_keywords,
            continue_unmarked_pages=True,
        )

        results: List[Dict[str, Any]] = []
        total_score = 0.0
        max_total = 0.0

        for qid in known_qids:
            ideal_answer = ideal_answers.get(qid)
            ideal_page_data = ideal_ocr.get(qid, {})
            rubric_for_q = self._get_rubric_for_question(qid)
            comp_max = self._compute_component_max(rubric_for_q)
            max_marks = comp_max["max_marks"]
            text_max = comp_max["text_max"]
            diagram_max = comp_max["diagram_max"]
            formula_max = comp_max["formula_max"]
            use_symbolic_formula_score = bool(rubric_for_q.get("use_symbolic_formula_score", True))
            holistic_scoring = bool(rubric_for_q.get("llm_full_question_score", False))

            max_total += max_marks

            student_answer = student_answers.get(qid)
            if not student_answer or not student_answer.get("text", "").strip():
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

            ideal_text = (ideal_answer or {}).get("text") or ideal_page_data.get("text", "")
            student_text = student_answer.get("text", "")
            ideal_asset_page = (
                int(ideal_answer.get("primary_page"))
                if ideal_answer and ideal_answer.get("primary_page") and not ideal_answer.get("shared_page", False)
                else (qid if qid in ideal_ocr else None)
            )
            ideal_formulas = (
                load_formula_page(ideal_base, ideal_asset_page, self.config.formula_root)
                if ideal_asset_page is not None
                else []
            )
            student_asset_page = (
                int(student_answer.get("primary_page"))
                if student_answer.get("primary_page") and not student_answer.get("shared_page", False)
                else None
            )
            student_formulas = (
                load_formula_page(student_base, student_asset_page, self.config.formula_root)
                if student_asset_page is not None
                else []
            )

            # Diagram paths (if exist)
            ideal_diag_path = os.path.join(
                self.config.diagram_root,
                f"{ideal_base}_page{ideal_asset_page}_diagram.png",
            ) if ideal_asset_page is not None else None
            student_diag_path = (
                os.path.join(
                    self.config.diagram_root,
                    f"{student_base}_page{student_asset_page}_diagram.png",
                )
                if student_asset_page is not None
                else None
            )
            has_ideal_diagram = bool(ideal_diag_path and os.path.exists(ideal_diag_path))
            has_student_diagram = bool(student_diag_path and os.path.exists(student_diag_path))

            prompt = self._build_llm_prompt(
                qid=qid,
                ideal_text=ideal_text,
                student_text=student_text,
                rubric_for_q=rubric_for_q,
                text_max=text_max,
                diagram_max=diagram_max,
                has_ideal_diagram=has_ideal_diagram,
                has_student_diagram=has_student_diagram,
                holistic_scoring=holistic_scoring,
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
                fallback_entry = self._fallback_question_result(
                    qid=qid,
                    ideal_text=ideal_text,
                    student_text=student_text,
                    ideal_diag_path=ideal_diag_path,
                    student_diag_path=student_diag_path,
                    ideal_formulas=ideal_formulas,
                    student_formulas=student_formulas,
                    llm_error=e,
                )
                total_score += float(fallback_entry["score"])
                results.append(fallback_entry)
                continue

            formula_similarity = None
            formula_feedback = ""
            formula_score = 0.0
            if formula_max > 0 and use_symbolic_formula_score:
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
