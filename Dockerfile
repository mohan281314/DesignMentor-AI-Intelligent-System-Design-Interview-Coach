# ============================================================
# DesignMentor AI — Backend Dockerfile
# Multi-stage: builder → runtime
# ============================================================

# ── Stage 1: Build dependencies ─────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --user --no-cache-dir -r requirements.txt


# ── Stage 2: Runtime image ───────────────────────────────────
FROM python:3.11-slim AS runtime

# Install runtime system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r designmentor && useradd -r -g designmentor designmentor

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/designmentor/.local

# Copy application source
COPY --chown=designmentor:designmentor . .

# Create necessary directories
RUN mkdir -p uploads temp/pdfs \
 && chown -R designmentor:designmentor /app

# Switch to non-root user
USER designmentor

# Add user local packages to PATH
ENV PATH=/home/designmentor/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command (override in docker-compose for dev hot-reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
