# Deploy On Vercel + Google Cloud Run

This is the final deployment path for the web version:

- `web/` on **Vercel**
- `backend_api/` + `src/` on **Google Cloud Run**

Azure stays in the project only as the handwritten OCR provider through:

- `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`
- `AZURE_DOCUMENT_INTELLIGENCE_KEY`

## Why this path

- Vercel is a strong fit for the professional Next.js frontend
- Cloud Run gives the backend a direct HTTPS URL
- the browser can upload PDFs directly to the backend without hitting the Vercel upload-proxy size limit
- Cloud Run supports containerized FastAPI services cleanly

## Important architecture note

The hosted website uses the synchronous `/api/evaluate` path instead of the background-job `/api/jobs` path.

That is intentional:

- local Streamlit and local web development can use background jobs
- production serverless hosting is more reliable when one request owns the full evaluation lifecycle

## 1. Google Cloud prerequisites

Before you deploy, make sure:

- the target Google Cloud project is linked to an **active** Cloud Billing account
- the following APIs are enabled:
  - `run.googleapis.com`
  - `cloudbuild.googleapis.com`
  - `artifactregistry.googleapis.com`

If `gcloud services enable ...` fails with a billing error, the project is not properly linked to billing yet.

## 2. Deploy the backend to Cloud Run

From the repository root:

```powershell
gcloud run deploy auto-subjective-grader-api `
  --source . `
  --project YOUR_PROJECT_ID `
  --region asia-south1 `
  --allow-unauthenticated `
  --memory 4Gi `
  --cpu 2 `
  --timeout 3600 `
  --concurrency 1 `
  --max-instances 1 `
  --port 8001 `
  --set-env-vars API_RUNS_ROOT=/tmp/api_runs,EASYOCR_USE_GPU=false,ALLOWED_ORIGINS=* `
  --set-env-vars GEMINI_API_KEY=YOUR_GEMINI_KEY
```

Optional handwritten OCR variables:

```powershell
--set-env-vars AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/,AZURE_DOCUMENT_INTELLIGENCE_KEY=YOUR_AZURE_KEY
```

After deployment, verify:

- `https://YOUR_BACKEND_URL/api/health`

Expected:

```json
{"status":"ok"}
```

## 3. Deploy the frontend on Vercel

Import the same GitHub repository into Vercel.

Use:

- Framework preset: `Next.js`
- Root directory: `web`

### Frontend environment variables

Add:

- `NEXT_PUBLIC_API_BASE_URL=https://YOUR_BACKEND_URL`
- `BACKEND_API_BASE_URL=https://YOUR_BACKEND_URL`

Then redeploy the frontend.

## 4. Test the live site

Check:

- Home
- Documentation
- Team
- Evaluate

For evaluation:

- upload one ideal PDF
- upload one rubric JSON
- upload one student PDF

## Runtime notes

- `API_RUNS_ROOT=/tmp/api_runs` is ephemeral
- generated files and history are not durable across container replacements
- this is acceptable for demo deployment

For durable production storage later, move reports and run artifacts to Cloud Storage.
