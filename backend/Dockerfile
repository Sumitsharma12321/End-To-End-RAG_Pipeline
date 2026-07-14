# ================================================================
# BACKEND DOCKERFILE
# FastAPI + ChromaDB + Sentence Transformers + Groq
# ================================================================

# =========================
# Stage 1 : Builder
# =========================
FROM python:3.11-slim AS builder

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip wheel

WORKDIR /install

# Copy only requirements first (Docker cache optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install \
    --no-cache-dir \
    --prefix=/install/packages \
    -r requirements.txt


# =========================
# Stage 2 : Runtime
# =========================
FROM python:3.11-slim

LABEL maintainer="Smart Documents Insights"
LABEL version="1.0"
LABEL description="FastAPI Backend"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Runtime packages
RUN apt-get update && apt-get install -y \
    libgomp1 \
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages
COPY --from=builder /install/packages /usr/local

# Create non-root user
RUN useradd -ms /bin/bash appuser

WORKDIR /app

# Copy backend source code
COPY . .

# Create required directories
RUN mkdir -p \
    chroma_db \
    uploaded_docs \
    .cache/sentence_transformers

# Give permissions
RUN chown -R appuser:appuser /app

USER appuser

# Sentence Transformer cache
ENV SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence_transformers

# Download embedding model during build
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Expose FastAPI port
EXPOSE 8000

# Health Check
HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=40s \
            --retries=3 \
CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]