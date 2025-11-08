# ---- Base with build deps ----
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps for wheels (psycopg2 etc.); remove if not needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---- Build wheel cache (faster installs) ----
FROM base AS builder
COPY requirements.txt .
RUN pip wheel --wheel-dir /wheels -r requirements.txt

# ---- Runtime image (small, non-root) ----
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UVICORN_WORKERS=2 \
    PORT=8000 \
    APP_MODULE=app.main:app

# Create non-root user
RUN useradd -m -u 10001 appuser
WORKDIR /app

# Only runtime libs
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy wheels and install
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --find-links=/wheels -r requirements.txt

# Copy source
COPY . .
COPY assets/ /assets/

USER appuser
EXPOSE 8000

# Gunicorn with Uvicorn workers (prod)
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60", \
     "--access-logfile", "-", "--error-logfile", "-", \
     "app.main:app"]
