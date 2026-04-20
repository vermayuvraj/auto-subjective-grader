import base64
import json
import os
import sys
import time
import textwrap
from typing import Any, Callable, Dict, List, Optional

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import diagram_extractor
import evaluation_core
import formula_pipeline
import llm_evaluator
import ocr_pipeline
import pipeline_service
import report_generator
from google_cloud_auth import find_local_google_credentials_path, resolve_google_cloud_project_id


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
POPPLER_BIN = r"C:\poppler-24.02.0\Library\bin"

DATA_IDEAL_DIR = os.path.join(PROJECT_ROOT, "data", "ideal")
DATA_STUDENTS_DIR = os.path.join(PROJECT_ROOT, "data", "students")

RESULTS_OCR_DIR = os.path.join(PROJECT_ROOT, "results", "ocr")
RESULTS_DIAG_DIR = os.path.join(PROJECT_ROOT, "results", "diagrams")
RESULTS_FORMULA_DIR = os.path.join(PROJECT_ROOT, "results", "formulas")
RESULTS_FORMULA_CROP_DIR = os.path.join(PROJECT_ROOT, "results", "formula_crops")

RESULTS_EVAL_SBERT_DIR = os.path.join(PROJECT_ROOT, "results", "eval")
RESULTS_REPORT_SBERT_DIR = os.path.join(PROJECT_ROOT, "results", "reports")

RESULTS_EVAL_LLM_DIR = os.path.join(PROJECT_ROOT, "results", "eval_llm")
RESULTS_REPORT_LLM_DIR = os.path.join(PROJECT_ROOT, "results", "reports_llm")

RUBRIC_PATH = os.path.join(PROJECT_ROOT, "rubric.json")

DEFAULT_AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = ""
DEFAULT_AZURE_DOCUMENT_INTELLIGENCE_KEY = ""
DOCUMENTATION_PATH = os.path.join(PROJECT_ROOT, "README.md")

HOME_GALLERY = [
    {
        "title": "Multimodal Evaluation",
        "caption": "Text, diagrams, formulas, and handwritten content are processed in one workflow.",
        "image": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Human-Centered Review",
        "caption": "Designed for faculty workflows with explainable outputs, reports, and downloadable results.",
        "image": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "title": "Research-Driven Product",
        "caption": "A BTP platform combining OCR, semantic scoring, formula recognition, and visual comparison.",
        "image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
    },
]

RESOURCE_ITEMS = [
    {
        "category": "Frontend / App",
        "name": "Streamlit",
        "purpose": "Interactive product dashboard and evaluation workflow UI.",
    },
    {
        "category": "OCR",
        "name": "EasyOCR",
        "purpose": "Printed and cleaner answer-sheet OCR.",
    },
    {
        "category": "OCR",
        "name": "Azure Document Intelligence",
        "purpose": "Alternative handwritten answer-sheet OCR backend.",
    },
    {
        "category": "OCR",
        "name": "Google Vision AI",
        "purpose": "Google Cloud handwriting-oriented OCR backend for scanned answer sheets.",
    },
    {
        "category": "Text Evaluation",
        "name": "Sentence-Transformers all-MiniLM-L6-v2",
        "purpose": "Semantic similarity scoring for answer text.",
    },
    {
        "category": "Diagram Evaluation",
        "name": "OpenAI CLIP ViT-B/32",
        "purpose": "Visual similarity comparison between ideal and student diagrams.",
    },
    {
        "category": "Formula Evaluation",
        "name": "pix2tex",
        "purpose": "Formula image to LaTeX OCR for equation-aware scoring.",
    },
    {
        "category": "Formula Evaluation",
        "name": "SymPy",
        "purpose": "Mathematical equivalence checking for formulas.",
    },
    {
        "category": "LLM Evaluation",
        "name": "Gemini 2.5 Flash",
        "purpose": "Optional rubric-guided LLM evaluation path.",
    },
    {
        "category": "PDF / Image Processing",
        "name": "pdf2image + OpenCV + Pillow",
        "purpose": "Page conversion, cropping, preprocessing, and diagram extraction.",
    },
    {
        "category": "Reporting",
        "name": "FPDF2",
        "purpose": "Downloadable student-wise report generation.",
    },
]

TEAM_MEMBERS = [
    {
        "name": "Dr. Ashwini Kumar Upadhyay",
        "branch": "Asst. Professor, Electronics Engineering, RECK",
        "role": "Mentor & Guide",
        "photo": "https://media.licdn.com/dms/image/v2/D5603AQFRkUiDIQREig/profile-displayphoto-shrink_800_800/B56ZZiQGZOGQAc-/0/1745405110883?e=1776902400&v=beta&t=YGa0Ha4d-BY-j4l0i0KrxKY2jtcbgxsYmrp6f3-5iZw",
        "linkedin": "https://www.linkedin.com/in/dr-ashwini-kumar-upadhyay-99055152/",
        "email": "mailto:ashwini@reck.ac.in",
    },
    {
        "name": "Yuvraj Verma",
        "branch": "Electronics",
        "role": "AI & Machine Learning ",
        "photo": "https://media.licdn.com/dms/image/v2/D4D03AQG0arPVxrqrQQ/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1687669111412?e=1776902400&v=beta&t=536F13W-WntxrKPKNaRyn0ikQyouuYqzfsECG_Whg9c",
        "linkedin": "https://www.linkedin.com/in/verma-yuvraj/",
        "email": "mailto:work.yuvrajverma@gmail.com",
    },
    {
        "name": "Netranshi Tripathi",
        "branch": "Electronics",
        "role": "AI & Machine Learning",
        "photo": "https://media.licdn.com/dms/image/v2/D5635AQGoYwXWxgPRPw/profile-framedphoto-shrink_400_400/B56ZiSu1M7HkAk-/0/1754808407227?e=1775638800&v=beta&t=rfuSn349cwP4WZwP9bIfUZBS4r8lGK-2jDt2Uwo7MCI",
        "linkedin": "https://www.linkedin.com/in/netranshi-tripathi/",
        "email": "mailto:netranshitripathi@gmail.com",
    },
    {
        "name": "Yashvi Shrivastava",
        "branch": "Electronics",
        "role": "Research & Development",
        "photo": "https://media.licdn.com/dms/image/v2/D5635AQHIcPHV2dziVg/profile-framedphoto-shrink_400_400/B56Zwkra_BHcAg-/0/1770141888677?e=1775638800&v=beta&t=m7-bcFR0ugdhoy15SCAL3jzDUJxWeHjAq2kvnjnoeWg",
        "linkedin": "https://www.linkedin.com/in/yashvi-srivastava-3b8666257/",
        "email": "mailto:2208390300060@reck.ac.in",
    },
]

WORKFLOW_BLOCKS = [
    {
        "key": "input",
        "title": "Input Ready",
        "short": "Input",
        "description": "Ideal answer sheet, rubric, and student PDFs are validated and queued.",
        "tech": "Streamlit / Next.js forms, FastAPI uploads, local file staging",
    },
    {
        "key": "ocr",
        "title": "OCR Extraction",
        "short": "OCR",
        "description": "PDF pages are converted into images and text is extracted using the selected OCR backend.",
        "tech": "pdf2image, Poppler, EasyOCR, Google Vision AI, or Azure Document Intelligence",
    },
    {
        "key": "formula",
        "title": "Formula Parsing",
        "short": "Formula",
        "description": "Formula-like regions are cropped, converted into LaTeX, and prepared for symbolic checking.",
        "tech": "pix2tex, LaTeX conversion, SymPy preprocessing",
    },
    {
        "key": "diagram",
        "title": "Diagram Extraction",
        "short": "Diagram",
        "description": "Visual regions are isolated so diagrams can be compared separately from text.",
        "tech": "OpenCV, page segmentation, connected-component analysis",
    },
    {
        "key": "evaluation",
        "title": "Evaluation",
        "short": "Score",
        "description": "Text, diagrams, and formulas are scored against the ideal answer using rubric weights.",
        "tech": "Sentence Transformers, CLIP, SymPy, Gemini 2.5 Flash",
    },
    {
        "key": "report",
        "title": "Report Generation",
        "short": "Report",
        "description": "Final JSON outputs, ranking tables, and downloadable student reports are generated.",
        "tech": "JSON serialization, FPDF2, tabular summaries",
    },
]

