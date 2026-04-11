# Automated Subjective Answer Sheet Evaluation Platform

## Overview

This project is a multimodal subjective answer-sheet evaluation system built for academic and research workflows. It supports both printed and handwritten answer sheets and combines OCR, semantic text comparison, diagram analysis, formula-aware scoring, and PDF report generation inside a Streamlit dashboard.

## Core Capabilities

- OCR for printed sheets using EasyOCR
- OCR for handwritten sheets using Google Vision AI or Azure Document Intelligence
- Semantic answer evaluation using Sentence-BERT
- LLM-assisted evaluation using Gemini
- Diagram extraction and similarity scoring
- Formula detection, pix2tex OCR, and SymPy-based mathematical equivalence scoring
- Student-wise PDF report generation
- Evaluation summaries and downloadable outputs through the UI

## High-Level Workflow

1. Upload the ideal answer sheet, rubric JSON, and student PDFs.
2. Select the OCR mode and evaluation engine.
3. Run OCR page by page on each PDF.
4. Extract diagrams from each page.
5. In SBERT mode, detect formula regions and convert them into LaTeX with pix2tex.
6. Score text, diagrams, and formulas according to rubric weights.
7. Save JSON results and generate PDF reports.
8. Review the output through the dashboard table and download actions.

## Current OCR Modes

### Current/printed sheets (EasyOCR)

Used for cleaner, printed, or less noisy answer sheets.

### Handwritten sheets (Azure Document Intelligence)

Used for handwritten answer sheets and works page by page to stay within practical resource limits.

### Handwritten sheets (Google Vision AI)

Used for handwritten answer sheets when you want a Google Cloud-native OCR path driven by Application Default Credentials.

## Current Evaluation Modes

### SBERT (fast, local)

- Text similarity with `sentence-transformers/all-MiniLM-L6-v2`
- Diagram similarity with CLIP
- Formula-aware scoring with pix2tex and SymPy

### Gemini 2.5 Flash (LLM API)

- OCR text is passed to Gemini
- Diagram images can be attached
- Returns score and textual feedback

Note: formula-aware symbolic scoring is currently strongest in the SBERT path.

## Formula-Aware Evaluation

The project now includes a dedicated formula stage:

- OCR blocks are grouped into line candidates
- Formula-like lines are cropped from page images
- pix2tex converts those crops to LaTeX
- SymPy attempts symbolic equivalence checks
- Formula similarity becomes a separate rubric-weighted component

This allows mathematically equivalent expressions such as `(x+1)^2` and `x^2 + 2x + 1` to receive appropriate credit.

## Output Directories

- `results/ocr` : page-wise OCR JSON
- `results/diagrams` : extracted diagram crops
- `results/formulas` : formula OCR JSON
- `results/formula_crops` : cropped formula images
- `results/eval` : SBERT evaluation JSON
- `results/eval_llm` : Gemini evaluation JSON
- `results/reports` : SBERT PDF reports
- `results/reports_llm` : Gemini PDF reports

## Technology Stack

- Streamlit
- FastAPI
- Next.js
- EasyOCR
- Google Vision AI
- Azure Document Intelligence
- Sentence Transformers
- OpenAI CLIP
- pix2tex
- SymPy
- pdf2image
- OpenCV
- Pillow
- FPDF2

## Production Deployment Path

Recommended public deployment:

- `web/` on **Vercel**
- `backend_api/` + `src/` on **Google Cloud Run**

This split is preferred because:

- Vercel is ideal for the professional Next.js frontend
- Cloud Run gives the backend a direct HTTPS URL and handles container deployment cleanly
- Cloud Run supports larger request bodies and longer request timeouts than the Vercel upload-proxy path
- handwritten OCR can use Google Vision AI or Azure Document Intelligence without tying hosting to Azure

Deployment guide:

- [DEPLOY_VERCEL_CLOUD_RUN.md](C:/Users/Yuvraj%20Verma/Desktop/BTP%20P1.1/auto_subjective_grader/DEPLOY_VERCEL_CLOUD_RUN.md)

Hosted run persistence:

- `API_RUNS_ROOT` is still used as the local working directory while a run is executing
- configure `API_RUNS_BUCKET` to mirror completed run metadata and generated PDF reports into Google Cloud Storage
- configure `API_RUNS_PREFIX` if you want those run artifacts under a custom folder inside the bucket

## Current Assumptions

- One page is treated as one question
- Diagram extraction relies on connected-component based cropping
- Formula extraction uses heuristic detection on OCR layout

## Current Limitations

- Multi-step derivations may still be harder than isolated formulas
- OCR quality still strongly affects text, symbols, and labels
- Gemini mode does not yet use the symbolic formula scoring path
- public deployments need durable storage configured if you want run history and PDF downloads to survive Cloud Run instance changes

## Team

The dashboard includes a Team tab with the current project members, roles, and contact links.

## Interfaces

The project now supports two interface directions:

### 1. Streamlit Research Dashboard

Used for rapid prototyping, internal testing, and quick end-to-end experiments.

Run with:

```powershell
.venv\Scripts\python.exe -m streamlit run src\app.py
```

### 2. Product Website Architecture

Used for the professional web version:

- `backend_api/` : FastAPI backend
- `web/` : Next.js frontend

Run the API with:

```powershell
.venv\Scripts\python.exe -m uvicorn backend_api.main:app --reload
```

Run the web app with:

```powershell
cd web
npm install
npm run dev
```

Default local URLs:

- FastAPI: `http://127.0.0.1:8000`
- Next.js: `http://localhost:3000`
- Streamlit: `http://localhost:8501`

## Next Directions

- Improve formula-region detection for complex handwritten derivations
- Separate printed and handwritten result directories
- Add charts, analytics, and richer per-question visualization
- Move reports and artifacts to more scalable persistent storage
