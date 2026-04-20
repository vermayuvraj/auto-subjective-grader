
import os
import re
import json
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Any, Optional, List, Iterable, Tuple

import numpy as np
import cv2
import torch
from huggingface_hub import snapshot_download
from sentence_transformers import SentenceTransformer, util
from transformers import CLIPProcessor, CLIPModel

from formula_evaluator import load_formula_page, score_formula_sets

# ---------- Config dataclass ----------

@dataclass
class EvalConfig:
    ocr_root: str = "results/ocr"
    diagram_root: str = "results/diagrams"
    formula_root: str = "results/formulas"
    rubric_path: str = "rubric.json"
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


# ---------- Utility loaders ----------

def load_rubric(rubric_path: str) -> Dict[str, Any]:
    if not os.path.exists(rubric_path):
        raise FileNotFoundError(f"Rubric file not found at {rubric_path}")
    with open(rubric_path, "r", encoding="utf-8") as f:
        rubric = json.load(f)
    return rubric


def base_name_from_pdf(pdf_path: str) -> str:
    """Return base filename without extension."""
    return os.path.splitext(os.path.basename(pdf_path))[0]


ANSWER_NO_MARKER_PATTERN = re.compile(
    r"^\s*(?:ans(?:wer)?[a-z]{0,4}|answ[a-z]{0,4}|answer[a-z]{0,4}|ass)(?:\s*no)?\s*[-:.)]*\s*(\d{1,2})\b\s*(.*)$",
    re.IGNORECASE,
)
QUESTION_NO_MARKER_PATTERN = re.compile(
    r"^\s*(?:q(?:uestion)?|que(?:stion)?|ques|qwestim|questim)\s*[.\s]*(?:no|n0)?\s*[-:.)]*\s*(\d{1,2})\b\s*(.*)$",
    re.IGNORECASE,
)
NO_PREFIX_MARKER_PATTERN = re.compile(
    r"^\s*(?:no|n0|mo|m0)\s*[-:.)]*\s*(\d{1,2})\b\s*(.*)$",
    re.IGNORECASE,
)
LEADING_NUMERIC_MARKER_PATTERN = re.compile(
    r"^\s*(\d{1,2})\s*[\].):,-]*\s*(.*)$",
    re.IGNORECASE,
)
JOINED_NUMERIC_ANSWER_PATTERN = re.compile(
    r"^\s*(\d{1,2})\s*[A-Za-z]{0,2}\s*ans(?:wer|ws|we|w)?\s*[-:.)]*\s*(.*)$",
    re.IGNORECASE,
)


def _bbox_to_rect(bbox: List[List[float]]) -> Optional[Tuple[float, float, float, float]]:
    if not bbox:
        return None

    xs = [float(point[0]) for point in bbox]
    ys = [float(point[1]) for point in bbox]
    x1 = min(xs)
    y1 = min(ys)
    x2 = max(xs)
    y2 = max(ys)
    if x2 <= x1 or y2 <= y1:
        return None
    return (x1, y1, x2, y2)


