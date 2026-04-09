# Deploy On Vercel + Render

This deployment path keeps:

- `web/` on **Vercel**
- `backend_api/` + `src/` on **Render**

Azure stays only as the handwritten OCR provider through `AZURE_DOCUMENT_INTELLIGENCE_*`
environment variables.

## Why this path

- Vercel is good for the Next.js frontend
- Render gives the backend a direct HTTPS URL
- the browser can upload PDFs directly to the backend without hitting Vercel upload limits

## 1. Deploy the backend on Render

Create a new **Web Service** in Render and connect:

- repository: `vermayuvraj/auto-subjective-grader`
- branch: `main`

Use these settings:

- Environment: `Docker`
- Dockerfile path: `./Dockerfile`
- Root directory: leave blank

### Backend environment variables

Add these in Render:

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

- `https://your-render-backend.onrender.com/api/health`

Expected:

```json
{"status":"ok"}
```

## 2. Deploy the frontend on Vercel

Import the same GitHub repository into Vercel.

Use:

- Framework preset: `Next.js`
- Root directory: `web`

### Frontend environment variables

Add:

- `NEXT_PUBLIC_API_BASE_URL=https://your-render-backend.onrender.com`
- `BACKEND_API_BASE_URL=https://your-render-backend.onrender.com`

Redeploy after saving these variables.

## 3. Test the live site

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

If you use a free Render instance:

- the backend may sleep when idle
- the first request can be slow
- local files in `/tmp` are temporary, so job history and generated files are not permanent across restarts

This is acceptable for demo deployment. For long-term production, move run outputs to persistent object storage.
