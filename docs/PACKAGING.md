# Packaging & External Services Setup

This guide lists **what you need**, **what is optional**, and **exact steps** to finish W&B, Slack, Google Drive (DVC), GitHub secrets, and Hugging Face Spaces.

---

## 1) What is required vs optional

| Item | Required for local dev? | Required for GitHub Actions? | Required for HF Spaces deploy? |
|------|-------------------------|--------------------------------|--------------------------------|
| Python 3.11 + `pip install -r requirements.txt` | Yes | Yes (CI installs it) | Yes (Dockerfile installs it) |
| `WANDB_API_KEY` | No (training/eval skip W&B if unset) | No (optional experiment tracking) | No |
| `SLACK_WEBHOOK_URL` | No | No (only `monitor.yml` Slack step) | No |
| DVC + Google Drive | No | No (workflows regenerate data + train) | No |
| GitHub repo + secrets | No | Yes if you use W&B/Slack in Actions | No (push image or connect repo) |

**Bottom line:** You can run and demo everything **without** W&B, Slack, or Drive. Add them when you want portfolio polish and automation alerts.

---

## 2) Weights & Biases (W&B)

**What it is:** Logs hyperparameters, metrics, and optional charts for each training/eval run.

### Get an API key

1. Create a free account at [https://wandb.ai](https://wandb.ai).
2. User settings → **API keys** → copy your key.

### Local development

1. Copy `.env.example` to `.env` (never commit `.env`).
2. Set:
   ```env
   WANDB_API_KEY=paste_your_key_here
   ```
3. Load env before training (PowerShell):
   ```powershell
   Get-Content .env | ForEach-Object { if ($_ -match '^([^#][^=]+)=(.*)$') { Set-Item -Path "env:$($matches[1])" -Value $matches[2].Trim() } }
   ```
   Or install `python-dotenv` and add a one-liner in scripts if you prefer.

Alternatively run once per session:
```powershell
$env:WANDB_API_KEY = "your_key"
python -m src.train
python -m src.evaluate
```

### GitHub Actions

1. Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
2. Name: `WANDB_API_KEY`, value: your key.
3. The `train.yml` workflow already passes `WANDB_API_KEY` into the job.

**If you skip this:** training and evaluation still run; W&B logging is skipped.

---

## 3) Slack (drift alerts)

**What it is:** `monitor.yml` can POST a message when drift triggers retraining.

### Create an Incoming Webhook

1. Slack workspace → [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** (From scratch).
2. **Incoming Webhooks** → Activate → **Add New Webhook to Workspace** → pick channel → copy URL.

### GitHub Actions

1. New secret: `SLACK_WEBHOOK_URL` = `https://hooks.slack.com/services/...`

### Local testing (optional)

```powershell
$env:SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/..."
curl -X POST -H "Content-Type: application/json" --data '{"text":"Test from ML project"}' $env:SLACK_WEBHOOK_URL
```

**If you skip this:** drift workflow still runs; the Slack step does nothing useful without the secret (workflow uses `if` on the secret).

---

## 4) DVC + Google Drive (data versioning)

**What it is:** Version large datasets **outside** Git (Git stores pointers; Drive stores blobs).

### Install DVC with Drive support

```powershell
pip install dvc dvc-gdrive
```

### One-time project setup

This repository **already includes** `dvc init`. If you cloned fresh and `.dvc` is missing, run once:

```powershell
dvc init
```

### Connect Google Drive (fastest)

1. Create a folder in **Google Drive** and copy its ID from the URL (the part after `/folders/`).

2. From the **repo root** (`credit-risk-mlops-pipeline`), run:

```powershell
.\scripts\setup_dvc_gdrive.ps1 -FolderId "PASTE_FOLDER_ID_HERE"
```

You can paste the **full folder URL**; the script extracts the ID.

3. First `dvc push` opens a **browser** so you can sign in to Google (only you can do this step).

### Connect Google Drive (manual commands)

If you prefer not to use the script:

```powershell
dvc remote add -f -d gdrive_remote gdrive://FOLDER_ID
dvc remote modify gdrive_remote gdrive_use_service_account false
```

Replace `FOLDER_ID` with your Drive folder ID.

### Google blocked the sign-in (“This app is blocked” / “Access denied”)

This is common. DVC talks to Drive through Google’s OAuth; the default client can show as **unverified**, or your **school/work Google Workspace** can block third‑party Drive access.

**Try these in order:**

1. **Use a personal Gmail account** (not a work/school account) when the browser opens, and make sure the Drive folder lives under that same account (or is shared appropriately).

2. **On the scary screen**, look for **“Advanced”** → **“Go to … (unsafe)”** or **“Continue”**. Google shows that for any app not in their public verification program; for a **personal portfolio project**, proceeding is normal. ([Google’s OAuth warnings](https://developers.google.com/identity/protocols/oauth2/production-readiness/sensitive-scope-verification) apply mostly to public apps.)

3. **Workspace / school account:** Your admin may block “Drive API” or “third‑party apps.” You cannot fix that from DVC alone. Options: ask IT for an exception, use **personal Gmail + a folder in that account**, or skip Drive (see below).

4. **Service account (advanced):** DVC can use a **Google Cloud service account** JSON key and shared folder access instead of your user login. See [DVC Google Drive remote](https://dvc.org/doc/user-guide/data-management/remote-storage/google-drive#service-account) and set `gdrive_use_service_account true` plus the credentials path. Use only if you are comfortable with GCP IAM.

5. **Skip Drive for the portfolio:** Your project already reproduces data via **`dvc repro`** / scripts. For your CV you can say **“DVC pipeline + Git-tracked `dvc.lock`”** and host large blobs on **GitHub Actions artifacts**, **Hugging Face**, or **Cloudflare R2** later—Drive is optional.

After any successful auth, run `dvc push` again from the repo root.

### Track your data files

After data exists under `data/`:

```powershell
dvc add data/raw/historical_credit_data.csv
dvc add data/raw/live_credit_applications.csv
dvc add data/processed/train_ready.csv
dvc add data/processed/live_ready.csv
git add data/*.dvc .gitignore
git commit -m "Track datasets with DVC"
dvc push
```

**If you skip this:** GitHub Actions still builds data from scripts; you lose “exact data snapshot in Drive” until you add DVC.

---

## 5) GitHub repository checklist

1. Create repo on GitHub (empty, no README, or push existing).
2. Add remote and push:

```powershell
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Secrets summary (Settings → Secrets → Actions)

| Secret name | Purpose |
|-------------|---------|
| `WANDB_API_KEY` | Optional W&B in `train.yml` |
| `SLACK_WEBHOOK_URL` | Optional Slack in `monitor.yml` |

`GITHUB_TOKEN` is **automatic**; do not create it manually.

### Enable Actions

Repo → **Actions** → enable workflows if prompted. Scheduled `monitor.yml` runs only on the **default branch** on GitHub’s schedule.

---

## 6) Hugging Face Spaces (Docker + FastAPI)

**What it is:** Free hosting for a public **Space** with a URL you can put on your CV.

### Create the Space

1. [https://huggingface.co/new-space](https://huggingface.co/new-space)
2. Name, license, **SDK: Docker** (matches this repo’s `Dockerfile`).
3. Create empty Space, then either:
   - **Push this git repo** as the Space repo (HF gives you a git URL), or
   - Connect GitHub (HF can sync from GitHub if you enable integration).

### Port

Hugging Face expects the app to listen on **`7860`** by default. This repo’s `Dockerfile` uses the `PORT` environment variable (defaults to `7860`).

### Model artifacts inside the image

`artifacts/` is gitignored. The **Dockerfile** runs a training pipeline at **image build** so `model.joblib` and related files exist inside the container without committing secrets.

First build can take several minutes (pip + train).

### Environment variables on HF (optional)

Space → **Settings** → **Variables and secrets**:

- `WANDB_API_KEY` — only if you want W&B from Space (unusual for serving-only).

Usually you **do not** need W&B on the Space for inference.

### Smoke test after deploy

```text
https://YOUR_USER-YOUR_SPACE.hf.space/health
https://YOUR_USER-YOUR_SPACE.hf.space/docs
```

---

## 7) Other things people forget

| Item | Why it matters |
|------|----------------|
| **`.env` never in Git** | Prevents leaking API keys. `.gitignore` already ignores `.env`. |
| **`requirements.txt` pinned (optional)** | Reproducible installs; pin versions when you freeze for production. |
| **Public vs private data** | UCI/synthetic is fine; do not commit real PII. |
| **HF Space visibility** | Public Space = anyone can hit `/predict`; OK for demo; add rate limits later if needed. |
| **Git LFS** | Alternative to DVC for large files; DVC + Drive is already documented above. |

---

## 8) Minimal “done” order (recommended)

1. `python -m venv .venv` → activate → `pip install -r requirements.txt`
2. `python -m scripts.portfolio_demo` — works with **no** secrets
3. `git init` + push to GitHub — CI runs
4. Add `WANDB_API_KEY` secret — optional polish
5. Add `SLACK_WEBHOOK_URL` secret — optional alerts
6. `dvc init` + Drive remote + `dvc push` — optional data lineage story
7. Create HF Space (Docker), push code, verify `/health` and `/docs`

After that you are ready for resume/LinkedIn copy (separate step).