def _ordered_ocr_blocks(blocks: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched: List[Tuple[float, float, Dict[str, Any]]] = []
    for block in blocks:
        rect = _bbox_to_rect(block.get("bbox", []))
        if rect is None:
            continue
        x1, y1, _, _ = rect
        enriched.append((y1, x1, block))

    enriched.sort(key=lambda item: (item[0], item[1]))
    return [block for _, _, block in enriched]


def _normalize_inline_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _coerce_allowed_qids(known_qids: Optional[Iterable[int]]) -> Optional[set[int]]:
    return {int(qid) for qid in known_qids} if known_qids is not None else None


def _pick_allowed_qid(candidate: Optional[str], allowed: Optional[set[int]]) -> Optional[int]:
    try:
        qid = int(candidate) if candidate is not None else None
    except (TypeError, ValueError):
        return None
    if qid is None:
        return None
    if allowed is not None and qid not in allowed:
        return None
    return qid


def _looks_like_question_heading(text: str) -> bool:
    normalized = _normalize_inline_text(text)
    if len(normalized) < 8:
        return False

    if re.fullmatch(r"[\d\s./,:;+\-()]+", normalized):
        return False

    alpha_hits = len(re.findall(r"[A-Za-z]", normalized))
    word_hits = len(re.findall(r"[A-Za-z]{2,}", normalized))
    digit_hits = len(re.findall(r"\d", normalized))
    if alpha_hits < 4 or word_hits < 2:
        return False

    if digit_hits > alpha_hits:
        return False

    return True


def extract_question_marker(
    text: str,
    known_qids: Optional[Iterable[int]] = None,
    allow_loose_numeric_markers: bool = True,
) -> Optional[Tuple[int, str]]:
    normalized = _normalize_inline_text(text)
    if not normalized:
        return None

    allowed = _coerce_allowed_qids(known_qids)

    strong_matchers = (
        (QUESTION_NO_MARKER_PATTERN, "question"),
        (ANSWER_NO_MARKER_PATTERN, "answer"),
        (NO_PREFIX_MARKER_PATTERN, "number"),
    )
    for pattern, marker_type in strong_matchers:
        match = pattern.match(normalized)
        if not match:
            continue
        qid = _pick_allowed_qid(match.group(1), allowed)
        if qid is not None:
            return qid, marker_type

    if allow_loose_numeric_markers:
        joined_answer_match = JOINED_NUMERIC_ANSWER_PATTERN.match(normalized)
        if joined_answer_match:
            qid = _pick_allowed_qid(joined_answer_match.group(1), allowed)
            if qid is not None:
                return qid, "numeric-answer"

        leading_numeric_match = LEADING_NUMERIC_MARKER_PATTERN.match(normalized)
        if leading_numeric_match:
            remainder = _normalize_inline_text(leading_numeric_match.group(2))
            if _looks_like_question_heading(remainder):
                qid = _pick_allowed_qid(leading_numeric_match.group(1), allowed)
                if qid is not None:
                    return qid, "numeric"

    return None


def extract_question_id(text: str, known_qids: Optional[Iterable[int]] = None) -> Optional[int]:
    marker = extract_question_marker(text, known_qids)
    return marker[0] if marker else None


def _strip_question_marker_prefix(text: str) -> str:
    normalized = _normalize_inline_text(text)
    if not normalized:
        return ""

    anchored_patterns = (
        QUESTION_NO_MARKER_PATTERN,
        ANSWER_NO_MARKER_PATTERN,
        NO_PREFIX_MARKER_PATTERN,
        JOINED_NUMERIC_ANSWER_PATTERN,
        LEADING_NUMERIC_MARKER_PATTERN,
    )
    for pattern in anchored_patterns:
        match = pattern.match(normalized)
        if not match:
            continue
        remainder = _normalize_inline_text(match.group(2) if match.lastindex and match.lastindex >= 2 else "")
        if pattern is LEADING_NUMERIC_MARKER_PATTERN and not _looks_like_question_heading(remainder):
            continue
        return remainder

    return normalized


def build_question_answer_map(
    base_name: str,
    ocr_root: str,
    known_qids: Iterable[int],
    allow_loose_numeric_markers: bool = True,
) -> Dict[int, Dict[str, Any]]:
    """
    Build a question-wise answer map from OCR pages.

    When a student PDF contains multiple answers on a single page, OCR often
    captures question markers such as "Que - 6" or "Question 3". We segment the
    page into question-wise text ranges using those markers. If no markers are
    found for a page, we fall back to the original page-number mapping.

    Returns:
      {
        qid: {
          "question_id": int,
          "text": str,
          "page_numbers": [int, ...],
          "primary_page": int,
          "source": "marker" | "page",
          "shared_page": bool,
        }
      }
    """
    pages = load_ocr_pages(base_name, ocr_root)
    allowed_qids = sorted({int(qid) for qid in known_qids})
    answer_map: Dict[int, Dict[str, Any]] = {}
    pages_with_marker_segments: set[int] = set()

    for page_no, page_data in sorted(pages.items()):
        ordered_blocks = _ordered_ocr_blocks(page_data.get("blocks", []) or [])
        detected_qids: List[int] = []
        segments: List[Tuple[int, List[str]]] = []
        current_qid: Optional[int] = None
        current_parts: List[str] = []
        preamble_parts: List[str] = []
        strong_marker_seen = False

        for block in ordered_blocks:
            block_text = _normalize_inline_text(str(block.get("text", "")))
            if not block_text:
                continue

            marker = extract_question_marker(
                block_text,
                allowed_qids,
                allow_loose_numeric_markers=allow_loose_numeric_markers,
            )
            if marker is not None:
                block_qid, marker_source = marker
                if strong_marker_seen and marker_source == "numeric":
                    if current_qid is not None:
                        current_parts.append(block_text)
                    else:
                        preamble_parts.append(block_text)
                    continue
                if current_qid is None and preamble_parts and page_no in allowed_qids and page_no != block_qid:
                    preamble_text = "\n".join(
                        part for part in preamble_parts if _normalize_inline_text(part)
                    ).strip()
                    if len(preamble_text) >= 20:
                        segments.append((page_no, preamble_parts.copy()))
                        detected_qids.append(page_no)
                preamble_parts = []
                if current_qid is not None:
                    segments.append((current_qid, current_parts))
                current_qid = block_qid
                detected_qids.append(block_qid)
                current_parts = []
                remainder = _strip_question_marker_prefix(block_text)
                if remainder:
                    current_parts.append(remainder)
                strong_marker_seen = strong_marker_seen or marker_source in {"question", "answer", "number"}
                continue

            if current_qid is not None:
                current_parts.append(block_text)
            else:
                preamble_parts.append(block_text)

        if current_qid is not None:
            segments.append((current_qid, current_parts))

        unique_qids = list(dict.fromkeys(detected_qids))
        if segments:
            pages_with_marker_segments.add(page_no)

        for qid, parts in segments:
            text = "\n".join(part for part in parts if _normalize_inline_text(part)).strip()
            if not text and len(unique_qids) == 1:
                text = _normalize_inline_text(str(page_data.get("text", "")))

            entry = answer_map.setdefault(
                qid,
                {
                    "question_id": qid,
                    "text_parts": [],
                    "page_numbers": [],
                    "primary_page": page_no,
                    "source": "marker",
                    "shared_page": len(unique_qids) > 1,
                    "marker_confidence": "strong" if strong_marker_seen else "medium",
                },
            )
            if text:
                entry["text_parts"].append(text)
            entry["page_numbers"].append(page_no)
            entry["shared_page"] = entry["shared_page"] or len(unique_qids) > 1
            entry["primary_page"] = min(int(entry["primary_page"]), page_no)
            entry["marker_confidence"] = (
                "strong"
                if entry.get("marker_confidence") == "strong" or strong_marker_seen
                else "medium"
            )

    # Fallback for pages that do not expose explicit question markers.
    for page_no, page_data in sorted(pages.items()):
        if page_no in pages_with_marker_segments:
            continue
        if page_no not in allowed_qids or page_no in answer_map:
            continue

        answer_map[page_no] = {
            "question_id": page_no,
            "text_parts": [_normalize_inline_text(str(page_data.get("text", "")))],
            "page_numbers": [page_no],
            "primary_page": page_no,
            "source": "page",
            "shared_page": False,
            "marker_confidence": "page",
        }

    finalized: Dict[int, Dict[str, Any]] = {}
    for qid, entry in answer_map.items():
        combined_text = "\n".join(
            part for part in entry.pop("text_parts", []) if _normalize_inline_text(part)
        ).strip()
        finalized[qid] = {
            "question_id": int(entry["question_id"]),
            "text": combined_text,
            "page_numbers": sorted({int(page_no) for page_no in entry["page_numbers"]}),
            "primary_page": int(entry["primary_page"]),
            "source": str(entry["source"]),
            "shared_page": bool(entry["shared_page"]),
            "marker_confidence": str(entry.get("marker_confidence", entry["source"])),
        }

    return finalized


@lru_cache(maxsize=8)
def resolve_model_source(repo_id: str) -> str:
    """
    Prefer an already-downloaded Hugging Face snapshot to avoid repeated
    network checks during local startup. Falls back to the repo id if the
    model is not cached yet.
    """
    try:
        return snapshot_download(repo_id=repo_id, local_files_only=True)
    except Exception:
        return repo_id


def load_ocr_pages(base_name: str, ocr_root: str) -> Dict[int, Dict[str, Any]]:
    """
    Load all OCR JSON pages for a given base PDF name.

    Expects files named:
      <base_name>_page1.json, <base_name>_page2.json, ...

    Returns { page_number: { 'page': int, 'text': str, 'blocks': [...] } }
    """
    pages: Dict[int, Dict[str, Any]] = {}
    if not os.path.isdir(ocr_root):
        raise FileNotFoundError(f"OCR root '{ocr_root}' does not exist.")

    prefix = base_name + "_page"
    for fname in os.listdir(ocr_root):
        if not fname.startswith(prefix) or not fname.endswith(".json"):
            continue
        full_path = os.path.join(ocr_root, fname)
        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        page_no = int(data.get("page", 0))
        pages[page_no] = data

    if not pages:
        raise FileNotFoundError(f"No OCR pages found for base '{base_name}' in '{ocr_root}'")

    return pages


def load_diagram_image(base_name: str, page_no: int, diagram_root: str) -> Optional[np.ndarray]:
    """
    Load a diagram image saved by diagram_extractor.py.

    Returns a numpy array (BGR, OpenCV) or None if not found.
    """
    fname = f"{base_name}_page{page_no}_diagram.png"
    path = os.path.join(diagram_root, fname)
    if not os.path.exists(path):
        return None
    img = cv2.imread(path)
    return img


# ---------- Model wrappers ----------

class TextSimilarityModel:
    """
    Wrapper around Sentence-BERT for semantic similarity.
    """

    def __init__(self, device: str = "cpu"):
        self.device = device
        model_source = resolve_model_source("sentence-transformers/all-MiniLM-L6-v2")
        self.model = SentenceTransformer(model_source, device=device)

    def similarity(self, text_a: str, text_b: str) -> float:
        if not text_a.strip() or not text_b.strip():
            return 0.0
        emb1 = self.model.encode(text_a, convert_to_tensor=True)
        emb2 = self.model.encode(text_b, convert_to_tensor=True)
        sim = util.cos_sim(emb1, emb2).item()  # [-1, 1]
        # Clamp to [0, 1]
        sim = max(0.0, min(1.0, sim))
        return sim


class DiagramSimilarityModel:
    """
    Wrapper around CLIP for diagram similarity.
    """

    def __init__(self, device: str = "cpu"):
        self.device = device
        model_source = resolve_model_source("openai/clip-vit-base-patch32")
        local_only = os.path.isdir(model_source)
        self.processor = CLIPProcessor.from_pretrained(
            model_source,
            local_files_only=local_only,
        )
        self.model = CLIPModel.from_pretrained(
            model_source,
            local_files_only=local_only,
        ).to(device)

    def similarity(self, img_a: np.ndarray, img_b: np.ndarray) -> float:
        # Convert BGR (OpenCV) -> RGB
        img_a_rgb = cv2.cvtColor(img_a, cv2.COLOR_BGR2RGB)
        img_b_rgb = cv2.cvtColor(img_b, cv2.COLOR_BGR2RGB)

        inputs = self.processor(
            images=[img_a_rgb, img_b_rgb], return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            feats = self.model.get_image_features(**inputs)

        # Normalize feature vectors
        feats = feats / feats.norm(dim=-1, keepdim=True)

        # cosine similarity between the two feature vectors (batch of 1)
        sim = torch.nn.functional.cosine_similarity(
            feats[0].unsqueeze(0), feats[1].unsqueeze(0)
        ).item()

        sim = max(0.0, min(1.0, sim))
        return sim


# ---------- Scoring curve helpers ----------

def map_text_similarity_to_fraction(sim: float) -> float:
    """
    Map raw cosine similarity [0,1] into a stricter "score fraction" [0,1].

    - <= 0.7  -> 0
    - 0.7..1.0 -> linear from 0 to 1
    """
    # if sim <= 0.7:
    #     return 0.0
    # return min(1.0, (sim - 0.7) / 0.3)

    # #more strict 
    # if sim <= 0.8:
    #     return 0.0
    # return min(1.0, (sim - 0.8) / 0.2)
    #more Lenient
    if sim <= 0.6:
        return 0.0
    return min(1.0, (sim - 0.6) / 0.4)




def map_diagram_similarity_to_fraction(sim: float) -> float:
    """
    For diagrams we can be slightly more lenient:
    keep it mostly linear but clip to [0,1].
    """
    # sim = max(0.0, min(1.0, sim))
    # return sim
# #more strict
#     if sim <= 0.6:
#         return 0.0
#     return (sim - 0.6) / 0.4
#more lenient
    return min(1.0, sim * 1.2)


def map_formula_similarity_to_fraction(sim: float) -> float:
    """
    Formula similarity is already normalized to [0, 1].
    Keep it direct so mathematically equivalent expressions can receive full marks.
    """
    return max(0.0, min(1.0, sim))




# ---------- Core evaluator ----------

@dataclass
class QuestionResult:
    question_id: int
    text_similarity: float
    diagram_similarity: Optional[float]
    formula_similarity: Optional[float]
    text_contribution: float   # marks from text
    diagram_contribution: float  # marks from diagram
    formula_contribution: float  # marks from formulas
    score: float
    max_marks: float
    feedback: str


class Evaluator:
    def __init__(self, config: EvalConfig):
        self.config = config
        self.text_model = TextSimilarityModel(device=config.device)
        self.diagram_model = DiagramSimilarityModel(device=config.device)
        self.rubric = load_rubric(config.rubric_path)

    def _get_rubric_for_question(self, qid: int) -> Dict[str, Any]:
        key = str(qid)
        if key not in self.rubric:
            raise KeyError(f"Question id {qid} not found in rubric.")
        return self.rubric[key]

    def evaluate_question(
        self,
        qid: int,
        ideal_text: str,
        student_text: str,
        ideal_diagram: Optional[np.ndarray],
        student_diagram: Optional[np.ndarray],
        ideal_formulas: List[Dict[str, Any]],
        student_formulas: List[Dict[str, Any]],
    ) -> QuestionResult:
        rub = self._get_rubric_for_question(qid)
        max_marks = float(rub.get("max_marks", 10))
        text_w = float(rub.get("text_weight", 0.7))
        diagram_w = float(rub.get("diagram_weight", 0.3))
        formula_w = float(rub.get("formula_weight", 0.0))
        # IMPORTANT: default is True -> missing diagram is a penalty
        penalize_missing_diagram = bool(rub.get("penalize_missing_diagram", True))
        penalize_missing_formula = bool(rub.get("penalize_missing_formula", True))

        # 1. text similarity
        raw_text_sim = self.text_model.similarity(ideal_text, student_text)
        text_sim_frac = map_text_similarity_to_fraction(raw_text_sim)

        # 2. diagram similarity + handling missing diagrams
        raw_diag_sim: Optional[float] = None

        # if there is no diagram in the ideal, ignore diagram weight entirely
        if ideal_diagram is None:
            diagram_w = 0.0
        else:
            # ideal has a diagram
            if student_diagram is not None:
                # both have diagrams -> compare normally
                raw_diag_sim = self.diagram_model.similarity(ideal_diagram, student_diagram)
            else:
                # student did NOT draw the diagram
                if penalize_missing_diagram:
                    # HARD penalty: keep diagram weight but similarity=0
                    raw_diag_sim = 0.0
                else:
                    # SOFT behaviour: ignore diagram weight
                    diagram_w = 0.0
                    raw_diag_sim = None

        # Map diagram sim through curve if present
        if raw_diag_sim is not None:
            diag_sim_frac = map_diagram_similarity_to_fraction(raw_diag_sim)
        else:
            diag_sim_frac = None

        # 3. formula similarity
        raw_formula_sim: Optional[float] = None
        formula_feedback = ""

        if not ideal_formulas:
            formula_w = 0.0
        else:
            if student_formulas:
                raw_formula_sim, formula_feedback = score_formula_sets(
                    ideal_formulas,
                    student_formulas,
                )
            else:
                if penalize_missing_formula:
                    raw_formula_sim = 0.0
                    formula_feedback = (
                        "Reference formula detected, but the student formula is missing."
                    )
                else:
                    formula_w = 0.0
                    raw_formula_sim = None
                    formula_feedback = (
                        "Formula marks were ignored because the student formula is missing."
                    )

        if raw_formula_sim is not None:
            formula_sim_frac = map_formula_similarity_to_fraction(raw_formula_sim)
        else:
            formula_sim_frac = None

        # normalize weights if needed
        total_w = text_w + diagram_w + formula_w
        if total_w <= 0:
            text_w = 1.0
            diagram_w = 0.0
            formula_w = 0.0
            total_w = 1.0

        text_w_norm = text_w / total_w
        diagram_w_norm = diagram_w / total_w
        formula_w_norm = formula_w / total_w

        # contributions (fractions)
        text_fraction = text_sim_frac * text_w_norm
        diagram_fraction = (diag_sim_frac if diag_sim_frac is not None else 0.0) * diagram_w_norm
        formula_fraction = (formula_sim_frac if formula_sim_frac is not None else 0.0) * formula_w_norm

        overall_fraction = text_fraction + diagram_fraction + formula_fraction
        score = overall_fraction * max_marks

        text_contrib_marks = text_fraction * max_marks
        diagram_contrib_marks = diagram_fraction * max_marks
        formula_contrib_marks = formula_fraction * max_marks

        # ----- feedback -----
        feedback_parts: List[str] = []
        if raw_text_sim > 0.85:
            feedback_parts.append("Text answer is very close to the ideal solution.")
        elif raw_text_sim > 0.6:
            feedback_parts.append("Text answer covers most key points but misses some details.")
        elif raw_text_sim > 0.4:
            feedback_parts.append("Text answer is partially correct but misses several key ideas.")
        else:
            feedback_parts.append("Text answer is mostly incorrect or incomplete.")

        if diagram_w > 0:
            if diag_sim_frac is None:
                feedback_parts.append("Diagram was not considered for this question.")
            elif raw_diag_sim is not None and raw_diag_sim > 0.8:
                feedback_parts.append("Diagram closely matches the ideal structure and labels.")
            elif raw_diag_sim is not None and raw_diag_sim > 0.5:
                feedback_parts.append("Diagram is roughly correct but has structural or labeling issues.")
            else:
                feedback_parts.append("Diagram is largely incorrect or missing important parts.")
        else:
            if ideal_diagram is not None and student_diagram is None and penalize_missing_diagram:
                feedback_parts.append("Diagram is missing; marks are heavily reduced for this question.")
            elif ideal_diagram is not None and student_diagram is None:
                feedback_parts.append("Diagram is missing; marks are based on text only.")

        if formula_w > 0:
            if formula_sim_frac is None:
                feedback_parts.append("Formula was not considered for this question.")
            elif raw_formula_sim is not None and raw_formula_sim > 0.85:
                feedback_parts.append("Formula is mathematically correct or equivalent to the ideal.")
            elif raw_formula_sim is not None and raw_formula_sim > 0.55:
                feedback_parts.append("Formula is partly correct but differs in some symbols or terms.")
            else:
                feedback_parts.append("Formula is incorrect, incomplete, or missing key terms.")
        elif formula_feedback:
            feedback_parts.append(formula_feedback)

        feedback = " ".join(feedback_parts)

        return QuestionResult(
            question_id=qid,
            text_similarity=raw_text_sim,
            diagram_similarity=raw_diag_sim,
            formula_similarity=raw_formula_sim,
            text_contribution=text_contrib_marks,
            diagram_contribution=diagram_contrib_marks,
            formula_contribution=formula_contrib_marks,
            score=score,
            max_marks=max_marks,
            feedback=feedback,
        )

    def evaluate_student(
        self,
        ideal_pdf_path: str,
        student_pdf_path: str,
    ) -> Dict[str, Any]:
        """
        Evaluate one student answer sheet against the ideal.

        Returns a dict:
        {
          "student_base": "...",
          "total_score": ...,
          "max_total": ...,
          "percentage": ...,
          "questions": [ { per-question result }, ... ]
        }
        """
        ideal_base = base_name_from_pdf(ideal_pdf_path)
        student_base = base_name_from_pdf(student_pdf_path)

        ideal_ocr = load_ocr_pages(ideal_base, self.config.ocr_root)
        known_qids = sorted(int(qid) for qid in self.rubric.keys())
        ideal_answers = build_question_answer_map(
            ideal_base,
            self.config.ocr_root,
            known_qids,
            allow_loose_numeric_markers=False,
        )
        student_answers = build_question_answer_map(
            student_base,
            self.config.ocr_root,
            known_qids,
        )

        results: List[Dict[str, Any]] = []
        total_score = 0.0
        max_total = 0.0

        for qid in known_qids:
            ideal_answer = ideal_answers.get(qid)
            ideal_page_data = ideal_ocr.get(qid, {})
            student_answer = student_answers.get(qid)
            ideal_text = (ideal_answer or {}).get("text") or ideal_page_data.get("text", "")
            if not student_answer or not student_answer.get("text", "").strip():
                rub = self._get_rubric_for_question(qid)
                max_marks = float(rub.get("max_marks", 10))
                max_total += max_marks
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

            student_text = student_answer.get("text", "")

            ideal_asset_page = (
                int(ideal_answer.get("primary_page"))
                if ideal_answer and ideal_answer.get("primary_page") and not ideal_answer.get("shared_page", False)
                else (qid if qid in ideal_ocr else None)
            )
            ideal_diag_img = (
                load_diagram_image(ideal_base, ideal_asset_page, self.config.diagram_root)
                if ideal_asset_page is not None
                else None
            )
            student_asset_page = (
                int(student_answer.get("primary_page"))
                if student_answer.get("primary_page") and not student_answer.get("shared_page", False)
                else None
            )
            student_diag_img = (
                load_diagram_image(student_base, student_asset_page, self.config.diagram_root)
                if student_asset_page is not None
                else None
            )
            ideal_formulas = (
                load_formula_page(ideal_base, ideal_asset_page, self.config.formula_root)
                if ideal_asset_page is not None
                else []
            )
            student_formulas = (
                load_formula_page(student_base, student_asset_page, self.config.formula_root)
                if student_asset_page is not None
                else []
            )

            qres = self.evaluate_question(
                qid,
                ideal_text,
                student_text,
                ideal_diag_img,
                student_diag_img,
                ideal_formulas,
                student_formulas,
            )

            total_score += qres.score
            max_total += qres.max_marks

            results.append(
                {
                    "question_id": qres.question_id,
                    "score": qres.score,
                    "max_marks": qres.max_marks,
                    "text_similarity": qres.text_similarity,
                    "diagram_similarity": qres.diagram_similarity,
                    "formula_similarity": qres.formula_similarity,
                    "feedback": qres.feedback,
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


# ---------- CLI: evaluate ALL students ----------

if __name__ == "__main__":
    """
    CLI usage:

        python -m src.evaluation_core

    This will:
      - Evaluate every student PDF in data/students/
      - Against the single ideal PDF: data/ideal/Ideal Answer Sheet.pdf
      - Print summaries
      - Save JSON under results/eval/<Student_X>_eval.json
    """
    ideal_pdf = os.path.join("data", "ideal", "Ideal Answer Sheet.pdf")
    students_dir = os.path.join("data", "students")

    cfg = EvalConfig(
        ocr_root="results/ocr",
        diagram_root="results/diagrams",
        formula_root="results/formulas",
        rubric_path="rubric.json",
    )

    evaluator = Evaluator(cfg)

    os.makedirs("results/eval", exist_ok=True)

    if not os.path.exists(ideal_pdf):
        print(f"[ERROR] Ideal PDF not found at {ideal_pdf}")
        raise SystemExit(1)

    if not os.path.isdir(students_dir):
        print(f"[ERROR] Students directory not found: {students_dir}")
        raise SystemExit(1)

    for fname in sorted(os.listdir(students_dir)):
        if not fname.lower().endswith(".pdf"):
            continue

        student_pdf = os.path.join(students_dir, fname)
        print("\n==============================")
        print(f"Evaluating student file: {fname}")
        print("==============================")

        result = evaluator.evaluate_student(ideal_pdf, student_pdf)

        # Print quick summary
        print("=== Evaluation Summary ===")
        print(f"Student: {result['student_base']}")
        print(
            f"Total: {result['total_score']:.2f} / {result['max_total']:.2f} "
            f"({result['percentage']:.2f}%)"
        )

        for q in result["questions"]:
            print(f"\nQ{q['question_id']}: {q['score']:.2f}/{q['max_marks']}")
            print(f"  Text similarity: {q['text_similarity']:.3f}")
            print(f"  Diagram similarity: {q['diagram_similarity']}")
            print(f"  Formula similarity: {q.get('formula_similarity')}")
            print(f"  Feedback: {q['feedback']}")

        # Save JSON per student
        json_path = os.path.join("results", "eval", f"{result['student_base']}_eval.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n[INFO] Saved evaluation JSON to {json_path}")
