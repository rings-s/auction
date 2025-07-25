# back/Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=back.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        postgresql-client \
        netcat-openbsd \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn uvicorn[standard]

# Copy project
COPY . .

# Create non-root user FIRST
RUN adduser --disabled-password --gecos '' --uid 1000 appuser

# Create necessary directories and set permissions
RUN mkdir -p /app/media /app/staticfiles /app/logs \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app/logs \
    && chmod -R 755 /app/media \
    && chmod -R 755 /app/staticfiles

# Copy entrypoint script and set permissions
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && chown appuser:appuser /entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/admin/ || exit 1

# Use entrypoint
ENTRYPOINT ["/entrypoint.sh"]