DOCUMENTATION_METRICS = [
    {"label": "OCR Backends", "value": "3", "detail": "EasyOCR + Google Vision AI + Azure Document Intelligence"},
    {"label": "Evaluation Paths", "value": "2", "detail": "SBERT local + Gemini LLM"},
    {"label": "Modalities", "value": "3", "detail": "Text, Diagram, Formula"},
    {"label": "Primary Outputs", "value": "3", "detail": "JSON, tables, PDF reports"},
]

DOCUMENTATION_STAGE_DETAILS = [
    {
        "title": "1. Upload and Validation",
        "goal": "Collect the ideal answer sheet, rubric JSON, and student PDFs before starting the run.",
        "details": [
            "The UI validates whether the ideal PDF, rubric, and at least one student PDF are present.",
            "The rubric JSON is parsed and written locally so the evaluation modules can access one consistent configuration.",
            "The current prototype keeps one page mapped to one question.",
        ],
        "tech": "Streamlit / Next.js, FastAPI, JSON parsing, local file staging",
    },
    {
        "title": "2. OCR Layer",
        "goal": "Convert PDFs into page-level text with block metadata.",
        "details": [
            "Printed or cleaner sheets are processed through EasyOCR.",
            "Google Vision AI adds a cloud-native handwritten OCR path on Google infrastructure.",
            "Handwritten sheets are processed through Azure Document Intelligence.",
            "pdf2image and Poppler convert each PDF page into an image before OCR is applied.",
        ],
        "tech": "pdf2image, Poppler, EasyOCR, Google Vision AI, Azure Document Intelligence",
    },
    {
        "title": "3. Formula Understanding",
        "goal": "Treat mathematical expressions as equations instead of plain noisy OCR text.",
        "details": [
            "Formula-like areas are detected from OCR/page layout cues.",
            "pix2tex converts cropped equations into LaTeX.",
            "SymPy checks whether the student formula is mathematically equivalent to the ideal formula.",
        ],
        "tech": "pix2tex, LaTeX, SymPy",
    },
    {
        "title": "4. Diagram Understanding",
        "goal": "Separate visual structure from ordinary text so diagram questions are graded more fairly.",
        "details": [
            "OpenCV is used to isolate likely diagram regions from page images.",
            "Diagram crops are stored independently from OCR text outputs.",
            "These crops feed the visual scoring module later in the pipeline.",
        ],
        "tech": "OpenCV, Pillow, connected-component extraction",
    },
    {
        "title": "5. Scoring and Rubric Application",
        "goal": "Score each answer using a multimodal comparison strategy.",
        "details": [
            "Text similarity is computed using Sentence Transformers in the local path.",
            "Diagram similarity is computed using CLIP image embeddings.",
            "Formula equivalence uses SymPy in the SBERT path, while Gemini provides an LLM-based alternative evaluation path.",
        ],
        "tech": "Sentence Transformers, CLIP, SymPy, Gemini 2.5 Flash",
    },
    {
        "title": "6. Results and Reporting",
        "goal": "Create reviewable outputs for faculty, researchers, and testing teams.",
        "details": [
            "A JSON evaluation file is produced for every student.",
            "A PDF report is generated for every student answer sheet.",
            "The UI presents ranking tables, run duration, top performer, and direct downloads.",
        ],
        "tech": "FPDF2, JSON, Streamlit tables, FastAPI download endpoints",
    },
]

