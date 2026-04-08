"""
Step 2.5: Formula Extraction + OCR

- Uses OCR blocks to locate likely math/formula lines on each page
- Crops those regions from the original page image
- Runs pix2tex to convert each crop into LaTeX
- Saves page-wise JSON under results/formulas/
"""

import json
import os
import re
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

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

try:
    from pix2tex.cli import LatexOCR
except ImportError:  # optional until formula mode is used
    LatexOCR = None


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


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _require_pix2tex() -> None:
    if LatexOCR is None:
        raise RuntimeError(
            "pix2tex is not installed. Install it before running formula-aware evaluation."
        )


def build_formula_reader():
    _require_pix2tex()
    return LatexOCR()


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


def _looks_formula_like(text: str) -> bool:
    text = _normalize_inline_text(text)
    if not text:
        return False

    lowered = text.lower()
    compact = text.replace(" ", "")
    if len(compact) < 2:
        return False

    math_keywords = (
        "sin",
        "cos",
        "tan",
        "cot",
        "sec",
        "cosec",
        "log",
        "ln",
        "lim",
        "sqrt",
        "theta",
        "alpha",
        "beta",
        "gamma",
        "delta",
        "sigma",
        "lambda",
        "pi",
        "dx",
        "dy",
    )
    keyword_pattern = r"\b(?:sin|cos|tan|cot|sec|cosec|log|ln|lim|sqrt|theta|alpha|beta|gamma|delta|sigma|lambda|pi|dx|dy)\b"
    if re.search(keyword_pattern, lowered):
        return True

    if re.search(r"[A-Za-z]\s*\d|\d\s*[A-Za-z]", text) and re.search(r"[=+*^<>]", text):
        return True

    if re.search(r"[A-Za-z]\s*=\s*[A-Za-z0-9]", text):
        return True

    if re.search(r"(?:\b[a-z]{1,3}\b|\d+(?:\.\d+)?|\([^)]+\))\s*[+*^]\s*(?:\b[a-z]{1,3}\b|\d+(?:\.\d+)?|\([^)]+\))", text):
        return True

    if re.search(r"(?:\b[a-z]{1,3}\b|\d+(?:\.\d+)?|\([^)]+\))\s*-\s*(?:\b[a-z]{1,3}\b|\d+(?:\.\d+)?|\([^)]+\))", text):
        return True

    if re.search(r"\([A-Za-z0-9+\-*/^\s]+\)", text) and re.search(r"[=+*^]", text):
        return True

    if re.search(r"(?:\d+(?:\.\d+)?|\([^)]+\)|\b[a-z]{1,3}\b)\s*/\s*(?:\d+(?:\.\d+)?|\([^)]+\)|\b[a-z]{1,3}\b)", text):
        return True

    if re.search(r"[∑∫√∞≈≤≥±×÷]", text):
        return True

    signal_chars = re.findall(r"[0-9=+*^/<>]", compact)
    if len(signal_chars) >= 2 and len(signal_chars) / max(len(compact), 1) >= 0.18:
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
) -> Dict[int, str]:
    if formula_reader is None:
        formula_reader = build_formula_reader()

    cleanup_formula_outputs(pdf_path, config)
    ensure_dir(config.crop_root)
    ensure_dir(config.output_root)

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    images = pdf_to_images(pdf_path, config)
    page_outputs: Dict[int, str] = {}

    for page_no, pil_img in enumerate(images, start=1):
        ocr_page = _load_ocr_page(base_name, page_no, config.ocr_root)
        blocks = list(ocr_page.get("blocks", []) or [])
        lines = _group_blocks_into_lines(blocks, config.line_merge_tolerance_px)

        formulas: List[Dict[str, Any]] = []
        for formula_index, line in enumerate(lines, start=1):
            line_text = _normalize_inline_text(
                " ".join(str(item["block"].get("text", "")) for item in line)
            )
            if not _looks_formula_like(line_text):
                continue

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
