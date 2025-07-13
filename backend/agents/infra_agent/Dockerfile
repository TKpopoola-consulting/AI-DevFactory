FROM python:3.11-slim

WORKDIR /app

# Install Terraform and Azure CLI for validation
RUN apt-get update && \
    apt-get install -y wget unzip && \
    wget https://releases.hashicorp.com/terraform/1.5.7/terraform_1.5.7_linux_amd64.zip && \
    unzip terraform_1.5.7_linux_amd64.zip -d /usr/local/bin && \
    rm terraform_1.5.7_linux_amd64.zip && \
    curl -sL https://aka.ms/InstallAzureCLIDeb | bash

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]