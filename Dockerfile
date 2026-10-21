# Production Dockerfile for Placement Management System
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000 \
    PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc

# Set working directory
WORKDIR /app

# Install security updates and curl for container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create non-root system user and necessary runtime directories
RUN useradd -u 1001 -m -s /bin/bash appuser && \
    mkdir -p /app/instance /app/uploads /tmp/prometheus_multiproc && \
    chown -R appuser:appuser /app /tmp/prometheus_multiproc && \
    chmod 777 /tmp/prometheus_multiproc

# Switch to non-root user
USER appuser

# Expose HTTP port
EXPOSE 5000

# Healthcheck targeting /health endpoint
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Production WSGI server command
# Note: Using 1 worker with 4 threads for optimal concurrent request handling,
# ensuring zero SQLite lock contention and clean in-memory Prometheus metrics.
# (If multi-worker gunicorn is desired, set PROMETHEUS_MULTIPROC_DIR)
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
