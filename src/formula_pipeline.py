"""
Step 2.5: Formula Extraction + OCR

- Uses OCR blocks to locate likely math/formula lines on each page
- Crops those regions from the original page image
- Runs pix2tex to convert each crop into LaTeX
- Saves page-wise JSON under results/formulas/
"""

import json
import importlib
import os
import re
import warnings
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

os.environ.setdefault("NO_ALBUMENTATIONS_UPDATE", "1")

warnings.filterwarnings(
    "ignore",
    message=r".*Pydantic serializer warnings.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*slow image processor.*",
    category=UserWarning,
)

from pdf2image import convert_from_path
from PIL import Image


@dataclass
class FormulaConfig:
    dpi: int = 300
    poppler_path: Optional[str] = None
    ocr_root: str = "results/ocr"
    output_root: str = "results/formulas"
    crop_root: str = "results/formula_crops"
    line_merge_tolerance_px: int = 20
    padding_px: int = 18
    min_crop_width_px: int = 36
    min_crop_height_px: int = 20
    max_formula_lines_per_page: int = 2
    max_candidate_pages: int = 3
    min_formula_line_score: int = 6
    min_weak_formula_line_score: int = 5
    min_rubric_symbol_hits: int = 8


@dataclass
class FormulaDetectionResult:
    needs_formula: bool
    candidate_pages: Optional[List[int]]
    reason: str
    rubric_hint: bool = False


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _load_pix2tex_class():
    try:
        cli_module = importlib.import_module("pix2tex.cli")
        return getattr(cli_module, "LatexOCR", None)
    except ImportError:
        return None


def _require_pix2tex():
    latex_ocr_class = _load_pix2tex_class()
    if latex_ocr_class is None:
        raise RuntimeError(
            "pix2tex is not installed. Install it before running formula-aware evaluation."
        )
    return latex_ocr_class


def build_formula_reader():
    latex_ocr_class = _require_pix2tex()
    return latex_ocr_class()


def cleanup_formula_outputs(pdf_path: str, config: FormulaConfig) -> None:
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    for root in (config.output_root, config.crop_root):
        if not os.path.isdir(root):
            continue

        prefix = f"{base_name}_page"
        for fname in os.listdir(root):
            if fname.startswith(prefix):
                os.remove(os.path.join(root, fname))


def pdf_to_images(pdf_path: str, config: FormulaConfig):
    return convert_from_path(
        pdf_path,
        dpi=config.dpi,
        poppler_path=config.poppler_path,
        use_pdftocairo=True,
        thread_count=max(1, min(4, (os.cpu_count() or 1))),
    )


def _load_ocr_page(base_name: str, page_no: int, ocr_root: str) -> Dict[str, Any]:
    path = os.path.join(ocr_root, f"{base_name}_page{page_no}.json")
    if not os.path.exists(path):
        return {"page": page_no, "text": "", "blocks": []}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _bbox_to_rect(bbox: List[List[float]]) -> Optional[Tuple[int, int, int, int]]:
    if not bbox:
        return None

    xs = [float(point[0]) for point in bbox]
    ys = [float(point[1]) for point in bbox]
    x1 = int(max(0, min(xs)))
    y1 = int(max(0, min(ys)))
    x2 = int(max(xs))
    y2 = int(max(ys))
    if x2 <= x1 or y2 <= y1:
        return None
    return (x1, y1, x2, y2)


def _normalize_inline_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


FORMULA_KEYWORD_PATTERN = re.compile(
    r"\b(?:formula|equation|solve|derive|derivative|integral|differentiate|simplify|"
    r"matrix|vector|theorem|proof|algebra|geometry|trigonometry|probability|"
    r"statistics|quadratic|polynomial|fraction|ratio|mean|median|variance|"
    r"sin|cos|tan|cot|sec|cosec|log|ln|sqrt|theta|alpha|beta|gamma|delta|sigma|pi)\b",
    re.IGNORECASE,
)
FORMULA_SYMBOL_PATTERN = re.compile(r"[=+\-*/^<>\u2211\u222b\u221a\u2248\u2264\u2265\u00b1\u00d7\u00f7]")


