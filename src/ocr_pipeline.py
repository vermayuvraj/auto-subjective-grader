"""
Step 1: OCR Pipeline

Supports two OCR backends:
- EasyOCR for the existing local flow
- Google Document AI for handwritten answer sheets

Both backends save OCR results as JSON in results/ocr/:

    <BaseName>_page1.json
    <BaseName>_page2.json
    ...
"""

import json
import os
from io import BytesIO
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
from pdf2image import convert_from_path
from PIL import Image

try:
    from google.api_core.client_options import ClientOptions
    from google.cloud import documentai
except ImportError:  # optional until handwritten mode is used
    ClientOptions = None
    documentai = None

try:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential
except ImportError:  # optional until handwritten mode is used
    DocumentIntelligenceClient = None
    AzureKeyCredential = None


@dataclass
class OCRConfig:
    dpi: int = 300
    poppler_path: Optional[str] = None
    languages: List[str] = None
    use_gpu: bool = True
    output_root: str = "results/ocr"
    backend: str = "easyocr"
    document_ai_project_id: Optional[str] = None
    document_ai_location: str = "us"
    document_ai_processor_id: Optional[str] = None
    azure_document_intelligence_endpoint: Optional[str] = None
    azure_document_intelligence_key: Optional[str] = None


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def cleanup_ocr_outputs(pdf_path: str, output_root: str) -> None:
    if not os.path.isdir(output_root):
        return

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    prefix = f"{base_name}_page"
    for fname in os.listdir(output_root):
        if fname.startswith(prefix) and fname.endswith(".json"):
            os.remove(os.path.join(output_root, fname))


def pdf_to_images(pdf_path: str, config: OCRConfig):
    print(f"[OCR] Converting PDF to images: {pdf_path}")
    images = convert_from_path(
        pdf_path,
        dpi=config.dpi,
        poppler_path=config.poppler_path,
    )
    print(f"[OCR] Converted to {len(images)} page image(s).")
    return images


def build_easyocr_reader(config: OCRConfig) -> Any:
    import easyocr

    return easyocr.Reader(config.languages, gpu=config.use_gpu)


def run_easyocr_on_page(pil_img, reader: Any) -> List[Dict[str, Any]]:
    img = np.array(pil_img)
    result = reader.readtext(img, detail=1, paragraph=False)

    blocks: List[Dict[str, Any]] = []
    for bbox, text, conf in result:
        blocks.append(
            {
                "bbox": [[float(x), float(y)] for (x, y) in bbox],
                "text": str(text),
                "confidence": float(conf),
            }
        )
    return blocks


def _require_document_ai() -> None:
    if documentai is None or ClientOptions is None:
        raise RuntimeError(
            "google-cloud-documentai is not installed. "
            "Install it before using handwritten OCR mode."
        )


def _text_from_anchor(full_text: str, text_anchor) -> str:
    if not text_anchor or not getattr(text_anchor, "text_segments", None):
        return ""

    chunks: List[str] = []
    for segment in text_anchor.text_segments:
        start_index = int(getattr(segment, "start_index", 0) or 0)
        end_index = int(segment.end_index)
        chunks.append(full_text[start_index:end_index])
    return "".join(chunks).strip()


def _bbox_from_layout(layout, page_width: float, page_height: float) -> List[List[float]]:
    poly = getattr(layout, "bounding_poly", None)
    if poly is None:
        return []

    vertices = list(getattr(poly, "vertices", []))
    if vertices:
        return [[float(v.x), float(v.y)] for v in vertices]

    norm_vertices = list(getattr(poly, "normalized_vertices", []))
    if norm_vertices:
        return [
            [float(v.x) * float(page_width), float(v.y) * float(page_height)]
            for v in norm_vertices
        ]

    return []


def _document_ai_blocks(document, page) -> List[Dict[str, Any]]:
    full_text = getattr(document, "text", "") or ""
    page_dim = getattr(page, "dimension", None)
    page_width = getattr(page_dim, "width", 0) or 0
    page_height = getattr(page_dim, "height", 0) or 0

    items = list(getattr(page, "lines", []))
    if not items:
        items = list(getattr(page, "tokens", []))

    blocks: List[Dict[str, Any]] = []
    for item in items:
        layout = getattr(item, "layout", None)
        if layout is None:
            continue

        text = _text_from_anchor(full_text, getattr(layout, "text_anchor", None))
        if not text:
            continue

        bbox = _bbox_from_layout(layout, page_width, page_height)
        if not bbox:
            continue

        blocks.append(
            {
                "bbox": bbox,
                "text": text,
                "confidence": float(getattr(layout, "confidence", 0.0) or 0.0),
            }
        )

    return blocks


