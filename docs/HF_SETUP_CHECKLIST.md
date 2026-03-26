# Hugging Face Space — setup checklist

Your repo is **Docker-ready**. Hugging Face’s **documented** way to keep a Space in sync with GitHub is **`git push` to the Space** (often automated with **GitHub Actions**), **not** a “Repository” dropdown — many accounts **do not** show “connect GitHub repo” under Space Settings. Use **Method A** below.

**Target Space:** [vijaygottipati/credit-risk-mlops-pipeline](https://huggingface.co/spaces/vijaygottipati/credit-risk-mlops-pipeline)

Official reference: [Managing Spaces with GitHub Actions](https://huggingface.co/docs/hub/spaces-github-actions)

---

## Method A — GitHub Actions + `HF_TOKEN` (recommended)

This repo includes `.github/workflows/sync-huggingface.yml`. It pushes `main` to your Space on every push to `main`.

### One-time steps

1. **Create a Hugging Face access token** with **Write** permission:  
   [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

2. **Add a GitHub Actions secret** on your repo:  
   GitHub → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**  
   - **Name:** `HF_TOKEN`  
   - **Value:** paste the HF token  

3. **Push to `main`** (or open **Actions** → **Sync to Hugging Face Space** → **Run workflow**).  
   The workflow runs and uploads your code to the Space; HF then **builds the Docker image**.

4. Open the Space → **Logs** and wait until the app is **Running**.

5. **Smoke test**
   - `https://vijaygottipati-credit-risk-mlops-pipeline.hf.space/health`
   - `https://vijaygottipati-credit-risk-mlops-pipeline.hf.space/docs`  

   Use the exact **App** URL from your Space page if it differs.

### If you saw “rejected (fetch first)” / non-fast-forward

The Space’s git history (e.g. a README created on huggingface.co) does not match GitHub’s. The workflow uses **`git push --force`** so **GitHub `main` wins**. Re-run **Actions → Sync to Hugging Face Space** after pulling the latest workflow.

To do the same locally once:

```bash
git remote add space https://huggingface.co/spaces/vijaygottipati/credit-risk-mlops-pipeline.git
git push --force space main
```

---

## Method B — Manual `git` only (no Actions)

From your project folder:

```bash
git remote add space https://huggingface.co/spaces/vijaygottipati/credit-risk-mlops-pipeline.git
git push space main
```

Use a [HF token](https://huggingface.co/settings/tokens) as the password when prompted (HTTPS), or:

`git push https://USER:TOKEN@huggingface.co/spaces/vijaygottipati/credit-risk-mlops-pipeline.git main`

Repeat **`git push space main`** whenever you want to update the Space.

---

## “I can’t find Repository in Space Settings”

That is **normal**. The UI varies by account and product updates. You **do not** need that screen if you use **Method A** or **Method B**.

If your Space UI *does* offer a GitHub connection under **Settings**, you can use it as an alternative — but **do not** also run a conflicting second sync without understanding it (avoid double pushes / confusing builds).

---

## Space must be Docker

When you [create the Space](https://huggingface.co/new-space), choose **SDK: Docker**. This repo expects a root **`Dockerfile`**.

---

## If build fails

| Symptom | What to try |
|--------|-------------|
| Workflow fails: `HF_TOKEN` | Add the **Actions** secret `HF_TOKEN` (see Method A). |
| Timeout on HF | Smaller `SIMULATE_BATCH_SIZE` in `Dockerfile`, or upgrade Space hardware. |
| 502 | **Logs** on the Space; confirm Uvicorn binds `0.0.0.0` and `$PORT`. |

More detail: [HUGGINGFACE.md](HUGGINGFACE.md)

---

## Local check (optional)

```bash
python -m scripts.verify_hf_space_ready
```
