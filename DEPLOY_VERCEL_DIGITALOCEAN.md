# Deploying The Web Version With Vercel + DigitalOcean

This deployment plan is designed for the current project architecture:

- `web/` -> Next.js frontend deployed on **Vercel**
- `backend_api/` + `src/` -> FastAPI/OCR backend deployed on **DigitalOcean**

This is the best split for the project because:

- Vercel is excellent for the Next.js product UI
- the OCR/report backend is long-running and not a good fit for Vercel serverless functions
- DigitalOcean GitHub Student Pack credit can pay for the backend compute

## What You Need

1. A GitHub repository containing this project
2. A Vercel account connected to GitHub
3. A DigitalOcean account with the GitHub Student Pack credit redeemed
4. Azure Document Intelligence credentials if you want handwritten OCR in production
5. A Gemini API key if you want the LLM path in production
6. A domain from your GitHub Student Pack, if you want a custom public domain

## Recommended Production Layout

- Frontend:
  - `https://your-project.vercel.app`
  - or `https://yourdomain.dev`
- Backend:
  - `https://api.yourdomain.dev`
  - or a temporary DigitalOcean backend URL/IP

## Step 1: Push The Project To GitHub

From the project root:

```powershell
git init
git add .
git commit -m "Prepare project for Vercel + DigitalOcean deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Step 2: Deploy The Frontend To Vercel

1. Open Vercel
2. Click `Add New Project`
3. Import your GitHub repository
4. Set the **Root Directory** to:

```text
web
```

5. Framework should detect as `Next.js`
6. Add environment variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.dev
```

If you are testing before the backend domain is ready, use your temporary backend URL instead.

7. Deploy

## Step 3: Prepare The Backend Secrets

Create a production env file on the server from:

```text
.env.production.example
```

Required values:

```text
ALLOWED_ORIGINS=https://your-project.vercel.app,https://yourdomain.dev
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_azure_key
GEMINI_API_KEY=your_gemini_api_key
EASYOCR_USE_GPU=false
API_RUNS_ROOT=/app/persistent_data/api_runs
```

Notes:

- `ALLOWED_ORIGINS` must include your final frontend URLs
- `POPPLER_PATH` should stay empty on Linux because `poppler-utils` is installed into the container
- `EASYOCR_USE_GPU=false` is the safest default for a CPU droplet

## Step 4: Provision The Backend On DigitalOcean

### Recommended option: Ubuntu Droplet + Docker

This is the most controllable option for your OCR-heavy backend.

Suggested droplet:

- Ubuntu 24.04
- Basic shared CPU
- start small and scale later

Then SSH into the droplet and install Docker:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo systemctl enable docker
sudo systemctl start docker
```

Clone your repo:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO/auto_subjective_grader
```

Create the production env file:

```bash
cp .env.production.example .env.production
nano .env.production
```

Start the backend:

```bash
sudo docker compose -f docker-compose.backend.yml up -d --build
```

This will:

- build the backend container from `Dockerfile`
- expose the API on port `8001`
- persist run files under `./persistent_data`

## Step 5: Verify The Backend

From your browser or SSH shell:

```bash
curl http://YOUR_DROPLET_IP:8001/api/health
```

Expected:

```json
{"status":"ok"}
```

Check runtime config too:

```bash
curl http://YOUR_DROPLET_IP:8001/api/runtime-config
```

That should tell you whether Azure and Gemini secrets are loaded correctly.

## Step 6: Connect The Frontend To The Backend

Once the backend works:

1. Go to Vercel Project Settings
2. Set:

```text
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.dev
```

or temporarily:

```text
NEXT_PUBLIC_API_BASE_URL=http://YOUR_DROPLET_IP:8001
```

3. Redeploy the frontend

## Step 7: Add Custom Domains

### Frontend domain on Vercel

Add your main domain, for example:

```text
yourdomain.dev
```

### Backend subdomain on DigitalOcean

Point a subdomain like:

```text
api.yourdomain.dev
```

to your droplet IP using an `A` record.

Then update:

```text
ALLOWED_ORIGINS=https://yourdomain.dev,https://www.yourdomain.dev
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.dev
```

## Step 8: Add HTTPS For The Backend

Recommended production approach:

- place Nginx in front of the backend container
- issue TLS with Let's Encrypt

At first, you can test with the IP. After that, move to the domain + HTTPS setup.

## Important Deployment Notes

### 1. This backend writes files

The backend stores:

- uploaded PDFs
- OCR outputs
- evaluation JSON
- PDF reports
- job history

That is why the deployment uses a persistent host folder:

```text
./persistent_data
```

### 2. The backend should stay single-worker initially

The current in-memory job cache and locking model is safest with:

```text
--workers 1
```

### 3. Public LLM usage can become expensive

If you expose Gemini mode publicly, users could consume your API quota.

For the first public deployment, consider:

- keep `SBERT` enabled
- disable `LLM` in the UI until you are ready

### 4. Handwritten OCR secrets are now server-side ready

The backend can now use:

- `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`
- `AZURE_DOCUMENT_INTELLIGENCE_KEY`

so your public website does not need to expose those secrets in the form.

## Recommended First Public Rollout

1. Deploy frontend on Vercel
2. Deploy backend on DigitalOcean droplet
3. Enable only:
   - EasyOCR
   - SBERT
4. Test with small batches
5. Then enable handwritten OCR
6. Then enable Gemini later if needed

## Helpful Commands

### Rebuild backend on the droplet

```bash
sudo docker compose -f docker-compose.backend.yml up -d --build
```

### View backend logs

```bash
sudo docker compose -f docker-compose.backend.yml logs -f
```

### Stop backend

```bash
sudo docker compose -f docker-compose.backend.yml down
```