def _iter_string_fragments(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
        return

    if isinstance(value, dict):
        for item in value.values():
            yield from _iter_string_fragments(item)
        return

    if isinstance(value, list):
        for item in value:
            yield from _iter_string_fragments(item)


def rubric_suggests_formula_work(rubric_dict: Optional[Dict[str, Any]]) -> bool:
    if not rubric_dict:
        return False

    if isinstance(rubric_dict, dict):
        for item in rubric_dict.values():
            if not isinstance(item, dict):
                continue
            try:
                if float(item.get("formula_weight", 0.0) or 0.0) > 0:
                    return True
            except (TypeError, ValueError):
                continue

    for fragment in _iter_string_fragments(rubric_dict):
        normalized = _normalize_inline_text(fragment)
        if not normalized:
            continue
        if FORMULA_KEYWORD_PATTERN.search(normalized):
            return True
        if len(FORMULA_SYMBOL_PATTERN.findall(normalized)) >= 2:
            return True
    return False


def _formula_signal_score(text: str) -> int:
    text = _normalize_inline_text(text)
    if not text:
        return 0

    compact = text.replace(" ", "")
    score = 0
    operator_hits = len(re.findall(r"[=+*/^<>]", compact))
    minus_hits = len(re.findall(r"(?<=\w)-(?=\w)|(?<=\d)-(?=\d)", compact))
    unicode_hits = len(FORMULA_SYMBOL_PATTERN.findall(text))
    digit_hits = len(re.findall(r"\d", compact))
    alpha_hits = len(re.findall(r"[A-Za-z]", compact))

    if FORMULA_KEYWORD_PATTERN.search(text):
        score += 4
    if re.search(r"[A-Za-z]\s*=\s*[A-Za-z0-9]", text):
        score += 4
    if re.search(r"\d+\s*/\s*\d+|\b\d+(?:\.\d+)?\s*[xX*]\s*\d+(?:\.\d+)?", text):
        score += 4
    if re.search(
        r"\b(?:sin|cos|tan|cot|sec|cosec|log|ln|lim|sqrt|theta|alpha|beta|gamma|delta|sigma|lambda|pi|dx|dy)\b",
        text,
        re.IGNORECASE,
    ):
        score += 4

    score += min(operator_hits + minus_hits, 4)
    score += min(unicode_hits * 2, 4)

    if digit_hits >= 2 and operator_hits + minus_hits >= 1:
        score += 2
    if digit_hits >= 1 and alpha_hits >= 1 and operator_hits + minus_hits >= 1:
        score += 2

    return score


def _looks_formula_like(text: str) -> bool:
    text = _normalize_inline_text(text)
    if not text:
        return False

    compact = text.replace(" ", "")
    if len(compact) < 2:
        return False

    if _formula_signal_score(text) >= 4:
        return True

    if re.search(
        r"(?:\b[a-z]{1,3}\b|\d+(?:\.\d+)?|\([^)]+\))\s*[+*^]\s*(?:\b[a-z]{1,3}\b|\d+(?:\.\d+)?|\([^)]+\))",
        text,
        re.IGNORECASE,
    ):
        return True

    if re.search(
        r"(?:\d+(?:\.\d+)?|\([^)]+\)|\b[a-z]{1,3}\b)\s*/\s*(?:\d+(?:\.\d+)?|\([^)]+\)|\b[a-z]{1,3}\b)",
        text,
        re.IGNORECASE,
    ):
        return True

    signal_chars = re.findall(r"[0-9=+*^/<>]", compact)
    if len(signal_chars) >= 3 and len(signal_chars) / max(len(compact), 1) >= 0.22:
        return True

    return False


def _group_blocks_into_lines(
    blocks: List[Dict[str, Any]],
    tolerance_px: int,
) -> List[List[Dict[str, Any]]]:
    enriched: List[Dict[str, Any]] = []
    for block in blocks:
        rect = _bbox_to_rect(block.get("bbox", []))
        if rect is None:
            continue
        x1, y1, x2, y2 = rect
        enriched.append(
            {
                "block": block,
                "rect": rect,
                "center_y": (y1 + y2) / 2.0,
                "height": max(1, y2 - y1),
            }
        )

    enriched.sort(key=lambda item: (item["center_y"], item["rect"][0]))

    lines: List[List[Dict[str, Any]]] = []
    for item in enriched:
        if not lines:
            lines.append([item])
            continue

        last_line = lines[-1]
        avg_center = sum(entry["center_y"] for entry in last_line) / len(last_line)
        avg_height = sum(entry["height"] for entry in last_line) / len(last_line)
        merge_tolerance = max(tolerance_px, int(avg_height * 0.6))

        if abs(item["center_y"] - avg_center) <= merge_tolerance:
            last_line.append(item)
        else:
            lines.append([item])

    for line in lines:
        line.sort(key=lambda item: item["rect"][0])
    return lines


def _page_formula_score(ocr_page: Dict[str, Any]) -> Tuple[int, int, int]:
    page_text = _normalize_inline_text(str(ocr_page.get("text", "")))
    blocks = list(ocr_page.get("blocks", []) or [])

    line_hits = 0
    symbol_hits = len(FORMULA_SYMBOL_PATTERN.findall(page_text))
    strongest_line_score = 0

    for line in _group_blocks_into_lines(blocks, tolerance_px=20):
        line_text = _normalize_inline_text(
            " ".join(str(item["block"].get("text", "")) for item in line)
        )
        line_score = _formula_signal_score(line_text)
        strongest_line_score = max(strongest_line_score, line_score)
        if _looks_formula_like(line_text):
            line_hits += 1

    if FORMULA_KEYWORD_PATTERN.search(page_text):
        line_hits += 1

    return line_hits, symbol_hits, strongest_line_score


def detect_formula_pages_for_pdf(
    pdf_path: str,
    config: FormulaConfig,
    rubric_dict: Optional[Dict[str, Any]] = None,
) -> FormulaDetectionResult:
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    rubric_hint = rubric_suggests_formula_work(rubric_dict)

    if rubric_dict is not None and not rubric_hint:
        return FormulaDetectionResult(
            needs_formula=False,
            candidate_pages=[],
            reason="Rubric does not allocate marks to formulas, so formula parsing is skipped.",
            rubric_hint=False,
        )

    strong_candidates: List[Tuple[int, int]] = []
    weak_candidates: List[Tuple[int, int]] = []
    known_pages: Set[int] = set()

    for entry in os.listdir(config.ocr_root) if os.path.isdir(config.ocr_root) else []:
        match = re.fullmatch(rf"{re.escape(base_name)}_page(\d+)\.json", entry)
        if not match:
            continue
        known_pages.add(int(match.group(1)))

    for page_no in sorted(known_pages):
        ocr_page = _load_ocr_page(base_name, page_no, config.ocr_root)
        line_hits, symbol_hits, strongest_line_score = _page_formula_score(ocr_page)
        if line_hits >= 1 and strongest_line_score >= config.min_formula_line_score:
            strong_candidates.append((page_no, strongest_line_score))
            continue

        if rubric_hint and symbol_hits >= config.min_rubric_symbol_hits:
            strong_candidates.append((page_no, max(strongest_line_score, config.min_formula_line_score)))
            continue

        if strongest_line_score >= config.min_weak_formula_line_score:
            weak_candidates.append((page_no, strongest_line_score))

    if strong_candidates:
        selected_pages = [
            page_no
            for page_no, _ in sorted(
                strong_candidates,
                key=lambda item: (-item[1], item[0]),
            )[: max(1, config.max_candidate_pages)]
        ]
        return FormulaDetectionResult(
            needs_formula=True,
            candidate_pages=selected_pages,
            reason=f"Detected strong formula cues on {len(selected_pages)} page(s).",
            rubric_hint=rubric_hint,
        )

    if rubric_hint and weak_candidates:
        selected_pages = [
            page_no
            for page_no, _ in sorted(
                weak_candidates,
                key=lambda item: (-item[1], item[0]),
            )[: max(1, config.max_candidate_pages)]
        ]
        return FormulaDetectionResult(
            needs_formula=True,
            candidate_pages=selected_pages,
            reason=f"Rubric suggests formulas; checking the {len(selected_pages)} page(s) with the strongest OCR math signals.",
            rubric_hint=True,
        )

    if rubric_hint and len(known_pages) <= 2 and known_pages:
        return FormulaDetectionResult(
            needs_formula=True,
            candidate_pages=sorted(known_pages),
            reason="Rubric indicates formula-heavy grading for a short document, so all pages will be checked.",
            rubric_hint=True,
        )

    return FormulaDetectionResult(
        needs_formula=False,
        candidate_pages=[],
        reason="No formula cues were detected strongly enough in OCR text to justify formula parsing.",
        rubric_hint=rubric_hint,
    )


def _line_bbox(line: List[Dict[str, Any]]) -> Tuple[int, int, int, int]:
    x1 = min(item["rect"][0] for item in line)
    y1 = min(item["rect"][1] for item in line)
    x2 = max(item["rect"][2] for item in line)
    y2 = max(item["rect"][3] for item in line)
    return (x1, y1, x2, y2)


def _crop_with_padding(
    pil_img: Image.Image,
    rect: Tuple[int, int, int, int],
    padding_px: int,
) -> Image.Image:
    x1, y1, x2, y2 = rect
    width, height = pil_img.size
    crop_box = (
        max(0, x1 - padding_px),
        max(0, y1 - padding_px),
        min(width, x2 + padding_px),
        min(height, y2 + padding_px),
    )
    return pil_img.crop(crop_box)


def _save_formula_page(
    pdf_path: str,
    page_no: int,
    formulas: List[Dict[str, Any]],
    config: FormulaConfig,
) -> str:
    ensure_dir(config.output_root)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    out_path = os.path.join(config.output_root, f"{base_name}_page{page_no}_formulas.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "page": page_no,
                "formula_count": len(formulas),
                "formulas": formulas,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    return out_path


def extract_formulas_for_pdf(
    pdf_path: str,
    config: FormulaConfig,
    formula_reader=None,
    candidate_pages: Optional[List[int]] = None,
    images: Optional[List[Image.Image]] = None,
) -> Dict[int, str]:
    if formula_reader is None:
        formula_reader = build_formula_reader()

    cleanup_formula_outputs(pdf_path, config)
    ensure_dir(config.crop_root)
    ensure_dir(config.output_root)

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    selected_pages = set(candidate_pages or [])
    if candidate_pages is not None and not selected_pages:
        return {}

    page_images = images or pdf_to_images(pdf_path, config)
    page_outputs: Dict[int, str] = {}

    for page_no, pil_img in enumerate(page_images, start=1):
        if selected_pages and page_no not in selected_pages:
            continue

        ocr_page = _load_ocr_page(base_name, page_no, config.ocr_root)
        blocks = list(ocr_page.get("blocks", []) or [])
        lines = _group_blocks_into_lines(blocks, config.line_merge_tolerance_px)

        candidate_lines: List[Tuple[int, str, List[Dict[str, Any]]]] = []
        for line in lines:
            line_text = _normalize_inline_text(
                " ".join(str(item["block"].get("text", "")) for item in line)
            )
            if not _looks_formula_like(line_text):
                continue
            signal_score = _formula_signal_score(line_text)
            if signal_score <= 0:
                continue
            candidate_lines.append((signal_score, line_text, line))

        candidate_lines.sort(key=lambda item: (-item[0], _line_bbox(item[2])[1], _line_bbox(item[2])[0]))

        formulas: List[Dict[str, Any]] = []
        for formula_index, (_, line_text, line) in enumerate(
            candidate_lines[: config.max_formula_lines_per_page],
            start=1,
        ):
            rect = _line_bbox(line)
            crop = _crop_with_padding(pil_img, rect, config.padding_px)
            crop_w, crop_h = crop.size
            if crop_w < config.min_crop_width_px or crop_h < config.min_crop_height_px:
                continue

            crop_name = f"{base_name}_page{page_no}_formula{formula_index}.png"
            crop_path = os.path.join(config.crop_root, crop_name)
            crop.save(crop_path)

            latex = ""
            error = ""
            try:
                latex = str(formula_reader(crop)).strip()
            except Exception as exc:
                error = str(exc)

            formulas.append(
                {
                    "index": len(formulas) + 1,
                    "bbox": [rect[0], rect[1], rect[2], rect[3]],
                    "ocr_text": line_text,
                    "latex": latex,
                    "crop_path": crop_path,
                    "error": error,
                }
            )

        page_outputs[page_no] = _save_formula_page(pdf_path, page_no, formulas, config)

    return page_outputs


if __name__ == "__main__":
    POPPLER_BIN = r"C:\poppler-24.02.0\Library\bin"

    cfg = FormulaConfig(
        dpi=300,
        poppler_path=POPPLER_BIN,
        ocr_root="results/ocr",
        output_root="results/formulas",
        crop_root="results/formula_crops",
    )

    reader = build_formula_reader()

    ideal_dir = os.path.join("data", "ideal")
    if os.path.isdir(ideal_dir):
        for fname in os.listdir(ideal_dir):
            if fname.lower().endswith(".pdf"):
                extract_formulas_for_pdf(os.path.join(ideal_dir, fname), cfg, reader)

    students_dir = os.path.join("data", "students")
    if os.path.isdir(students_dir):
        for fname in os.listdir(students_dir):
            if fname.lower().endswith(".pdf"):
                extract_formulas_for_pdf(os.path.join(students_dir, fname), cfg, reader)