def _require_azure_document_intelligence() -> None:
    if DocumentIntelligenceClient is None or AzureKeyCredential is None:
        raise RuntimeError(
            "azure-ai-documentintelligence is not installed. "
            "Install it before using handwritten OCR mode."
        )


def _azure_polygon_to_bbox(polygon) -> List[List[float]]:
    if not polygon:
        return []

    values = list(polygon)
    if len(values) < 8:
        return []

    points: List[List[float]] = []
    for idx in range(0, len(values), 2):
        points.append([float(values[idx]), float(values[idx + 1])])
    return points


def _azure_document_blocks(page) -> List[Dict[str, Any]]:
    items = list(getattr(page, "lines", []) or [])
    if not items:
        items = list(getattr(page, "words", []) or [])

    blocks: List[Dict[str, Any]] = []
    for item in items:
        text = getattr(item, "content", "") or ""
        if not text.strip():
            continue

        bbox = _azure_polygon_to_bbox(getattr(item, "polygon", None))
        if not bbox:
            continue

        blocks.append(
            {
                "bbox": bbox,
                "text": text.strip(),
                "confidence": float(getattr(item, "confidence", 0.0) or 0.0),
            }
        )

    return blocks


def _pil_image_to_azure_bytes(pil_img) -> bytes:
    """
    Encode a page image so it fits Azure F0 request limits.
    """
    max_bytes = 4 * 1024 * 1024
    work_img = pil_img.convert("RGB")

    for quality in (90, 80, 70, 60, 50):
        buffer = BytesIO()
        work_img.save(buffer, format="JPEG", quality=quality, optimize=True)
        data = buffer.getvalue()
        if len(data) <= max_bytes:
            return data

    for scale in (0.85, 0.7, 0.55, 0.4):
        resized = work_img.resize(
            (
                max(1, int(work_img.width * scale)),
                max(1, int(work_img.height * scale)),
            ),
            Image.Resampling.LANCZOS,
        )
        for quality in (75, 65, 55, 45):
            buffer = BytesIO()
            resized.save(buffer, format="JPEG", quality=quality, optimize=True)
            data = buffer.getvalue()
            if len(data) <= max_bytes:
                return data

    raise RuntimeError(
        "Azure OCR page image is still too large after compression. "
        "Try a lower DPI for handwritten OCR."
    )


