# aq-bot — Bukit Air Quality Reporter
#
# Lean Python image. The bot has no heavy dependencies (no ML, no
# image processing) — that all lives on the M1.

FROM python:3.12-slim

# Non-root user — defensive default for the NAS
RUN useradd --create-home --uid 1000 aq
WORKDIR /app

# Install deps first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bot + dashboard code (same image, different entrypoint per service)
COPY bot_murmurations.py .
COPY murmurations_adapter.py .
COPY vision_analyzer.py .
COPY messages.py .
COPY dashboard.py .
COPY schemas/ ./schemas/

# Persistent data lives outside the image (bind-mounted from docker-compose)
RUN mkdir -p reports profiles images vision_queue/processing \
              vision_queue/done vision_queue/failed && \
    chown -R aq:aq /app

USER aq

EXPOSE 5055

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5055/health').read()"

CMD ["python", "bot_murmurations.py"]
