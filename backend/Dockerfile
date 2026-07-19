# ---------- Backend Dockerfile ----------
# Place this file at: backend/Dockerfile
# Assumes: backend/requirements.txt and backend/app/main.py with `app = FastAPI()`
# Adjust the two marked lines below if your structure differs.

FROM python:3.11-slim AS base

# Prevents .pyc files and forces stdout/stderr to be unbuffered (so Render's logs show up in real time)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps needed by WeasyPrint (PDF export) and asyncpg (Postgres driver)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (separate layer = faster rebuilds when only app code changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Render sets $PORT at runtime; default to 8000 for local `docker build && docker run`
ENV PORT=8000
EXPOSE 8000

# Health check hits the /health endpoint from your OpenAPI spec
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# <-- ADJUST if your FastAPI instance isn't at app.main:app
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
