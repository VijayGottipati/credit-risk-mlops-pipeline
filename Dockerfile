FROM python:3.11-slim

WORKDIR /app

ENV PORT=7860
# Smaller batch keeps HF Docker builds a bit faster (SIMULATE_BATCH_SIZE is read in simulate_live_data)
ENV SIMULATE_BATCH_SIZE=150

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# artifacts/ is gitignored; train at build so the API has a model (Hugging Face Spaces, etc.)
RUN python -m src.data_ingest && \
    python -m src.simulate_live_data && \
    python -m src.preprocess && \
    python -m src.train

EXPOSE 7860

# Hugging Face Spaces sets PORT (default 7860); local: docker run -e PORT=8000 -p 8000:8000
CMD sh -c "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-7860}"
