# Hugging Face Space — setup checklist (5 minutes)

Your repo is already **Docker-ready** (`Dockerfile`, `README` frontmatter, port `7860`). You only need to wire the Space to GitHub **once** in the browser.

**Target Space:** [vijaygottipati/credit-risk-mlops-pipeline](https://huggingface.co/spaces/vijaygottipati/credit-risk-mlops-pipeline)

---

## Before you start

- [ ] Code is on GitHub: `VijayGottipati/credit-risk-mlops-pipeline`, branch **`main`**.
- [ ] You are logged into [huggingface.co](https://huggingface.co) (same account that owns the Space).

---

## Steps (do in order)

1. **Open your Space**  
   [https://huggingface.co/spaces/vijaygottipati/credit-risk-mlops-pipeline](https://huggingface.co/spaces/vijaygottipati/credit-risk-mlops-pipeline)

2. **Settings → Repository** (left sidebar on the Space page).

3. **Connect a repository**
   - **User or organization:** `VijayGottipati` (or pick from list).
   - **Repository:** `credit-risk-mlops-pipeline`.
   - **Branch:** `main`.
   - **Path:** `/` (repository root).

4. **SDK** must be **Docker** (if you see “Gradio” or “Static”, switch Space type or recreate with Docker).

5. **Save** → Hugging Face will start a **build** (several minutes the first time: `pip` + training in `Dockerfile`).

6. **Watch build logs**  
   Space → **Logs** tab until you see the server listening (Uvicorn).

7. **Smoke test**
   - Health: `https://vijaygottipati-credit-risk-mlops-pipeline.hf.space/health`
   - API docs: `https://vijaygottipati-credit-risk-mlops-pipeline.hf.space/docs`

   If the subdomain differs, use the **App** URL shown on your Space page.

---

## If the Space does not exist yet

1. [Create a new Space](https://huggingface.co/new-space).
2. Owner: **vijaygottipati**, name: **credit-risk-mlops-pipeline** (or any name; then use that URL in docs).
3. **SDK:** **Docker**.
4. **Visibility:** Public (typical).
5. **Create** → then follow **Settings → Repository** as above.

---

## If build fails

| Symptom | What to try |
|--------|-------------|
| Timeout | Upgrade hardware in Space settings, or reduce training in `Dockerfile` / `src/train.py`. |
| Wrong port | Ensure `CMD` uses `$PORT`; this repo already does. |
| Missing model | `Dockerfile` trains at build; check **Logs** for Python errors. |

More detail: [HUGGINGFACE.md](HUGGINGFACE.md)

---

## After setup

Every **`git push` to `main`** on GitHub triggers a **new HF build** (when Repository is connected). No extra GitHub Action required for basic sync.
