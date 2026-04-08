# Deploying The Web Version With Vercel + Azure For Students

This is the recommended deployment path when:

- the frontend should be public and polished
- the backend needs a real long-running environment for OCR and PDF/report generation
- you do not want to use a personal credit card

## Final Architecture

- `web/` -> **Vercel**
- `backend_api/` + `src/` -> **Azure App Service (Linux, custom container)**
- container image -> **Azure Container Registry (ACR)**

## Why This Path Fits The Project

The backend performs:

- OCR
- formula extraction
- diagram processing
- long-running evaluation jobs
- PDF report generation
- local artifact storage

That makes the backend a poor fit for serverless-only hosting.

## What You Need Before Starting

1. Azure for Students subscription
2. GitHub repository already pushed
3. Vercel account connected to GitHub
4. Azure Document Intelligence credentials if you want handwritten OCR
5. Gemini API key if you want the LLM path

## Part 1: Deploy Frontend On Vercel

1. Import the GitHub repository into Vercel
2. Set the **Root Directory** to:

```text
web
```

3. Framework preset:

```text
Next.js
```

4. Add this environment variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.dev
```

If the backend domain is not ready yet, use a temporary Azure backend URL and change it later.

5. Deploy

## Part 2: Create Azure Resources

### Step A: Create A Resource Group

Suggested values:

- Resource group: `auto-grader-rg`
- Region: `Central India`

### Step B: Create Azure Container Registry

Create:

- Resource type: `Azure Container Registry`
- Name: something unique like `autograderyvacr`
- SKU: `Basic`
- Region: same as resource group

After creation:

1. Open the registry
2. Go to `Access keys`
3. Enable `Admin user`
4. Copy:
   - Login server
   - Username
   - Password

These will be used in GitHub Actions secrets.

### Step C: Create App Service Plan

Create:

- Resource type: `App Service Plan`
- OS: `Linux`
- Region: same as registry
- Pricing tier: start with `B1`

### Step D: Create The Backend Web App

Create:

- Resource type: `Web App`
- Publish: `Container`
- Operating system: `Linux`
- Region: same as resource group
- App Service plan: the Linux plan you created
- Name: something unique like `auto-grader-api-yv`

At container stage:

- Image source: `Azure Container Registry`
- Registry: your ACR
- Image: `auto-subjective-grader-backend`
- Tag: `latest`

If the image is not available yet, create the web app after pushing the image, or update the container settings after the first push.

## Part 3: Add GitHub Secrets

In your GitHub repository:

`Settings -> Secrets and variables -> Actions`

Add:

```text
AZURE_ACR_LOGIN_SERVER
AZURE_ACR_USERNAME
AZURE_ACR_PASSWORD
```

Use the values from Azure Container Registry access keys.

## Part 4: Push The Backend Container From GitHub Actions

This repository now includes:

```text
.github/workflows/backend-acr.yml
```

That workflow:

- builds the backend image from `Dockerfile`
- pushes it to ACR
- tags it as:
  - `latest`
  - commit SHA

To trigger it:

1. Push to `main`
2. Or run the workflow manually from the `Actions` tab

After the workflow succeeds, the container image will exist in ACR.

## Part 5: Configure Azure App Service Settings

In the Azure Web App:

`Settings -> Environment variables`

Add these:

```text
WEBSITES_PORT=8001
WEBSITES_ENABLE_APP_SERVICE_STORAGE=true
API_RUNS_ROOT=/home/api_runs
ALLOWED_ORIGINS=https://your-vercel-project.vercel.app,https://yourdomain.dev
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_azure_key
GEMINI_API_KEY=your_gemini_api_key
EASYOCR_USE_GPU=false
```

Notes:

- `WEBSITES_PORT=8001` is required because the container listens on port `8001`
- `WEBSITES_ENABLE_APP_SERVICE_STORAGE=true` is important so the app can keep files under `/home`
- `API_RUNS_ROOT=/home/api_runs` keeps run artifacts in persistent App Service storage
- `EASYOCR_USE_GPU=false` is correct for a normal CPU Azure App Service plan

## Part 6: Point Vercel To The Azure Backend

After the Azure backend is live, update the Vercel env var:

```text
NEXT_PUBLIC_API_BASE_URL=https://auto-grader-api-yv.azurewebsites.net
```

or your custom backend domain:

```text
https://api.yourdomain.dev
```

Then redeploy the frontend.

## Part 7: Recommended First Public Launch

For the first public rollout:

1. Keep `SBERT` enabled
2. Keep `EasyOCR` enabled
3. Enable Azure handwritten OCR only after checking runtime cost
4. Keep Gemini disabled unless you are ready for public quota usage

## Important Notes

### 1. The backend stores generated files

It writes:

- uploaded PDFs
- OCR outputs
- evaluation JSON
- PDF reports
- run metadata

That is why persistent storage settings matter.

### 2. Start with one backend instance

The current backend uses in-memory job state and a single execution lock, so start with one instance.

### 3. Use App Service before moving to Kubernetes

App Service is simpler and more than enough for the first production deployment.

## What To Do Right Now

1. Create the **Azure Container Registry**
2. Enable **Admin user**
3. Copy:
   - Login server
   - Username
   - Password
4. Add those 3 values as GitHub Actions secrets
5. Run the `Build And Push Backend To ACR` workflow

Once you reach step 3, you can continue immediately from GitHub without needing Docker on your laptop.
