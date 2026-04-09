# Deploy On Vercel + Hugging Face Spaces

This is the clean no-card deployment path for the web version:

- `web/` on **Vercel**
- `backend_api/` + `src/` on **Hugging Face Docker Spaces**

Azure stays in the project only as the handwritten OCR provider through:

- `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`
- `AZURE_DOCUMENT_INTELLIGENCE_KEY`

## Why this path

- Vercel is a strong fit for the Next.js frontend
- Hugging Face Spaces support arbitrary Dockerfiles, including FastAPI backends
- Spaces provide a public HTTPS URL, so the browser can call the backend directly
- this avoids the Vercel upload-proxy size limit and avoids Azure hosting entirely

Official references:

- Hugging Face Spaces overview: [https://huggingface.co/docs/hub/spaces-overview](https://huggingface.co/docs/hub/spaces-overview)
- Docker Spaces: [https://huggingface.co/docs/hub/en/spaces-sdks-docker](https://huggingface.co/docs/hub/en/spaces-sdks-docker)
- GitHub sync for Spaces: [https://huggingface.co/docs/hub/spaces-github-actions](https://huggingface.co/docs/hub/spaces-github-actions)

## Free-tier notes

Hugging Face documents that free Spaces provide:

- 2 CPU cores
- 16 GB RAM
- 50 GB non-persistent disk

This is suitable for a demo deployment. Generated reports and temporary files should be treated as non-persistent.

## 1. Create the backend Space

In Hugging Face:

1. Create a new **Space**
2. Choose:
   - Owner: your profile
   - Space name: for example `auto-subjective-grader-backend`
   - SDK: `Docker`
   - Visibility: `Public` or `Private`, depending on your need

After the Space is created, it will have a repository like:

- `https://huggingface.co/spaces/YOUR_USERNAME/auto-subjective-grader-backend`

## 2. Sync this GitHub repo to the Space

The simplest path is:

1. Add the Space as another Git remote locally, or
2. Use GitHub Actions to sync `main` to the Space

Hugging Face documents the GitHub Actions sync workflow here:

- [Managing Spaces with GitHub Actions](https://huggingface.co/docs/hub/spaces-github-actions)

You will need:

- a Hugging Face access token with write access
- a GitHub secret named `HF_TOKEN`

## 3. Configure the Space for Docker

The Space repository needs Docker Space metadata in its `README.md` front matter, including:

```yaml
---
title: Auto Subjective Grader Backend
emoji: "🚀"
colorFrom: blue
colorTo: pink
sdk: docker
app_port: 8001
---
```

Then the existing backend `Dockerfile` can be used directly.

## 4. Backend environment variables

Set these as Space variables or secrets:

- `PORT=8001`
- `API_RUNS_ROOT=/tmp/api_runs`
- `ALLOWED_ORIGINS=https://your-vercel-project.vercel.app,https://yourdomain.dev`
- `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/`
- `AZURE_DOCUMENT_INTELLIGENCE_KEY=your_azure_key`
- `GEMINI_API_KEY=your_gemini_api_key`
- `EASYOCR_USE_GPU=false`

Optional:

- `POPPLER_PATH=`

After deploy, verify:

- `https://YOUR_SPACE_SUBDOMAIN.hf.space/api/health`

Expected:

```json
{"status":"ok"}
```

## 5. Deploy the frontend on Vercel

Import the same GitHub repository into Vercel.

Use:

- Framework preset: `Next.js`
- Root directory: `web`

### Frontend environment variables

Add:

- `NEXT_PUBLIC_API_BASE_URL=https://YOUR_SPACE_SUBDOMAIN.hf.space`
- `BACKEND_API_BASE_URL=https://YOUR_SPACE_SUBDOMAIN.hf.space`

Redeploy after saving these variables.

## 6. Test the live site

Check:

- Home
- Documentation
- Team
- Evaluate

For evaluation:

- upload one ideal PDF
- upload one rubric JSON
- upload one student PDF

## Important note

On a free Space:

- cold starts can happen
- local files under `/tmp` are not persistent
- generated reports and run history are demo-grade unless you later add persistent storage

This path is intended to get the product-style web version live without a payment-method gate.
