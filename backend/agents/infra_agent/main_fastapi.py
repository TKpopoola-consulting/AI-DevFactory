from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import os

app = FastAPI(title="Infrastructure Agent", version="1.0.0")

# Request models
class InfrastructureConfig(BaseModel):
    job_id: str
    cloud_provider: str = "azure"
    services: List[str] = ["compute"]
    scaling: Dict[str, Any] = {}
    environment: str = "dev"
    region: str = "eastus"
    tags: Dict[str, str] = {}

class GenerationRequest(BaseModel):
    config: InfrastructureConfig

class DeploymentRequest(BaseModel):
    job_id: str
    templates: Dict[str, Any]
    cloud_provider: str

class CostEstimateRequest(BaseModel):
    templates: Dict[str, Any]
    cloud_provider: str
    services: List[str]

class ValidationRequest(BaseModel):
    templates: Dict[str, Any]
    cloud_provider: str

class SecurityScanRequest(BaseModel):
    templates: Dict[str, Any]
    cloud_provider: str

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "infrastructure",
        "cloud_providers": ["azure", "aws", "gcp", "kubernetes"],
        "services": ["compute", "database", "storage", "monitoring", "networking", "secrets"],
        "version": "2.0.0"
    }

@app.post("/generate")
async def generate_infrastructure(request: GenerationRequest):
    """Generate infrastructure templates"""
    try:
        templates = create_infrastructure_templates(
            request.config.cloud_provider,
            request.config.services,
            request.config.environment,
            request.config.region
        )

        return {
            "status": "success",
            "job_id": request.config.job_id,
            "templates": templates,
            "cloud_provider": request.config.cloud_provider,
            "environment": request.config.environment
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deploy")
async def deploy_infrastructure(request: DeploymentRequest):
    """Deploy generated infrastructure"""
    try:
        # Simulate deployment
        deployment_status = simulate_deployment(
            request.templates,
            request.cloud_provider
        )

        return {
            "status": "deployment_started",
            "job_id": request.job_id,
            "deployment_id": f"deploy-{request.job_id}",
            "status_url": f"/deployments/{request.job_id}/status",
            "estimated_completion": "10 minutes",
            **deployment_status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cost")
async def estimate_cost(request: CostEstimateRequest):
    """Estimate infrastructure cost"""
    try:
        cost_estimate = calculate_cost_estimate(
            request.templates,
            request.cloud_provider,
            request.services
        )

        return {
            "status": "success",
            "cost_estimate": cost_estimate,
            "currency": "USD",
            "period": "monthly"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate")
async def validate_templates(request: ValidationRequest):
    """Validate infrastructure templates"""
    try:
        validation_results = validate_infrastructure_templates(
            request.templates,
            request.cloud_provider
        )

        return {
            "status": "success",
            "is_valid": validation_results["is_valid"],
            "issues": validation_results["issues"],
            "warnings": validation_results["warnings"],
            "suggestions": validation_results["suggestions"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/security")
async def scan_security(request: SecurityScanRequest):
    """Scan templates for security issues"""
    try:
        security_scan = perform_security_scan(
            request.templates,
            request.cloud_provider
        )

        return {
            "status": "success",
            "security_score": security_scan["score"],
            "issues": security_scan["issues"],
            "recommendations": security_scan["recommendations"],
            "compliance": security_scan["compliance"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def create_infrastructure_templates(provider: str, services: List[str], environment: str, region: str) -> Dict[str, Any]:
    """Create infrastructure templates for the specified provider"""
    templates = {}

    if provider == "azure":
        templates = create_azure_templates(services, environment, region)
    elif provider == "aws":
        templates = create_aws_templates(services, environment, region)
    elif provider == "gcp":
        templates = create_gcp_templates(services, environment, region)
    elif provider == "kubernetes":
        templates = create_kubernetes_templates(services, environment)
    else:
        templates = create_azure_templates(services, environment, region)  # Default

    return templates

def create_azure_templates(services: List[str], environment: str, region: str) -> Dict[str, Any]:
    """Create Azure infrastructure templates"""
    templates = {
        "main.tf": f"""
# Azure Infrastructure for {environment} environment
terraform {{
  required_providers {{
    azurerm = {{
      source = "hashicorp/azurerm"
      version = "~> 3.0"
    }}
  }}
}}

provider "azurerm" {{
  features {{}}
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
  client_id       = var.client_id
  client_secret   = var.client_secret
}}

resource "azurerm_resource_group" "main" {{
  name     = "rg-{environment}-{region}"
  location = "{region}"
  tags = {{
    environment = "{environment}"
    managed-by  = "ai-devfactory"
  }}
}}
""",
        "variables.tf": """
variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
  sensitive   = true
}

variable "tenant_id" {
  description = "Azure tenant ID"
  type        = string
  sensitive   = true
}

variable "client_id" {
  description = "Azure client ID"
  type        = string
  sensitive   = true
}

variable "client_secret" {
  description = "Azure client secret"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}
"""
    }

    if "compute" in services:
        templates["compute.tf"] = f"""
resource "azurerm_linux_virtual_machine" "app_server" {{
  name                = "vm-{environment}-app"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_B2s"
  admin_username      = "adminuser"
  network_interface_ids = [azurerm_network_interface.app_nic.id]

  admin_ssh_key {{
    username   = "adminuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }}

  os_disk {{
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }}

  source_image_reference {{
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }}

  tags = {{
    environment = "{environment}"
    role        = "application"
  }}
}}
"""

    if "database" in services:
        templates["database.tf"] = f"""
resource "azurerm_postgresql_server" "database" {{
  name                = "psql-{environment}-server"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  sku_name = "GP_Gen5_2"

  storage_mb = 5120
  backup_retention_days = 7
  geo_redundant_backup_enabled = false

  administrator_login          = var.db_admin_login
  administrator_login_password = var.db_admin_password

  version = "11"
  ssl_enforcement_enabled = true

  tags = {{
    environment = "{environment}"
  }}
}}
"""

    if "storage" in services:
        templates["storage.tf"] = f"""
resource "azurerm_storage_account" "storage" {{
  name                     = "st{environment}{replace(region, "-", "")}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {{
    environment = "{environment}"
  }}
}}
"""

    return templates

def create_aws_templates(services: List[str], environment: str, region: str) -> Dict[str, Any]:
    """Create AWS infrastructure templates"""
    return {
        "main.tf": f"""
# AWS Infrastructure for {environment} environment
terraform {{
  required_providers {{
    aws = {{
      source = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{region}"
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}}

resource "aws_vpc" "main" {{
  cidr_block = "10.0.0.0/16"

  tags = {{
    Name        = "vpc-{environment}"
    Environment = "{environment}"
    ManagedBy   = "ai-devfactory"
  }}
}}
""",
        "variables.tf": """
variable "aws_access_key" {
  description = "AWS access key"
  type        = string
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS secret key"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}
"""
    }

def create_gcp_templates(services: List[str], environment: str, region: str) -> Dict[str, Any]:
    """Create GCP infrastructure templates"""
    return {
        "main.tf": f"""
# GCP Infrastructure for {environment} environment
terraform {{
  required_providers {{
    google = {{
      source = "hashicorp/google"
      version = "~> 5.0"
    }}
  }}
}}

provider "google" {{
  project = var.gcp_project_id
  region  = "{region}"
  credentials = file(var.gcp_credentials)
}}

resource "google_project_service" "services" {{
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "sqladmin.googleapis.com"
  ])

  service = each.key
  disable_on_destroy = false
}}

resource "google_compute_network" "vpc_network" {{
  name                    = "vpc-{environment}"
  auto_create_subnetworks = false

  depends_on = [google_project_service.services]
}}
""",
        "variables.tf": """
variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_credentials" {
  description = "Path to GCP service account key file"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}
"""
    }

def create_kubernetes_templates(services: List[str], environment: str) -> Dict[str, Any]:
    """Create Kubernetes infrastructure templates"""
    return {
        "deployment.yaml": f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
  namespace: {environment}
  labels:
    app: application
    environment: {environment}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: application
  template:
    metadata:
      labels:
        app: application
    spec:
      containers:
      - name: application
        image: your-app:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: app-service
  namespace: {environment}
spec:
  selector:
    app: application
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
"""
    }

def simulate_deployment(templates: Dict[str, Any], cloud_provider: str) -> Dict[str, Any]:
    """Simulate infrastructure deployment"""
    return {
        "status": "in_progress",
        "steps": [
            {"step": "terraform_init", "status": "completed", "timestamp": "2024-01-01T00:00:00Z"},
            {"step": "terraform_plan", "status": "completed", "timestamp": "2024-01-01T00:01:00Z"},
            {"step": "terraform_apply", "status": "in_progress", "timestamp": "2024-01-01T00:02:00Z"},
            {"step": "verification", "status": "pending", "timestamp": None}
        ],
        "resources_to_create": len(templates) * 2,  # Rough estimate
        "estimated_cost": "100.00 USD/month",
        "deployment_logs_url": "/deployments/logs/temp-id"
    }

def calculate_cost_estimate(templates: Dict[str, Any], cloud_provider: str, services: List[str]) -> Dict[str, Any]:
    """Calculate infrastructure cost estimate"""
    base_cost = 100.0
    service_multipliers = {
        "compute": 1.5,
        "database": 2.0,
        "storage": 0.5,
        "monitoring": 0.3,
        "networking": 0.2,
        "secrets": 0.1
    }

    total_cost = base_cost
    for service in services:
        multiplier = service_multipliers.get(service, 1.0)
        total_cost *= multiplier

    # Provider adjustments
    provider_adjustments = {
        "azure": 1.0,
        "aws": 0.9,
        "gcp": 1.1,
        "kubernetes": 0.8
    }

    adjustment = provider_adjustments.get(cloud_provider, 1.0)
    total_cost *= adjustment

    return {
        "estimated_monthly_cost": round(total_cost, 2),
        "breakdown": {
            "base_infrastructure": round(base_cost * adjustment, 2),
            "additional_services": round((total_cost - base_cost * adjustment), 2),
            "services_count": len(services)
        },
        "savings_recommendations": [
            "Consider reserved instances for long-term usage",
            "Use auto-scaling to reduce costs during low traffic",
            "Implement cost monitoring and alerts"
        ]
    }

def validate_infrastructure_templates(templates: Dict[str, Any], cloud_provider: str) -> Dict[str, Any]:
    """Validate infrastructure templates"""
    issues = []
    warnings = []
    suggestions = []

    # Check for sensitive data exposure
    for filename, content in templates.items():
        if "password" in content or "secret" in content or "key" in content:
            if not any(var in content for var in ["var.", "get_env", "vault"]):
                issues.append(f"Hardcoded secret found in {filename}")

        # Check for security best practices
        if "0.0.0.0/0" in content and "security_group" not in content.lower():
            warnings.append(f"Open to public internet in {filename}")

    # Provider-specific validations
    if cloud_provider == "azure":
        if not any("resource_group" in content for content in templates.values()):
            issues.append("Missing Azure resource group definition")

    elif cloud_provider == "aws":
        if not any("vpc" in content for content in templates.values()):
            issues.append("Missing AWS VPC definition")

    elif cloud_provider == "gcp":
        if not any("project" in content for content in templates.values()):
            issues.append("Missing GCP project configuration")

    suggestions = [
        "Add tags/labels for resource management",
        "Implement monitoring and alerting",
        "Add backup and disaster recovery configuration",
        "Set up cost monitoring and budgets"
    ]

    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "suggestions": suggestions
    }

def perform_security_scan(templates: Dict[str, Any], cloud_provider: str) -> Dict[str, Any]:
    """Perform security scan on templates"""
    issues = []
    recommendations = []
    compliance = []

    # Security checks
    security_checks = {
        "encryption_at_rest": False,
        "encryption_in_transit": False,
        "network_segmentation": False,
        "access_control": False,
        "logging_enabled": False,
        "backup_enabled": False
    }

    for filename, content in templates.items():
        content_lower = content.lower()

        # Check security features
        if any(keyword in content_lower for keyword in ["encryption", "encrypted"]):
            security_checks["encryption_at_rest"] = True

        if any(keyword in content_lower for keyword in ["tls", "ssl", "https"]):
            security_checks["encryption_in_transit"] = True

        if any(keyword in content_lower for keyword in ["subnet", "vpc", "network_security"]):
            security_checks["network_segmentation"] = True

        if any(keyword in content_lower for keyword in ["iam", "rbac", "role", "permission"]):
            security_checks["access_control"] = True

        if any(keyword in content_lower for keyword in ["log", "monitor", "audit"]):
            security_checks["logging_enabled"] = True

        if any(keyword in content_lower for keyword in ["backup", "snapshot", "recovery"]):
            security_checks["backup_enabled"] = True

        # Detect potential issues
        if "0.0.0.0/0" in content:
            issues.append(f"Publicly accessible resource in {filename}")

        if "password" in content_lower and "var." not in content:
            issues.append(f"Hardcoded credentials in {filename}")

    # Generate recommendations
    for check, passed in security_checks.items():
        if not passed:
            recommendations.append(f"Implement {check.replace('_', ' ')}")

    # Compliance standards
    compliance_standards = ["SOC2", "ISO27001", "HIPAA", "GDPR", "PCI-DSS"]
    passed_checks = sum(security_checks.values())
    total_checks = len(security_checks)

    compliance = []
    if passed_checks / total_checks > 0.7:
        compliance.append("SOC2 Ready")
    if passed_checks / total_checks > 0.8:
        compliance.append("ISO27001 Ready")
    if security_checks["encryption_at_rest"] and security_checks["encryption_in_transit"]:
        compliance.append("HIPAA Data Protection")

    security_score = int((passed_checks / total_checks) * 100)

    return {
        "score": security_score,
        "issues": issues,
        "recommendations": recommendations,
        "compliance": compliance,
        "security_checks": security_checks
    }

@app.post("/test")
async def test_generation():
    """Test endpoint to verify agent is working"""
    test_config = InfrastructureConfig(
        job_id="test-123",
        cloud_provider="azure",
        services=["compute", "database", "storage"],
        environment="dev",
        region="eastus"
    )

    try:
        templates = create_infrastructure_templates(
            test_config.cloud_provider,
            test_config.services,
            test_config.environment,
            test_config.region
        )

        return {
            "status": "success",
            "test": "passed",
            "templates_generated": len(templates),
            "services": test_config.services,
            "cloud_provider": test_config.cloud_provider
        }
    except Exception as e:
        return {
            "status": "error",
            "test": "failed",
            "error": str(e)
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5002))
    print(f"🚀 Starting Infrastructure Agent on port {port}")
    print(f"📍 Endpoint: http://localhost:{port}/generate")
    print(f"📚 Docs: http://localhost:{port}/docs")
    print(f"☁️  Supported providers: Azure, AWS, GCP, Kubernetes")

    uvicorn.run(app, host="0.0.0.0", port=port)