# Multi-stage build for production
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Install Flutter SDK for validation
RUN apt-get update && \
    apt-get install -y curl unzip git && \
    curl -O https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.19.0-stable.tar.xz && \
    tar xf flutter_linux_3.19.0-stable.tar.xz -C /usr/local/ && \
    rm flutter_linux_3.19.0-stable.tar.xz

# Final stage
FROM python:3.11-slim
WORKDIR /app

# Copy installed packages
COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/local/flutter /usr/local/flutter

# Ensure scripts in .local are usable
ENV PATH=/root/.local/bin:/usr/local/flutter/bin:$PATH
ENV FLUTTER_ROOT=/usr/local/flutter

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]