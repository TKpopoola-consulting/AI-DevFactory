FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for validation tools
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Install Node.js validator dependencies
RUN cd validation/nodejs_validator && npm install

HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]