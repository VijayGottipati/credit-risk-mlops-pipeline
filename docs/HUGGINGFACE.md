# Hugging Face Spaces (Docker) Setup

Your Space: [vijaygottipati/credit-risk-mlops-pipeline](https://huggingface.co/spaces/vijaygottipati/credit-risk-mlops-pipeline)

Official reference: [Spaces — Docker](https://huggingface.co/docs/hub/spaces-sdks-docker)

## What this repo does on HF

- **SDK:** Docker (root `Dockerfile`).
- **Process:** Image build runs ingest → simulate → preprocess → **train** (so `artifacts/` exists), then starts **FastAPI** with **Uvicorn**.
- **Port:** Hugging Face sets `PORT` (usually **7860**). The `CMD` in the Dockerfile uses `${PORT:-7860}`.

## One-time Space configuration

1. **Create / open the Space** → [Create new Space](https://huggingface.co/new-space).
2. **Owner / name:** e.g. `vijaygottipati` / `credit-risk-mlops-pipeline`.
3. **SDK:** **Docker** (not Gradio / not Python default).
4. **Visibility:** Public (typical for portfolio).
5. **Hardware:** CPU basic is enough; first **build** can take **several minutes** (pip + training).

## Connect GitHub ↔ Hugging Face (three patterns)

You may read: *add the Space as a git remote, push once, then use a GitHub Action to sync.* That is **one** valid setup, but **not required** for this project.

### A) Hugging Face pulls from GitHub (**recommended**)

Keep **GitHub** as the only place you `git push` day-to-day. In the Space:

1. **Settings** → **Repository** (or create the Space **from GitHub**).
2. Select **`VijayGottipati/credit-risk-mlops-pipeline`**, branch **`main`**, path **`/`** (repo root).
3. **Save**.

Hugging Face then **builds from your GitHub repo** when `main` updates. You do **not** need a second `git remote` named `hf` for normal work, and you usually **do not** need a separate “sync” Action—HF’s integration is the sync.

### B) HF Space as a **second** `git` remote (optional)

For one-off pushes or workflows without the Repository link:

```bash
git remote add hf https://huggingface.co/spaces/vijaygottipati/credit-risk-mlops-pipeline.git
# push requires HF token (Settings → Access Tokens)
git push hf main
```

You still keep **`origin`** → GitHub. You must remember to push **both** when you want both sites updated.

### C) GitHub Action pushes to HF (optional, advanced)

A workflow can `git push` to `huggingface.co` using a **`HF_TOKEN`** secret. That is **redundant** if you already use **(A)**, because HF already rebuilds when GitHub changes. Use **(C)** only if you cannot use HF’s GitHub integration or you need extra pre-deploy steps.

**Do not** combine **(A)** and **(C)** in a confusing way (double builds / races). Prefer **(A)** unless you have a concrete reason.

---

## Connect the repo in the Space UI (method A)

1. Space → **Settings** → **Repository** (or create Space from GitHub).
2. Point to: `VijayGottipati/credit-risk-mlops-pipeline`, branch **`main`**, path **`/`** (repo root).
3. **Save** → HF will build from your **`Dockerfile`** on each push to `main`.

## After deploy — URLs

Replace with your username/space name if different:

- **API docs (Swagger):** `https://vijaygottipati-credit-risk-mlops-pipeline.hf.space/docs`
- **Health:** `https://vijaygottipati-credit-risk-mlops-pipeline.hf.space/health`

Pattern: `https://<org>-<space-name>.hf.space` (hyphens, not slashes).

## Environment variables (optional)

Space → **Settings** → **Variables and secrets**

| Variable | Purpose |
|----------|---------|
| *(none required)* | Inference works without W&B. |
| `WANDB_API_KEY` | Only if you want runs logged from the Space (unusual for serving-only). |

Do **not** commit secrets; use HF secrets UI.

## Troubleshooting

| Issue | What to do |
|-------|------------|
| **Build timeout** | Free tier builds can time out if install + train is too heavy. Reduce load in Dockerfile (smaller `SIMULATE_BATCH_SIZE`, fewer trees in `train.py`) or upgrade hardware in Space settings. |
| **502 / won’t start** | Check **Logs** tab on the Space; confirm Uvicorn binds `0.0.0.0` and uses `$PORT`. |
| **Wrong SDK** | Space must be **Docker**, not Gradio template. |
| **README card not pretty** | The repo `README.md` includes YAML **frontmatter** at the top for the Space card (`sdk: docker`, `app_port: 7860`). |

## Relationship to GitHub Actions

- **GitHub Actions:** scheduled training, drift, artifacts, CI.
- **Hugging Face:** hosts the **live API** for demos. They complement each other; HF does not run your `.github/workflows` by default.
