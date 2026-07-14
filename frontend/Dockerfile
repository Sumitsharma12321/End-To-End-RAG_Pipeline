# ================================================================
# FRONTEND DOCKERFILE
# Streamlit Frontend
# ================================================================

FROM python:3.11-slim

LABEL maintainer="Smart Document Insights"
LABEL version="1.0"
LABEL description="Streamlit Frontend"

# ----------------------------------------------------
# Environment Variables
# ----------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ----------------------------------------------------
# Install System Dependencies
# ----------------------------------------------------
RUN apt-get update && apt-get install -y \
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------
# Upgrade pip
# ----------------------------------------------------
RUN pip install --upgrade pip

# ----------------------------------------------------
# Create Non-Root User
# ----------------------------------------------------
RUN useradd --create-home --shell /bin/bash appuser

# ----------------------------------------------------
# Working Directory
# ----------------------------------------------------
WORKDIR /app

# ----------------------------------------------------
# Copy Requirements First
# (Docker Layer Caching)
# ----------------------------------------------------
COPY requirements.txt .

# ----------------------------------------------------
# Install Python Packages
# ----------------------------------------------------
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------------
# Copy Frontend Source Code
# ----------------------------------------------------
COPY . .

# ----------------------------------------------------
# Set Ownership
# ----------------------------------------------------
RUN chown -R appuser:appuser /app

USER appuser

# ----------------------------------------------------
# Streamlit Configuration
# ----------------------------------------------------
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# ----------------------------------------------------
# Expose Port
# ----------------------------------------------------
EXPOSE 8501

# ----------------------------------------------------
# Health Check
# ----------------------------------------------------
HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=30s \
            --retries=3 \
CMD curl -f http://localhost:8501/_stcore/health || exit 1

# ----------------------------------------------------
# Start Streamlit
# ----------------------------------------------------
# ----------------------------------------------------

CMD ["streamlit", "run", "streamlit_app/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]