def save_ocr_page(
    pdf_path: str,
    page_no: int,
    blocks: List[Dict[str, Any]],
    config: OCRConfig,
) -> str:
    ensure_dir(config.output_root)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    out_name = f"{base_name}_page{page_no}.json"
    out_path = os.path.join(config.output_root, out_name)

    full_text = "\n".join(b["text"] for b in blocks)
    page_obj = {
        "page": page_no,
        "text": full_text,
        "blocks": blocks,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(page_obj, f, ensure_ascii=False, indent=2)

    print(f"[OCR] Saved page {page_no} -> {out_path}")
    return out_path


def ocr_pdf_with_document_ai(pdf_path: str, config: OCRConfig) -> None:
    _require_document_ai()

    if not config.document_ai_project_id or not config.document_ai_processor_id:
        raise RuntimeError(
            "Document AI OCR requires project id and processor id."
        )

    location = config.document_ai_location or "us"
    client = documentai.DocumentProcessorServiceClient(
        client_options=ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    )
    processor_name = client.processor_path(
        config.document_ai_project_id,
        location,
        config.document_ai_processor_id,
    )

    with open(pdf_path, "rb") as f:
        raw_document = documentai.RawDocument(
            content=f.read(),
            mime_type="application/pdf",
        )

    request = documentai.ProcessRequest(
        name=processor_name,
        raw_document=raw_document,
        process_options=documentai.ProcessOptions(
            ocr_config=documentai.OcrConfig(
                enable_native_pdf_parsing=True,
                enable_image_quality_scores=True,
                hints=documentai.OcrConfig.Hints(
                    language_hints=config.languages or ["en"]
                ),
            )
        ),
    )

    print(f"[OCR] Processing PDF with Document AI: {pdf_path}")
    result = client.process_document(request=request)
    document = result.document

    for fallback_page_no, page in enumerate(document.pages, start=1):
        page_no = int(getattr(page, "page_number", fallback_page_no) or fallback_page_no)
        blocks = _document_ai_blocks(document, page)
        save_ocr_page(pdf_path, page_no, blocks, config)

    print(f"[OCR] Completed with Document AI: {pdf_path}")


def ocr_pdf_with_azure_document_intelligence(pdf_path: str, config: OCRConfig) -> None:
    _require_azure_document_intelligence()

    if not config.azure_document_intelligence_endpoint or not config.azure_document_intelligence_key:
        raise RuntimeError(
            "Azure handwritten OCR requires the Azure Document Intelligence endpoint and key."
        )

    client = DocumentIntelligenceClient(
        endpoint=config.azure_document_intelligence_endpoint,
        credential=AzureKeyCredential(config.azure_document_intelligence_key),
    )
    print(f"[OCR] Processing PDF with Azure Document Intelligence: {pdf_path}")

    if pdf_path.lower().endswith(".pdf"):
        images = pdf_to_images(pdf_path, config)
        for page_no, pil_img in enumerate(images, start=1):
            page_bytes = _pil_image_to_azure_bytes(pil_img)
            poller = client.begin_analyze_document(
                "prebuilt-read",
                body=page_bytes,
            )
            result = poller.result()
            page = result.pages[0] if result.pages else None
            blocks = _azure_document_blocks(page) if page is not None else []
            save_ocr_page(pdf_path, page_no, blocks, config)
    else:
        with open(pdf_path, "rb") as f:
            poller = client.begin_analyze_document(
                "prebuilt-read",
                body=f.read(),
            )
        result = poller.result()
        for fallback_page_no, page in enumerate(result.pages, start=1):
            page_no = int(getattr(page, "page_number", fallback_page_no) or fallback_page_no)
            blocks = _azure_document_blocks(page)
            save_ocr_page(pdf_path, page_no, blocks, config)

    print(f"[OCR] Completed with Azure Document Intelligence: {pdf_path}")


def ocr_pdf(pdf_path: str, config: OCRConfig, reader: Optional[Any]):
    cleanup_ocr_outputs(pdf_path, config.output_root)

    if config.backend == "documentai":
        ocr_pdf_with_document_ai(pdf_path, config)
        return
    if config.backend == "azure":
        ocr_pdf_with_azure_document_intelligence(pdf_path, config)
        return

    print(f"\n[OCR] Processing PDF: {pdf_path}")
    images = pdf_to_images(pdf_path, config)

    for page_no, pil_img in enumerate(images, start=1):
        blocks = run_easyocr_on_page(pil_img, reader)
        save_ocr_page(pdf_path, page_no, blocks, config)

    print(f"[OCR] Completed: {pdf_path}")


if __name__ == "__main__":
    POPPLER_BIN = r"C:\poppler-24.02.0\Library\bin"

    cfg = OCRConfig(
        dpi=300,
        poppler_path=POPPLER_BIN,
        languages=["en"],
        use_gpu=True,
        output_root="results/ocr",
        backend="easyocr",
    )

    ensure_dir(cfg.output_root)

    print(f"[OCR] Initialising EasyOCR reader (languages={cfg.languages}, gpu={cfg.use_gpu})...")
    reader = build_easyocr_reader(cfg)
    print("[OCR] EasyOCR reader ready.")

    ideal_dir = os.path.join("data", "ideal")
    if os.path.isdir(ideal_dir):
        for fname in sorted(os.listdir(ideal_dir)):
            if fname.lower().endswith(".pdf"):
                ocr_pdf(os.path.join(ideal_dir, fname), cfg, reader)
    else:
        print(f"[WARN] Ideal directory not found: {ideal_dir}")

    students_dir = os.path.join("data", "students")
    if os.path.isdir(students_dir):
        for fname in sorted(os.listdir(students_dir)):
            if fname.lower().endswith(".pdf"):
                ocr_pdf(os.path.join(students_dir, fname), cfg, reader)
    else:
        print(f"[WARN] Students directory not found: {students_dir}")
