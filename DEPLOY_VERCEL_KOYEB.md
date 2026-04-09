# Deploy On Vercel + Koyeb

This is the clean deployment path for the web version:

- `web/` on **Vercel**
- `backend_api/` + `src/` on **Koyeb**

Azure stays in the project only as the handwritten OCR provider through:

- `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`
- `AZURE_DOCUMENT_INTELLIGENCE_KEY`

## Why this path

- Vercel is a strong fit for the Next.js frontend
- Koyeb gives the backend a direct HTTPS URL
- the browser can upload PDFs directly to the backend without going through a Vercel upload proxy
- the backend can keep using the existing `Dockerfile`

## 1. Deploy the backend on Koyeb

Create a new **Web Service** in Koyeb and connect:

- repository: `vermayuvraj/auto-subjective-grader`
- branch: `main`

Use these settings:

- Deployment method: `GitHub`
- Build method: `Dockerfile`
- Dockerfile path: `./Dockerfile`
- Context / workdir: repository root

Koyeb injects the `PORT` environment variable automatically, and the backend startup script already uses it.

### Backend environment variables

Add these in Koyeb:

- `API_RUNS_ROOT=/tmp/api_runs`
- `ALLOWED_ORIGINS=https://your-vercel-project.vercel.app,https://yourdomain.dev`
- `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/`
- `AZURE_DOCUMENT_INTELLIGENCE_KEY=your_azure_key`
- `GEMINI_API_KEY=your_gemini_api_key`
- `EASYOCR_USE_GPU=false`

Optional:

- `POPPLER_PATH=`

After the service is deployed, verify:

- `https://your-koyeb-backend.koyeb.app/api/health`

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

- `NEXT_PUBLIC_API_BASE_URL=https://your-koyeb-backend.koyeb.app`
- `BACKEND_API_BASE_URL=https://your-koyeb-backend.koyeb.app`

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

On a free backend:

- cold starts may happen when the service has been idle
- temporary files under `/tmp` are not guaranteed to survive restarts
- run history and generated reports are best treated as demo data unless you add persistent storage later

This path is intended to get the product-style web version live quickly without relying on Azure hosting.