DOCUMENTATION_OUTPUTS = [
    {"Artifact": "OCR JSON", "Purpose": "Stores extracted text, blocks, and page-wise OCR output."},
    {"Artifact": "Formula JSON", "Purpose": "Stores detected formulas and pix2tex LaTeX outputs."},
    {"Artifact": "Diagram crops", "Purpose": "Stores extracted diagram regions used for visual comparison."},
    {"Artifact": "Evaluation JSON", "Purpose": "Stores per-student scoring details and question-wise feedback."},
    {"Artifact": "PDF report", "Purpose": "Creates a downloadable report for each student."},
]


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #f4f7fb;
            --surface: rgba(255, 255, 255, 0.78);
            --surface-strong: rgba(255, 255, 255, 0.92);
            --text: #0f172a;
            --muted: #475569;
            --primary: #0f766e;
            --secondary: #2563eb;
            --accent: #f97316;
            --shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
            --radius: 22px;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.16), transparent 30%),
                radial-gradient(circle at top right, rgba(249, 115, 22, 0.16), transparent 24%),
                linear-gradient(180deg, #f8fbff 0%, #eef4ff 45%, #f9fbff 100%);
            color: var(--text);
        }

        .block-container {
            max-width: 1280px;
            padding-top: 1.75rem;
            padding-bottom: 3rem;
        }

        div[data-testid="stVerticalBlock"] > div:has(> .hero-card),
        div[data-testid="stVerticalBlock"] > div:has(> .section-card),
        div[data-testid="stVerticalBlock"] > div:has(> .team-shell) {
            width: 100%;
        }

        .hero-card {
            background: linear-gradient(135deg, rgba(15, 118, 110, 0.96), rgba(37, 99, 235, 0.92) 58%, rgba(249, 115, 22, 0.90));
            border-radius: 28px;
            padding: 32px 34px;
            box-shadow: var(--shadow);
            color: #ffffff;
            overflow: hidden;
            position: relative;
            margin-bottom: 1rem;
        }

        .hero-card::after {
            content: "";
            position: absolute;
            inset: auto -10% -40% auto;
            width: 280px;
            height: 280px;
            background: rgba(255, 255, 255, 0.14);
            border-radius: 50%;
            filter: blur(2px);
        }

        .hero-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.16);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 999px;
            padding: 8px 14px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 16px;
        }

        .hero-title {
            font-size: 2.35rem;
            line-height: 1.05;
            font-weight: 800;
            margin: 0 0 0.75rem 0;
            letter-spacing: -0.03em;
        }

        .hero-subtitle {
            max-width: 760px;
            font-size: 1.02rem;
            line-height: 1.7;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 1.1rem;
        }

        .hero-stats {
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            margin-top: 18px;
        }

        .hero-stat {
            min-width: 170px;
            background: rgba(255, 255, 255, 0.16);
            border-radius: 18px;
            padding: 14px 16px;
            backdrop-filter: blur(8px);
        }

        .hero-stat-label {
            font-size: 0.82rem;
            color: rgba(255, 255, 255, 0.76);
        }

        .hero-stat-value {
            font-size: 1.18rem;
            font-weight: 700;
            margin-top: 5px;
        }

        .section-card {
            background: var(--surface);
            border: 1px solid rgba(255, 255, 255, 0.65);
            box-shadow: var(--shadow);
            border-radius: var(--radius);
            padding: 24px 24px 12px 24px;
            backdrop-filter: blur(14px);
            margin: 0.5rem 0 1rem 0;
        }

        .section-heading {
            font-size: 1.2rem;
            font-weight: 750;
            color: var(--text);
            margin-bottom: 0.4rem;
        }

        .section-subtext {
            color: var(--muted);
            font-size: 0.96rem;
            line-height: 1.6;
            margin-bottom: 1rem;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 16px;
        }

        .feature-card {
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(245, 248, 255, 0.92));
            border-radius: 20px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            padding: 18px;
            min-height: 180px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.72);
        }

        .feature-icon {
            width: 46px;
            height: 46px;
            border-radius: 14px;
            display: grid;
            place-items: center;
            font-size: 1.3rem;
            margin-bottom: 14px;
            background: linear-gradient(135deg, rgba(15, 118, 110, 0.14), rgba(37, 99, 235, 0.14));
        }

        .feature-title {
            font-size: 1rem;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 8px;
        }

        .feature-desc {
            color: var(--muted);
            line-height: 1.55;
            font-size: 0.92rem;
        }

        .team-shell {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.94));
            border-radius: 28px;
            padding: 26px;
            box-shadow: var(--shadow);
            color: white;
            margin-top: 1.2rem;
        }

        .team-heading {
            font-size: 1.35rem;
            font-weight: 760;
            margin-bottom: 0.35rem;
        }

        .team-subtext {
            color: rgba(255,255,255,0.72);
            margin-bottom: 1.2rem;
        }

        .team-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 18px;
        }

        .team-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.09), rgba(255,255,255,0.06));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 24px;
            padding: 18px;
            text-align: center;
        }

        .team-photo {
            width: 84px;
            height: 84px;
            border-radius: 50%;
            object-fit: cover;
            margin: 0 auto 12px auto;
            display: block;
            border: 3px solid rgba(255,255,255,0.12);
        }

        .team-name {
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .team-role {
            color: #7dd3fc;
            font-size: 0.88rem;
            margin-bottom: 6px;
        }

        .team-branch {
            color: rgba(255,255,255,0.72);
            font-size: 0.9rem;
            margin-bottom: 14px;
        }

        .team-links {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .team-links a {
            text-decoration: none;
            color: white;
            font-size: 0.86rem;
            font-weight: 700;
            padding: 8px 12px;
            border-radius: 999px;
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.95), rgba(14, 165, 233, 0.9));
            border: 1px solid rgba(255, 255, 255, 0.12);
        }

        .team-links a:last-child {
            background: linear-gradient(135deg, rgba(249, 115, 22, 0.96), rgba(239, 68, 68, 0.9));
        }

        div[data-testid="stTabs"] button[role="tab"] {
            border-radius: 999px;
            padding: 10px 18px;
            margin-right: 8px;
            background: rgba(255, 255, 255, 0.68);
            border: 1px solid rgba(148, 163, 184, 0.18);
            color: var(--text);
            font-weight: 700;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            background: linear-gradient(135deg, rgba(15, 118, 110, 0.95), rgba(37, 99, 235, 0.95));
            color: #ffffff;
            border: none;
        }

        .overview-card {
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(241, 245, 255, 0.92));
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 24px;
            overflow: hidden;
            box-shadow: var(--shadow);
            margin-bottom: 1rem;
        }

        .overview-card img {
            width: 100%;
            height: 220px;
            object-fit: cover;
            display: block;
        }

        .overview-content {
            padding: 18px;
        }

        .overview-title {
            font-size: 1rem;
            font-weight: 750;
            margin-bottom: 6px;
        }

        .overview-caption {
            color: var(--muted);
            line-height: 1.6;
            font-size: 0.92rem;
        }

        .workflow-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 14px;
            margin-top: 1rem;
        }

        .workflow-step {
            background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(247,250,255,0.95));
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 22px;
            padding: 18px;
            box-shadow: var(--shadow);
            min-height: 145px;
        }

        .workflow-index {
            width: 36px;
            height: 36px;
            display: grid;
            place-items: center;
            border-radius: 12px;
            color: white;
            font-weight: 800;
            background: linear-gradient(135deg, rgba(15, 118, 110, 0.95), rgba(249, 115, 22, 0.92));
            margin-bottom: 12px;
        }

        .workflow-title {
            font-size: 0.98rem;
            font-weight: 730;
            margin-bottom: 8px;
            color: var(--text);
        }

        .workflow-desc {
            font-size: 0.9rem;
            line-height: 1.55;
            color: var(--muted);
        }

        .simple-home-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 16px;
            margin-top: 1rem;
        }

        .simple-home-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(248,250,255,0.95));
            border-radius: 22px;
            border: 1px solid rgba(148, 163, 184, 0.16);
            box-shadow: var(--shadow);
            padding: 18px;
        }

        .simple-home-title {
            font-size: 0.98rem;
            font-weight: 760;
            color: var(--text);
            margin-bottom: 0.45rem;
        }

        .simple-home-desc {
            color: var(--muted);
            line-height: 1.6;
            font-size: 0.92rem;
        }

        .live-workflow-shell {
            background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(245,248,255,0.96));
            border-radius: 24px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            box-shadow: var(--shadow);
            padding: 22px;
            margin: 0.7rem 0 1rem 0;
        }

        .live-workflow-head {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }

        .live-workflow-title {
            font-size: 1.08rem;
            font-weight: 780;
            color: var(--text);
            margin-bottom: 0.3rem;
        }

        .live-workflow-subtext {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.6;
        }

        .workflow-status-chip {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 8px 12px;
            border-radius: 999px;
            font-size: 0.84rem;
            font-weight: 760;
            background: rgba(37, 99, 235, 0.12);
            color: #1d4ed8;
        }

        .workflow-flow {
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 10px;
            align-items: stretch;
        }

        .workflow-node-live {
            position: relative;
            padding: 16px 14px;
            border-radius: 20px;
            border: 1px solid rgba(148, 163, 184, 0.16);
            background: rgba(255,255,255,0.9);
            min-height: 136px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.72);
        }

        .workflow-node-live::after {
            content: "";
            position: absolute;
            top: 50%;
            right: -10px;
            width: 18px;
            height: 4px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.35);
            transform: translateY(-50%);
        }

        .workflow-node-live:last-child::after {
            display: none;
        }

        .workflow-node-live.done {
            border-color: rgba(15, 118, 110, 0.2);
            background: linear-gradient(180deg, rgba(220, 252, 231, 0.78), rgba(236, 253, 245, 0.92));
        }

        .workflow-node-live.active {
            border-color: rgba(37, 99, 235, 0.24);
            background: linear-gradient(180deg, rgba(219, 234, 254, 0.92), rgba(239, 246, 255, 0.96));
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.08), var(--shadow);
        }

        .workflow-node-live.pending {
            opacity: 0.88;
        }

        .workflow-node-live.skipped {
            background: rgba(241, 245, 249, 0.92);
            color: #64748b;
        }

        .workflow-node-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            margin-bottom: 10px;
        }

        .workflow-node-badge {
            width: 32px;
            height: 32px;
            display: grid;
            place-items: center;
            border-radius: 11px;
            font-size: 0.9rem;
            font-weight: 800;
            color: white;
            background: linear-gradient(135deg, rgba(15,118,110,0.95), rgba(37,99,235,0.95));
        }

        .workflow-node-state {
            font-size: 0.74rem;
            font-weight: 760;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            color: var(--muted);
        }

        .workflow-node-title {
            font-size: 0.96rem;
            font-weight: 760;
            color: var(--text);
            margin-bottom: 6px;
        }

        .workflow-node-meta {
            font-size: 0.84rem;
            line-height: 1.5;
            color: var(--muted);
        }

        .doc-metric-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 16px;
            margin-bottom: 1rem;
        }

        .doc-metric-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(248,250,255,0.94));
            border-radius: 20px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            padding: 16px;
            box-shadow: var(--shadow);
        }

        .doc-metric-label {
            color: var(--muted);
            font-size: 0.84rem;
        }

        .doc-metric-value {
            font-size: 1.2rem;
            font-weight: 780;
            color: var(--text);
            margin: 5px 0;
        }

        .doc-metric-detail {
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.5;
        }

        .doc-stage-card {
            background: rgba(255,255,255,0.92);
            border-radius: 22px;
            border: 1px solid rgba(148, 163, 184, 0.16);
            box-shadow: var(--shadow);
            padding: 18px;
            margin-bottom: 0.8rem;
        }

        .doc-stage-title {
            font-size: 1rem;
            font-weight: 760;
            color: var(--text);
            margin-bottom: 0.45rem;
        }

        .doc-stage-goal {
            color: var(--muted);
            line-height: 1.6;
            margin-bottom: 0.55rem;
        }

        .doc-tech-line {
            color: #1d4ed8;
            font-size: 0.88rem;
            font-weight: 700;
            margin-top: 0.45rem;
        }

        .resource-shell {
            background: var(--surface);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.65);
            box-shadow: var(--shadow);
            padding: 22px;
        }

        .doc-shell {
            background: rgba(15, 23, 42, 0.95);
            border-radius: 26px;
            padding: 24px;
            box-shadow: var(--shadow);
            color: #e2e8f0;
        }

        .doc-shell h1, .doc-shell h2, .doc-shell h3 {
            color: #ffffff;
        }

        .paper-shell {
            background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(248,250,255,0.94));
            border-radius: 24px;
            border: 1px solid rgba(148, 163, 184, 0.16);
            box-shadow: var(--shadow);
            padding: 22px;
        }

        .highlight-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(37, 99, 235, 0.12);
            color: #1d4ed8;
            border-radius: 999px;
            padding: 8px 14px;
            font-size: 0.88rem;
            font-weight: 700;
            margin-right: 8px;
            margin-bottom: 8px;
        }

        .results-note {
            color: var(--muted);
            line-height: 1.6;
            margin-top: -0.25rem;
            margin-bottom: 1rem;
        }

        @media (max-width: 1100px) {
            .feature-grid,
            .team-grid,
            .workflow-grid,
            .simple-home-grid,
            .doc-metric-grid,
            .workflow-flow {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 700px) {
            .hero-title {
                font-size: 1.8rem;
            }

            .feature-grid,
            .team-grid,
            .workflow-grid,
            .simple-home-grid,
            .doc-metric-grid,
            .workflow-flow {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <section class="hero-card">
            <div class="hero-chip">Product Dashboard • Automated Evaluation Suite</div>
            <h1 class="hero-title">Subjective Answer Sheet Evaluation Platform</h1>
            <p class="hero-subtitle">
                Run OCR, extract diagrams, compare answers against the ideal sheet, evaluate with
                local or LLM scoring, and export polished student reports from one colorful workflow.
            </p>
            <div class="hero-stats">
                <div class="hero-stat">
                    <div class="hero-stat-label">OCR Modes</div>
                    <div class="hero-stat-value">Printed + Handwritten</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-label">Evaluation Engines</div>
                    <div class="hero-stat-value">SBERT + Gemini</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-label">Outputs</div>
                    <div class="hero-stat-value">JSON, PDF, Summary Tables</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-label">Designed For</div>
                    <div class="hero-stat-value">Faculty + Research Workflows</div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_feature_cards() -> None:
    st.markdown(
        """
        <section class="section-card">
            <div class="section-heading">Platform Features</div>
            <div class="section-subtext">
                The workflow below is organized like a lightweight product dashboard so you can
                upload, run, monitor, review, and export results without losing the research
                flexibility of your current pipeline.
            </div>
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">1</div>
                    <div class="feature-title">Multimodal OCR</div>
                    <div class="feature-desc">
                        Use EasyOCR for printed sheets, Google Vision AI for Google-hosted handwritten
                        OCR, or Azure Document Intelligence as an alternative handwritten path without
                        changing the rest of the pipeline.
                    </div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">2</div>
                    <div class="feature-title">Hybrid Evaluation</div>
                    <div class="feature-desc">
                        Compare textual content semantically, detect diagrams, and score with either
                        fast local SBERT evaluation or Gemini-based grading.
                    </div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">3</div>
                    <div class="feature-title">Run-Time Visibility</div>
                    <div class="feature-desc">
                        Track evaluation progress live and see how much total time the run consumed
                        once processing is complete.
                    </div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">4</div>
                    <div class="feature-title">Ready-To-Share Outputs</div>
                    <div class="feature-desc">
                        Review a clean summary table, inspect output folders, and download
                        individual student reports directly from the dashboard.
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <section class="section-card">
            <div class="section-heading">{title}</div>
            <div class="section-subtext">{subtitle}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_team_section() -> None:
    cards_html: List[str] = []
    for member in TEAM_MEMBERS:
        cards_html.append(
            (
                '<div class="team-card">'
                f'<img class="team-photo" src="{member["photo"]}" alt="{member["name"]}" />'
                f'<div class="team-name">{member["name"]}</div>'
                f'<div class="team-role">{member["role"]}</div>'
                f'<div class="team-branch">{member["branch"]}</div>'
                '<div class="team-links">'
                f'<a href="{member["linkedin"]}" target="_blank">LinkedIn</a>'
                f'<a href="{member["email"]}" target="_blank">Email</a>'
                "</div>"
                "</div>"
            )
        )

    team_html = (
        '<section class="team-shell">'
        '<div class="team-heading">Our Team</div>'
        '<div class="team-subtext">'
        "Meet the talented individuals behind our innovative solution."
        "</div>"
        '<div class="team-grid">'
        f'{"".join(cards_html)}'
        "</div>"
        "</section>"
    )

    st.markdown(team_html, unsafe_allow_html=True)


def render_project_highlights() -> None:
    st.markdown(
        """
        <div style="margin: 0.25rem 0 1rem 0;">
            <span class="highlight-pill">Multimodal grading</span>
            <span class="highlight-pill">Printed + handwritten OCR</span>
            <span class="highlight-pill">Diagram + formula aware</span>
            <span class="highlight-pill">JSON + PDF reports</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview_gallery() -> None:
    cols = st.columns(3)
    for col, item in zip(cols, HOME_GALLERY):
        with col:
            st.markdown(
                f"""
                <div class="overview-card">
                    <img src="{item['image']}" alt="{item['title']}" />
                    <div class="overview-content">
                        <div class="overview-title">{item['title']}</div>
                        <div class="overview-caption">{item['caption']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_workflow_section() -> None:
    st.markdown(
        """
        <section class="section-card">
            <div class="section-heading">Simple Workflow</div>
            <div class="section-subtext">
                The current pipeline follows a clean page-wise evaluation flow so every stage can be
                tracked, debugged, and extended independently.
            </div>
            <div class="workflow-grid">
                <div class="workflow-step">
                    <div class="workflow-index">1</div>
                    <div class="workflow-title">Upload</div>
                    <div class="workflow-desc">
                        Upload the ideal answer sheet, rubric, and one or more student PDFs.
                    </div>
                </div>
                <div class="workflow-step">
                    <div class="workflow-index">2</div>
                    <div class="workflow-title">OCR</div>
                    <div class="workflow-desc">
                        Extract page-wise text using EasyOCR, Google Vision AI, or Azure Document
                        Intelligence based on the sheet type.
                    </div>
                </div>
                <div class="workflow-step">
                    <div class="workflow-index">3</div>
                    <div class="workflow-title">Visual + Formula Parsing</div>
                    <div class="workflow-desc">
                        Detect diagrams, crop formula-like regions, and convert equations into LaTeX with pix2tex.
                    </div>
                </div>
                <div class="workflow-step">
                    <div class="workflow-index">4</div>
                    <div class="workflow-title">Evaluation</div>
                    <div class="workflow-desc">
                        Score answer text, diagram similarity, and mathematical equivalence using rubric weights.
                    </div>
                </div>
                <div class="workflow-step">
                    <div class="workflow-index">5</div>
                    <div class="workflow-title">Reports</div>
                    <div class="workflow-desc">
                        Generate JSON outputs, PDF reports, ranking tables, and downloadable summaries.
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_home_tab() -> None:
    render_section_header(
        "Project Overview",
        "Automated subjective answer-sheet evaluation for text, diagrams, formulas, and handwritten submissions.",
    )
    st.markdown(
        """
        <div class="simple-home-grid">
            <div class="simple-home-card">
                <div class="simple-home-title">What It Does</div>
                <div class="simple-home-desc">
                    Runs OCR, extracts formulas and diagrams, evaluates answers, and generates student-wise PDF reports.
                </div>
            </div>
            <div class="simple-home-card">
                <div class="simple-home-title">Who It Helps</div>
                <div class="simple-home-desc">
                    Built for faculty demos, research experiments, and future product deployment workflows.
                </div>
            </div>
            <div class="simple-home-card">
                <div class="simple-home-title">Current Modes</div>
                <div class="simple-home-desc">
                    Printed OCR, handwritten OCR, SBERT local scoring, Gemini evaluation, and formula-aware grading.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_workflow_section()


def render_pdf_preview(file_bytes: bytes, height: int = 780) -> None:
    encoded = base64.b64encode(file_bytes).decode("utf-8")
    iframe = f"""
    <iframe
        src="data:application/pdf;base64,{encoded}"
        width="100%"
        height="{height}"
        type="application/pdf"
        style="border: none; border-radius: 18px; background: white;"
    ></iframe>
    """
    components.html(iframe, height=height + 20, scrolling=True)


def load_documentation_markdown() -> str:
    if os.path.exists(DOCUMENTATION_PATH):
        with open(DOCUMENTATION_PATH, "r", encoding="utf-8") as f:
            return f.read()

    return (
        "# Documentation\n\n"
        "Documentation file not found yet. Add a README.md to show project documentation here."
    )


def render_resources_tab() -> None:
    st.markdown(
        """
        <section class="section-card">
            <div class="section-heading">Resources</div>
            <div class="section-subtext">
                Key libraries, models, APIs, and frameworks currently used in the platform.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.dataframe(RESOURCE_ITEMS, width="stretch", hide_index=True)

    st.markdown(
        """
        <section class="section-card">
            <div class="section-heading">Reference Areas</div>
            <div class="section-subtext">
                OCR, visual similarity, semantic scoring, symbolic mathematics, PDF rendering,
                and Streamlit-based interaction design form the current technical base.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_research_paper_tab() -> None:
    st.markdown(
        """
        <div class="paper-shell">
            <div class="section-heading">Research Paper Preview</div>
            <div class="section-subtext">
                Upload the final research paper PDF here later. This tab is ready to preview the PDF directly inside the app.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_paper = st.file_uploader(
        "Upload Research Paper (PDF)",
        type=["pdf"],
        key="research-paper-uploader",
        help="This is only for UI preview right now. It does not affect the evaluation pipeline.",
    )

    if uploaded_paper is None:
        st.info("No research paper uploaded yet. Once you upload a PDF here, a full preview will appear below.")
        return

    paper_bytes = uploaded_paper.getvalue()
    st.download_button(
        "Download Uploaded Paper",
        data=paper_bytes,
        file_name=uploaded_paper.name,
        mime="application/pdf",
        width="content",
    )
    render_pdf_preview(paper_bytes)


def render_documentation_tab() -> None:
    render_section_header(
        "Documentation",
        "Technical notes for every stage of the pipeline, the main technologies in use, and the outputs generated after evaluation.",
    )
    render_documentation_overview()

    with st.expander("README / Detailed Notes", expanded=False):
        documentation_text = load_documentation_markdown()
        st.markdown(documentation_text)
        st.download_button(
            "Download Documentation",
            data=documentation_text.encode("utf-8"),
            file_name="README.md",
            mime="text/markdown",
            key="download-documentation",
        )


def save_uploaded_file(uploaded_file, save_dir: str) -> str:
    ocr_pipeline.ensure_dir(save_dir)
    file_path = os.path.join(save_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def format_duration(duration_seconds: float) -> str:
    total_seconds = int(round(duration_seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def infer_workflow_stage(message: str, engine: str) -> str:
    message_lc = message.lower()
    if "formula parsing not needed" in message_lc or "no formula cues" in message_lc:
        return "diagram"
    if "report" in message_lc:
        return "report"
    if "evaluat" in message_lc:
        return "evaluation"
    if "diagram" in message_lc:
        return "diagram"
    if "formula" in message_lc:
        return "formula"
    if "ocr" in message_lc:
        return "ocr"
    if "complete" in message_lc:
        return "report"
    return "input"


def visible_workflow_step(current_step: int, total_steps: int, message: str) -> int:
    if total_steps <= 0:
        return 0
    if "complete" in message.lower():
        return total_steps
    return min(current_step + 1, total_steps)


def build_workflow_html(
    engine: str,
    current_message: str,
    current_step: int,
    total_steps: int,
    elapsed_seconds: float,
    history_messages: Optional[List[str]] = None,
) -> str:
    active_stage = infer_workflow_stage(current_message, engine)
    display_step = visible_workflow_step(current_step, total_steps, current_message)
    steps_per_minute = (current_step / max(elapsed_seconds, 0.001)) * 60 if current_step else 0.0
    stage_order = [block["key"] for block in WORKFLOW_BLOCKS]
    active_index = stage_order.index(active_stage) if active_stage in stage_order else 0
    normalized_message = (current_message or "").lower()
    is_complete = "complete" in normalized_message and "fail" not in normalized_message
    formula_not_needed = any(
        "formula parsing not needed" in message.lower() or "no formula cues" in message.lower()
        for message in (history_messages or [current_message])
    )

    blocks_html: List[str] = []
    for index, block in enumerate(WORKFLOW_BLOCKS):
        key = block["key"]
        if key == "formula" and formula_not_needed:
            state_class = "skipped"
            state_label = "Not Needed"
        elif is_complete:
            state_class = "done"
            state_label = "Done"
        elif index < active_index:
            state_class = "done"
            state_label = "Done"
        elif key == active_stage:
            state_class = "active"
            state_label = "Running"
        else:
            state_class = "pending"
            state_label = "Pending"

        blocks_html.append(
            textwrap.dedent(
                f"""
                <div class="workflow-node-live {state_class}">
                    <div>
                        <div class="workflow-node-top">
                            <div class="workflow-node-badge">{index + 1}</div>
                            <div class="workflow-node-state">{state_label}</div>
                        </div>
                        <div class="workflow-node-title">{block['title']}</div>
                        <div class="workflow-node-meta">{block['description']}</div>
                    </div>
                    <div class="workflow-node-meta"><strong>Tech:</strong> {block['tech']}</div>
                </div>
                """
            ).strip()
        )

    return textwrap.dedent(
        f"""
        <section class="live-workflow-shell">
            <div class="live-workflow-head">
                <div>
                    <div class="live-workflow-title">Real-Time Workflow Tracker</div>
                    <div class="live-workflow-subtext">{current_message}</div>
                </div>
                <div class="workflow-status-chip">Step {display_step}/{max(total_steps, 1)} • {steps_per_minute:.2f} steps/min • {format_duration(elapsed_seconds)}</div>
            </div>
            <div class="workflow-flow">{''.join(blocks_html)}</div>
        </section>
        """
    ).strip()


def render_documentation_overview() -> None:
    metric_cards = "".join(
        [
            f"""
            <div class="doc-metric-card">
                <div class="doc-metric-label">{item['label']}</div>
                <div class="doc-metric-value">{item['value']}</div>
                <div class="doc-metric-detail">{item['detail']}</div>
            </div>
            """
            for item in DOCUMENTATION_METRICS
        ]
    )
    st.markdown(
        f"""
        <div class="doc-metric-grid">
            {metric_cards}
        </div>
        """,
        unsafe_allow_html=True,
    )

    chart_df = pd.DataFrame(
        {
            "Coverage": [100, 100, 95, 90, 100, 100],
        },
        index=["PDF Upload", "OCR", "Formula", "Diagram", "Scoring", "Reports"],
    )
    st.bar_chart(chart_df, width="stretch")

    for section in DOCUMENTATION_STAGE_DETAILS:
        bullets = "".join(f"<li>{item}</li>" for item in section["details"])
        st.markdown(
            f"""
            <section class="doc-stage-card">
                <div class="doc-stage-title">{section['title']}</div>
                <div class="doc-stage-goal">{section['goal']}</div>
                <ul>{bullets}</ul>
                <div class="doc-tech-line">Tech used: {section['tech']}</div>
            </section>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Output Artifacts")
    st.dataframe(DOCUMENTATION_OUTPUTS, width="stretch", hide_index=True)

    st.markdown("### Technology Stack")
    st.dataframe(RESOURCE_ITEMS, width="stretch", hide_index=True)


def build_summary_rows(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ordered = sorted(results, key=lambda row: row["percentage"], reverse=True)
    summary_rows: List[Dict[str, Any]] = []
    for rank, row in enumerate(ordered, start=1):
        summary_rows.append(
            {
                "Rank": rank,
                "Student": row["student_base"],
                "Total Score": round(row["total_score"], 2),
                "Max Score": round(row["max_total"], 2),
                "Percentage": round(row["percentage"], 2),
            }
        )
    return summary_rows


def build_questionwise_rows(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ordered = sorted(results, key=lambda row: row["percentage"], reverse=True)
    question_ids = sorted(
        {
            int(question.get("question_id", 0))
            for result in ordered
            for question in result.get("questions", [])
            if question.get("question_id") is not None
        }
    )

    table_rows: List[Dict[str, Any]] = []
    for result in ordered:
        row: Dict[str, Any] = {"Student": result["student_base"]}
        question_map = {
            int(question["question_id"]): round(float(question.get("score", 0.0)), 2)
            for question in result.get("questions", [])
            if question.get("question_id") is not None
        }
        for question_id in question_ids:
            row[f"Q{question_id}"] = question_map.get(question_id, 0.0)
        row["Total"] = round(float(result.get("total_score", 0.0)), 2)
        table_rows.append(row)

    return table_rows


def build_run_signature(
    ideal_pdf: Optional[Any],
    rubric_file: Optional[Any],
    student_pdfs: Optional[List[Any]],
    engine_choice: str,
    ocr_mode: str,
) -> Dict[str, Any]:
    def file_signature(uploaded: Optional[Any]) -> Optional[tuple]:
        if uploaded is None:
            return None
        return (
            getattr(uploaded, "name", None),
            getattr(uploaded, "size", None),
        )

    return {
        "ideal_pdf": file_signature(ideal_pdf),
        "rubric_file": file_signature(rubric_file),
        "student_pdfs": tuple(file_signature(uploaded) for uploaded in (student_pdfs or [])),
        "engine_choice": engine_choice,
        "ocr_mode": ocr_mode,
    }


def get_local_runtime_status(ocr_backend: str) -> Dict[str, str]:
    try:
        import torch
    except Exception as exc:
        return {
            "cuda_available": "No",
            "device_name": f"Unavailable ({exc})",
            "easyocr_gpu": "Disabled",
            "torch_version": "Unavailable",
        }

    cuda_available = bool(torch.cuda.is_available())
    device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU only"
    if ocr_backend == "easyocr":
        easyocr_gpu = "Enabled" if cuda_available else "Disabled"
    elif ocr_backend == "google_vision":
        easyocr_gpu = "N/A (Google Vision mode)"
    else:
        easyocr_gpu = "N/A (Azure OCR mode)"
    return {
        "cuda_available": "Yes" if cuda_available else "No",
        "device_name": device_name,
        "easyocr_gpu": easyocr_gpu,
        "torch_version": getattr(torch, "__version__", "Unknown"),
    }


def prepare_google_cloud_runtime() -> Dict[str, Optional[str]]:
    project_id = resolve_google_cloud_project_id()
    credentials_path = find_local_google_credentials_path()

    if project_id:
        for env_name in ("GOOGLE_CLOUD_PROJECT", "VERTEX_AI_PROJECT", "GCLOUD_PROJECT", "GCP_PROJECT"):
            if not os.environ.get(env_name, "").strip():
                os.environ[env_name] = project_id

    if credentials_path and os.path.exists(credentials_path):
        current_credentials = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
        if not current_credentials or not os.path.exists(current_credentials):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    if not os.environ.get("GOOGLE_CLOUD_LOCATION", "").strip():
        os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

    return {
        "project_id": project_id,
        "credentials_path": credentials_path,
    }


def run_full_pipeline(
    ideal_pdf_path: str,
    student_pdf_paths: List[str],
    rubric_dict: Dict[str, Any],
    engine: str,
    ocr_backend: str,
    azure_settings: Optional[Dict[str, str]] = None,
    progress_callback: Optional[Callable[[int, int, str, float], None]] = None,
) -> (List[Dict[str, Any]], str, str, float):
    started_at = time.perf_counter()
    azure_settings = azure_settings or {}
    progress_bar = None
    status_text = None
    if progress_callback is None:
        progress_bar = st.progress(0.0)
        status_text = st.empty()

    def publish_progress(current_step: int, total_steps: int, message: str) -> None:
        elapsed = time.perf_counter() - started_at
        if status_text is not None:
            status_text.write(message)
        if progress_bar is not None:
            progress = current_step / max(total_steps, 1)
            progress_bar.progress(min(progress, 1.0))
        if progress_callback is not None:
            progress_callback(current_step, total_steps, message, elapsed)

    try:
        import torch

        local_use_gpu = bool(torch.cuda.is_available())
    except Exception:
        local_use_gpu = False

    config = pipeline_service.PipelineServiceConfig(
        poppler_path=POPPLER_BIN,
        dpi=300,
        use_gpu=local_use_gpu,
        languages=["en"],
        google_vision_language_hints=["en-t-i0-handwrit", "en"],
        rubric_path=RUBRIC_PATH,
        ocr_root=RESULTS_OCR_DIR,
        diagram_root=RESULTS_DIAG_DIR,
        formula_root=RESULTS_FORMULA_DIR,
        formula_crop_root=RESULTS_FORMULA_CROP_DIR,
        eval_sbert_root=RESULTS_EVAL_SBERT_DIR,
        report_sbert_root=RESULTS_REPORT_SBERT_DIR,
        eval_llm_root=RESULTS_EVAL_LLM_DIR,
        report_llm_root=RESULTS_REPORT_LLM_DIR,
        ocr_workers=2 if (ocr_backend == "easyocr" and local_use_gpu) else 4,
        diagram_workers=6,
        formula_workers=2 if local_use_gpu else 2,
        sbert_eval_workers=2 if local_use_gpu else 1,
        llm_eval_workers=4,
        report_workers=6,
        enable_formula_autoskip=True,
    )

    all_results, eval_dir, report_dir, _ = pipeline_service.run_pipeline(
        ideal_pdf_path=ideal_pdf_path,
        student_pdf_paths=student_pdf_paths,
        rubric_dict=rubric_dict,
        engine=engine,
        ocr_backend=ocr_backend,
        config=config,
        azure_settings=azure_settings,
        progress_callback=publish_progress,
    )

    if progress_bar is not None:
        progress_bar.progress(1.0)
    time.sleep(0.25)

    elapsed = time.perf_counter() - started_at
    return all_results, eval_dir, report_dir, elapsed


def render_results(
    results: List[Dict[str, Any]],
    engine_choice: str,
    ocr_mode: str,
    eval_dir_used: str,
    report_dir_used: str,
    elapsed_seconds: float,
) -> None:
    st.markdown(
        """
        <section class="section-card">
            <div class="section-heading">Execution Summary</div>
            <div class="section-subtext">
                The run has finished successfully. Review timing, ranking, exported artifacts,
                and report downloads below.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    total_students = len(results)
    average_percentage = (
        sum(result["percentage"] for result in results) / total_students
        if total_students
        else 0.0
    )
    top_student = max(results, key=lambda item: item["percentage"]) if results else None

    metric_cols = st.columns(4)
    metric_cols[0].metric("Students Processed", total_students)
    metric_cols[1].metric("Run Time", format_duration(elapsed_seconds))
    metric_cols[2].metric("Average Score", f"{average_percentage:.2f}%")
    metric_cols[3].metric(
        "Top Performer",
        top_student["student_base"] if top_student else "-",
        f"{top_student['percentage']:.2f}%" if top_student else None,
    )

    st.markdown(
        f"""
        <div class="results-note">
            <strong>Engine:</strong> {engine_choice} &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>OCR Mode:</strong> {ocr_mode} &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>Evaluation JSON:</strong> {eval_dir_used} &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>Reports:</strong> {report_dir_used}
        </div>
        """,
        unsafe_allow_html=True,
    )

    summary_rows = build_summary_rows(results)
    st.dataframe(summary_rows, width="stretch", hide_index=True)

    questionwise_rows = build_questionwise_rows(results)
    questionwise_df = pd.DataFrame(questionwise_rows)

    st.markdown(
        """
        <section class="section-card">
            <div class="section-heading">Question-Wise Marks Table</div>
            <div class="section-subtext">
                Download the complete marksheet with each student's question-wise marks and total score.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(questionwise_df, width="stretch", hide_index=True)
    st.download_button(
        label="Download question-wise marks table (CSV)",
        data=questionwise_df.to_csv(index=False).encode("utf-8"),
        file_name="questionwise_marks_table.csv",
        mime="text/csv",
        width="stretch",
        key="download-questionwise-table",
    )

    st.markdown(
        """
        <section class="section-card">
            <div class="section-heading">Download Reports</div>
            <div class="section-subtext">
                Export polished student PDFs directly from the dashboard.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    for index in range(0, len(summary_rows), 3):
        cols = st.columns(3)
        for col, row in zip(cols, summary_rows[index:index + 3]):
            student_name = row["Student"]
            pdf_path = os.path.join(report_dir_used, f"{student_name}_report.pdf")
            with col:
                st.markdown(
                    f"""
                    <div class="section-card" style="padding:18px 18px 10px 18px; margin-bottom: 0.6rem;">
                        <div class="section-heading" style="font-size: 1rem; margin-bottom: 0.2rem;">{student_name}</div>
                        <div class="section-subtext" style="margin-bottom: 0.3rem;">
                            Score: <strong>{row['Percentage']:.2f}%</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    st.download_button(
                        label=f"Download {student_name}",
                        data=pdf_bytes,
                        file_name=f"{student_name}_report.pdf",
                        mime="application/pdf",
                        width="stretch",
                        key=f"download-{student_name}",
                    )
                else:
                    st.warning(f"Report not found for {student_name}.")


def render_evaluate_tab() -> None:
    render_section_header(
        "Evaluate Answer Sheets",
        "Configure the batch, choose the OCR and scoring mode, then track the pipeline live from OCR to report generation.",
    )

    col_left, col_right = st.columns([1.15, 0.85])
    azure_settings: Dict[str, str] = {}

    with col_left:
        st.subheader("Input Configuration")
        ideal_pdf = st.file_uploader(
            "Ideal Answer Sheet (PDF)",
            type=["pdf"],
            help="Upload the teacher's ideal answer sheet.",
            key="ideal-pdf",
        )

        rubric_file = st.file_uploader(
            "Rubric (rubric.json)",
            type=["json"],
            help="Upload the rubric JSON with per-question weights.",
            key="rubric-json",
        )

        student_pdfs = st.file_uploader(
            "Student Answer Sheets (PDF, multiple allowed)",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload one or more student answer sheets.",
            key="student-pdfs",
        )

    with col_right:
        st.subheader("Execution Settings")
        engine_choice = st.radio(
            "Evaluation Engine",
            ["SBERT (fast, local)", "Gemini 2.5 Flash (Vertex AI)"],
            help="Use SBERT for fast local scoring or Gemini for LLM-assisted evaluation.",
            key="engine-choice",
        )
        st.caption(
            "Formula-aware parsing using pix2tex + SymPy now runs before scoring for both SBERT and Gemini paths when formulas are detected."
        )

        ocr_mode = st.radio(
            "OCR Mode",
            [
                "Current/printed sheets (EasyOCR)",
                "Handwritten sheets (Google Vision AI)",
                "Handwritten sheets (Azure Document Intelligence)",
            ],
            help="Choose the OCR backend that matches the batch you are processing.",
            key="ocr-mode",
        )

        if "Google Vision" in ocr_mode:
            st.caption(
                "Google Vision handwritten mode uses Google Cloud Application Default Credentials "
                "from your local machine or deployed runtime."
            )
        elif ocr_mode.startswith("Handwritten"):
            st.caption("Azure handwritten mode uses your Azure Document Intelligence endpoint and key.")
            azure_settings = {
                "endpoint": st.text_input(
                    "Azure Document Intelligence Endpoint",
                    value=DEFAULT_AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
                    help="Example: https://your-resource-name.cognitiveservices.azure.com/",
                    key="azure-endpoint",
                ).strip(),
                "key": st.text_input(
                    "Azure Document Intelligence Key",
                    value=DEFAULT_AZURE_DOCUMENT_INTELLIGENCE_KEY,
                    type="password",
                    key="azure-key",
                ).strip(),
            }

        runtime_status = get_local_runtime_status(
            "google_vision" if "Google Vision" in ocr_mode else "azure" if "Azure" in ocr_mode else "easyocr"
        )
        st.markdown(
            f"""
            <div class="results-note" style="margin: 0.9rem 0 0.2rem 0;">
                <strong>CUDA available:</strong> {runtime_status['cuda_available']} &nbsp;&nbsp;|&nbsp;&nbsp;
                <strong>Device:</strong> {runtime_status['device_name']} &nbsp;&nbsp;|&nbsp;&nbsp;
                <strong>EasyOCR GPU:</strong> {runtime_status['easyocr_gpu']} &nbsp;&nbsp;|&nbsp;&nbsp;
                <strong>Torch:</strong> {runtime_status['torch_version']}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        run_button = st.button("Run Evaluation", width="stretch", type="primary", key="run-eval")

    workflow_placeholder = st.empty()
    progress_metrics_placeholder = st.empty()

    initial_workflow_message = (
        "Waiting for inputs. Once you click Run Evaluation, the workflow will track OCR, formulas, diagrams, scoring, and reports."
    )
    workflow_history_messages = [initial_workflow_message]
    workflow_placeholder.markdown(
        build_workflow_html(
            engine="SBERT" if engine_choice.startswith("SBERT") else "LLM",
            current_message=initial_workflow_message,
            current_step=0,
            total_steps=1,
            elapsed_seconds=0.0,
            history_messages=workflow_history_messages,
        ),
        unsafe_allow_html=True,
    )

    current_signature = build_run_signature(
        ideal_pdf=ideal_pdf,
        rubric_file=rubric_file,
        student_pdfs=student_pdfs,
        engine_choice=engine_choice,
        ocr_mode=ocr_mode,
    )
    previous_signature = st.session_state.get("last_run_signature")
    if previous_signature is not None and previous_signature != current_signature:
        st.session_state.pop("last_run", None)
    st.session_state["last_run_signature"] = current_signature

    if run_button:
        if ideal_pdf is None:
            st.error("Please upload the ideal answer sheet PDF.")
            return
        if not student_pdfs:
            st.error("Please upload at least one student PDF.")
            return
        if rubric_file is None:
            st.error("Please upload a rubric.json file.")
            return

        st.session_state.pop("last_run", None)

        try:
            rubric_dict = json.load(rubric_file)
        except Exception as e:
            st.error(f"Failed to parse rubric JSON: {e}")
            return

        engine_flag = "SBERT" if engine_choice.startswith("SBERT") else "LLM"
        if "Google Vision" in ocr_mode:
            ocr_backend = "google_vision"
        elif "Azure" in ocr_mode:
            ocr_backend = "azure"
        else:
            ocr_backend = "easyocr"

        if ocr_backend == "azure":
            missing_fields = [
                label
                for label, value in (
                    ("endpoint", azure_settings.get("endpoint", "")),
                    ("key", azure_settings.get("key", "")),
                )
                if not value
            ]
            if missing_fields:
                st.error(
                    "Please fill in the Azure Document Intelligence settings for handwritten OCR: "
                    + ", ".join(missing_fields)
                    + "."
                )
                return

        st.success(
            f"Files received. Engine selected: {engine_choice}. OCR mode: {ocr_mode}. Starting the pipeline..."
        )

        ideal_pdf_path = save_uploaded_file(ideal_pdf, DATA_IDEAL_DIR)
        student_pdf_paths = [save_uploaded_file(f, DATA_STUDENTS_DIR) for f in student_pdfs]
        workflow_history_messages = []
        workflow_state = {"current_step": 0, "total_steps": 1, "elapsed_seconds": 0.0}

        if ocr_backend == "google_vision" or engine_flag == "LLM":
            cloud_runtime = prepare_google_cloud_runtime()
            if engine_flag == "LLM" and not cloud_runtime.get("project_id"):
                st.error(
                    "Google Cloud project configuration is missing for Gemini Vertex AI. "
                    "Set a default project in gcloud before running the local LLM path."
                )
                return

        def progress_callback(current_step: int, total_steps: int, message: str, elapsed_seconds: float) -> None:
            workflow_history_messages.append(message)
            workflow_state["current_step"] = current_step
            workflow_state["total_steps"] = total_steps
            workflow_state["elapsed_seconds"] = elapsed_seconds
            display_step = visible_workflow_step(current_step, total_steps, message)
            workflow_placeholder.markdown(
                build_workflow_html(
                    engine=engine_flag,
                    current_message=message,
                    current_step=current_step,
                    total_steps=total_steps,
                    elapsed_seconds=elapsed_seconds,
                    history_messages=workflow_history_messages,
                ),
                unsafe_allow_html=True,
            )
            cols = progress_metrics_placeholder.columns(4)
            cols[0].metric("Current Step", f"{display_step}/{max(total_steps, 1)}")
            cols[1].metric("Elapsed", format_duration(elapsed_seconds))
            cols[2].metric(
                "Speed",
                f"{((current_step / max(elapsed_seconds, 0.001)) * 60):.2f} steps/min" if current_step else "0.00 steps/min",
            )
            cols[3].metric("Active Stage", infer_workflow_stage(message, engine_flag).replace("-", " ").title())

        try:
            results, eval_dir_used, report_dir_used, elapsed_seconds = run_full_pipeline(
                ideal_pdf_path=ideal_pdf_path,
                student_pdf_paths=student_pdf_paths,
                rubric_dict=rubric_dict,
                engine=engine_flag,
                ocr_backend=ocr_backend,
                azure_settings=azure_settings,
                progress_callback=progress_callback,
            )
        except Exception as e:
            st.session_state.pop("last_run", None)
            st.error(f"Pipeline failed: {e}")
            return

        final_total_steps = max(int(workflow_state["total_steps"]), 1)
        workflow_placeholder.markdown(
            build_workflow_html(
                engine=engine_flag,
                current_message="Evaluation completed successfully.",
                current_step=final_total_steps,
                total_steps=final_total_steps,
                elapsed_seconds=elapsed_seconds,
                history_messages=workflow_history_messages + ["Evaluation completed successfully."],
            ),
            unsafe_allow_html=True,
        )
        cols = progress_metrics_placeholder.columns(4)
        cols[0].metric("Students", len(results))
        cols[1].metric("Total Time", format_duration(elapsed_seconds))
        cols[2].metric(
            "Average Speed",
            f"{(((3 + 5 * len(student_pdf_paths)) if engine_flag == 'SBERT' else (2 + 4 * len(student_pdf_paths))) / max(elapsed_seconds, 0.001) * 60):.2f} steps/min",
        )
        cols[3].metric("Stage", "Completed")

        st.session_state["last_run"] = {
            "results": results,
            "engine_choice": engine_choice,
            "ocr_mode": ocr_mode,
            "eval_dir_used": eval_dir_used,
            "report_dir_used": report_dir_used,
            "elapsed_seconds": elapsed_seconds,
        }
        st.session_state["last_run_signature"] = current_signature

    last_run = st.session_state.get("last_run")
    if last_run:
        render_results(
            results=last_run["results"],
            engine_choice=last_run["engine_choice"],
            ocr_mode=last_run["ocr_mode"],
            eval_dir_used=last_run["eval_dir_used"],
            report_dir_used=last_run["report_dir_used"],
            elapsed_seconds=last_run["elapsed_seconds"],
        )


def main():
    st.set_page_config(
        page_title="Automated Subjective Answer Sheet Evaluation",
        layout="wide",
        page_icon="📘",
    )

    inject_custom_css()
    render_hero()
    render_feature_cards()

    st.markdown(
        """
        <section class="section-card">
            <div class="section-heading">Run A New Evaluation</div>
            <div class="section-subtext">
                Upload the teacher reference sheet, rubric, and one or more student answer sheets.
                Choose the OCR mode and evaluation engine that best fits the batch you want to process.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([1.15, 0.85])
    azure_settings: Dict[str, str] = {}

    with col_left:
        st.subheader("Input Configuration")
        ideal_pdf = st.file_uploader(
            "Ideal Answer Sheet (PDF)",
            type=["pdf"],
            help="Upload the teacher's ideal answer sheet.",
        )

        rubric_file = st.file_uploader(
            "Rubric (rubric.json)",
            type=["json"],
            help="Upload the rubric JSON with per-question weights.",
        )

        student_pdfs = st.file_uploader(
            "Student Answer Sheets (PDF, multiple allowed)",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload one or more student answer sheets.",
        )

    with col_right:
        st.subheader("Execution Settings")
        engine_choice = st.radio(
            "Evaluation Engine",
            ["SBERT (fast, local)", "Gemini 2.5 Flash (Vertex AI)"],
            help="Use SBERT for fast local scoring or Gemini for LLM-assisted evaluation.",
        )
        st.caption(
            "Formula-aware parsing using pix2tex + SymPy now runs before scoring for both SBERT and Gemini paths when formulas are detected."
        )

        ocr_mode = st.radio(
            "OCR Mode",
            [
                "Current/printed sheets (EasyOCR)",
                "Handwritten sheets (Google Vision AI)",
                "Handwritten sheets (Azure Document Intelligence)",
            ],
            help="Choose the OCR backend that matches the batch you are processing.",
        )

        if "Google Vision" in ocr_mode:
            st.caption(
                "Google Vision handwritten mode uses Google Cloud Application Default Credentials "
                "from your local machine or deployed runtime."
            )
        elif ocr_mode.startswith("Handwritten"):
            st.caption(
                "Azure handwritten mode uses your Azure Document Intelligence endpoint and key."
            )
            azure_settings = {
                "endpoint": st.text_input(
                    "Azure Document Intelligence Endpoint",
                    value=DEFAULT_AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
                    help="Example: https://your-resource-name.cognitiveservices.azure.com/",
                ).strip(),
                "key": st.text_input(
                    "Azure Document Intelligence Key",
                    value=DEFAULT_AZURE_DOCUMENT_INTELLIGENCE_KEY,
                    type="password",
                ).strip(),
            }

        st.markdown("---")
        run_button = st.button("Run Evaluation", width="stretch", type="primary")

    if not run_button:
        render_team_section()
        return

    if ideal_pdf is None:
        st.error("Please upload the ideal answer sheet PDF.")
        render_team_section()
        return
    if not student_pdfs:
        st.error("Please upload at least one student PDF.")
        render_team_section()
        return
    if rubric_file is None:
        st.error("Please upload a rubric.json file.")
        render_team_section()
        return

    try:
        rubric_dict = json.load(rubric_file)
    except Exception as e:
        st.error(f"Failed to parse rubric JSON: {e}")
        render_team_section()
        return

    engine_flag = "SBERT" if engine_choice.startswith("SBERT") else "LLM"
    if "Google Vision" in ocr_mode:
        ocr_backend = "google_vision"
    elif "Azure" in ocr_mode:
        ocr_backend = "azure"
    else:
        ocr_backend = "easyocr"

    if ocr_backend == "azure":
        missing_fields = [
            label
            for label, value in (
                ("endpoint", azure_settings.get("endpoint", "")),
                ("key", azure_settings.get("key", "")),
            )
            if not value
        ]
        if missing_fields:
            st.error(
                "Please fill in the Azure Document Intelligence settings for handwritten OCR: "
                + ", ".join(missing_fields)
                + "."
            )
            render_team_section()
            return

    st.success(
        f"Files received. Engine selected: {engine_choice}. "
        f"OCR mode: {ocr_mode}. Starting the pipeline..."
    )

    ideal_pdf_path = save_uploaded_file(ideal_pdf, DATA_IDEAL_DIR)
    student_pdf_paths = [
        save_uploaded_file(f, DATA_STUDENTS_DIR) for f in student_pdfs
    ]

    try:
        results, eval_dir_used, report_dir_used, elapsed_seconds = run_full_pipeline(
            ideal_pdf_path=ideal_pdf_path,
            student_pdf_paths=student_pdf_paths,
            rubric_dict=rubric_dict,
            engine=engine_flag,
            ocr_backend=ocr_backend,
            azure_settings=azure_settings,
        )
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        render_team_section()
        return

    render_results(
        results=results,
        engine_choice=engine_choice,
        ocr_mode=ocr_mode,
        eval_dir_used=eval_dir_used,
        report_dir_used=report_dir_used,
        elapsed_seconds=elapsed_seconds,
    )
    render_team_section()


def main():
    st.set_page_config(
        page_title="Automated Subjective Answer Sheet Evaluation",
        layout="wide",
        page_icon="📘",
    )

    inject_custom_css()
    st.markdown(
        """
        <section class="section-card" style="padding-bottom: 18px;">
            <div class="section-heading">Platform Navigation</div>
            <div class="section-subtext">
                Move from overview to evaluation, then review the full technical documentation before opening the team and supporting tabs.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    home_tab, evaluate_tab, docs_tab, team_tab, paper_tab, resources_tab = st.tabs(
        ["Home", "Evaluate", "Documentation", "Team", "Research Paper", "Resources"]
    )

    with home_tab:
        render_home_tab()

    with evaluate_tab:
        render_evaluate_tab()

    with docs_tab:
        render_documentation_tab()

    with team_tab:
        render_section_header(
            "Team",
            "Meet the people behind the project, their roles, and how they contribute to the platform.",
        )
        render_team_section()

    with paper_tab:
        render_research_paper_tab()

    with resources_tab:
        render_resources_tab()


if __name__ == "__main__":
    main()
