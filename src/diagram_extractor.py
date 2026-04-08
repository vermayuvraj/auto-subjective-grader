"""
Step 2: Diagram Extraction (Connected Components based)

- Converts each PDF page to an image
- Detects all non-white "ink" pixels
- Runs connected components to find visual blocks
- Filters out small components (text) and keeps only large ones in the lower
  half of the page (where your diagrams live)
- Unions these components and crops a tight diagram region
- Saves diagrams as PNG under results/diagrams/
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
import cv2
from pdf2image import convert_from_path


# ---------- Config dataclass ----------

@dataclass
class DiagramConfig:
    dpi: int = 300
    poppler_path: Optional[str] = None   # e.g. r"C:\poppler-24.02.0\Library\bin"
    output_root: str = "results/diagrams"
    # tuning params
    min_area_ratio: float = 0.003       # 0.3% of page area -> ignore tiny text blobs
    min_center_y_ratio: float = 0.45    # only keep components whose centerY > 45% of page height


# ---------- Utility functions ----------

def ensure_dir(path: str) -> None:
    """Create directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


def pdf_to_images(pdf_path: str, config: DiagramConfig):
    """
    Convert a PDF into a list of PIL images (one per page).
    """
    images = convert_from_path(
        pdf_path,
        dpi=config.dpi,
        poppler_path=config.poppler_path,
    )
    return images


# ---------- Core: CC-based diagram extraction ----------

def extract_diagram_from_page_cc(
    pil_img,
    config: DiagramConfig,
):
    """
    Extract diagram using connected components:

    1. Convert to grayscale.
    2. Threshold to get "ink" (non-white) pixels.
    3. Run connectedComponentsWithStats.
    4. Keep only components with:
         - area > min_area_ratio * page_area
         - center_y > min_center_y_ratio * page_height
    5. Take union of their bounding boxes and crop from original image.
    """
    # PIL -> numpy -> BGR
    img_rgb = np.array(pil_img)
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape[:2]
    page_area = h * w

    # 1. Threshold: anything slightly darker than near-white is "ink"
    _, ink_mask = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY_INV)

    # 2. Slightly close gaps so diagram strokes connect more
    kernel = np.ones((3, 3), np.uint8)
    ink_mask = cv2.morphologyEx(ink_mask, cv2.MORPH_CLOSE, kernel, iterations=1)

    # 3. Connected components on ink
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        ink_mask, connectivity=8
    )

    # 4. Filter components
    min_area = config.min_area_ratio * page_area
    min_center_y = config.min_center_y_ratio * h

    kept_boxes = []

    for label in range(1, num_labels):  # label 0 is background
        x, y, w2, h2, area = stats[label]
        cx, cy = centroids[label]

        if area < min_area:
            continue  # too small -> likely text/noise

        if cy < min_center_y:
            continue  # in upper half -> likely header/paragraphs

        kept_boxes.append((x, y, w2, h2))

    if not kept_boxes:
        # Fallback: maybe diagram is higher; pick the largest component by area
        max_label = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1  # skip background
        x, y, w2, h2, area = stats[max_label]
        if area < min_area:
            return None
        kept_boxes = [(x, y, w2, h2)]

    # 5. Union of kept boxes
    x_min = min(b[0] for b in kept_boxes)
    y_min = min(b[1] for b in kept_boxes)
    x_max = max(b[0] + b[2] for b in kept_boxes)
    y_max = max(b[1] + b[3] for b in kept_boxes)

    # Clamp to image bounds
    x_min = max(0, x_min)
    y_min = max(0, y_min)
    x_max = min(w, x_max)
    y_max = min(h, y_max)

    if x_max <= x_min or y_max <= y_min:
        return None

    diagram = img_bgr[y_min:y_max, x_min:x_max]
    return diagram


def save_diagram_image(diagram_img, pdf_path: str, page_no: int, config: DiagramConfig) -> str:
    """
    Save a diagram image as PNG under results/diagrams/.
    """
    ensure_dir(config.output_root)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    out_path = os.path.join(config.output_root, f"{base_name}_page{page_no}_diagram.png")
    cv2.imwrite(out_path, diagram_img)
    print(f"[DIAGRAM] Saved: {out_path}")
    return out_path


def extract_diagrams_for_pdf(pdf_path: str, config: DiagramConfig):
    """
    Extract and save diagrams for each page of a single PDF.
    """
    print(f"[DIAGRAM] Processing PDF: {pdf_path}")

    images = pdf_to_images(pdf_path, config)

    diagram_paths: Dict[int, Optional[str]] = {}

    for page_no, pil_img in enumerate(images, start=1):
        diagram_img = extract_diagram_from_page_cc(pil_img, config)

        if diagram_img is None:
            print(f"[DIAGRAM] No diagram found for page {page_no}.")
            diagram_paths[page_no] = None
        else:
            out_path = save_diagram_image(diagram_img, pdf_path, page_no, config)
            diagram_paths[page_no] = out_path

    print(f"[DIAGRAM] Completed: {pdf_path}")
    return diagram_paths


# ---------- CLI: process ALL ideal + student PDFs ----------

if __name__ == "__main__":
    """
    Example usage:

        python -m src.diagram_extractor

    This will:
      - Look in data/ideal/ for all *.pdf (including Ideal Answer Sheet.pdf)
      - Look in data/students/ for all *.pdf
      - Extract diagrams for every page of each PDF
      - Save them in results/diagrams/
    """
    POPPLER_BIN = r"C:\poppler-24.02.0\Library\bin"

    cfg = DiagramConfig(
        dpi=300,
        poppler_path=POPPLER_BIN,
        output_root="results/diagrams",
        min_area_ratio=0.003,
        min_center_y_ratio=0.45,
    )

    # Process all ideal PDFs
    ideal_dir = os.path.join("data", "ideal")
    if os.path.isdir(ideal_dir):
        for fname in os.listdir(ideal_dir):
            if fname.lower().endswith(".pdf"):
                pdf_path = os.path.join(ideal_dir, fname)
                extract_diagrams_for_pdf(pdf_path, cfg)
    else:
        print(f"[WARN] Ideal dir not found: {ideal_dir}")

    # Process all student PDFs
    students_dir = os.path.join("data", "students")
    if os.path.isdir(students_dir):
        for fname in os.listdir(students_dir):
            if fname.lower().endswith(".pdf"):
                pdf_path = os.path.join(students_dir, fname)
                extract_diagrams_for_pdf(pdf_path, cfg)
    else:
        print(f"[WARN] Students dir not found: {students_dir}")
