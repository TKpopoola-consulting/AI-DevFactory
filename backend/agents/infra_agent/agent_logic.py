# backend/agents/infra_agent/agent_logic.py (COMPLETE)
"""
Complete Infrastructure Agent with full template generation,
validation, deployment, cost estimation, security scanning, and diagrams
"""
import os
import json
import asyncio
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import yaml

# Import utilities (will create these files)
from utils.template_generator import TemplateGenerator
from utils.validator import InfrastructureValidator
from utils.deployer import InfrastructureDeployer
from utils.cost_calculator import CostCalculator
from utils.security_scanner import SecurityScanner


@dataclass
class InfrastructureConfig:
    """Infrastructure configuration"""
    job_id: str
    cloud_provider: str
    services: List[str]
    scaling: Dict[str, Any]
    environment: str = "dev"
    region: str = "eastus"
    tags: Dict[str, str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class InfraAgent:
    """Complete infrastructure agent for multi-cloud deployment"""
    
    def __init__(self):
        self.template_gen = TemplateGenerator()
        self.validator = InfrastructureValidator()
        self.deployer = InfrastructureDeployer()
        self.cost_calc = CostCalculator()
        self.security_scanner = SecurityScanner()
        self.cache = {}
        
    async def generate_infrastructure(self, config: InfrastructureConfig) -> Dict[str, Any]:
        """
        Generate complete infrastructure templates
        
        Args:
            config: Infrastructure configuration
            
        Returns:
            Dictionary with templates, validation results, and metadata
        """
        try:
            # Check cache
            cache_key = f"{config.cloud_provider}_{'_'.join(config.services)}_{config.environment}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Generate templates based on cloud provider
            if config.cloud_provider == "azure":
                templates = await self._generate_azure_templates(config)
            elif config.cloud_provider == "aws":
                templates = await self._generate_aws_templates(config)
            elif config.cloud_provider == "gcp":
                templates = await self._generate_gcp_templates(config)
            else:
                raise ValueError(f"Unsupported cloud provider: {config.cloud_provider}")
            
            # Validate templates
            validation = await self.validator.validate_templates(templates, config.cloud_provider)
            
            # Scan for security issues
            security = await self.security_scanner.scan_templates(templates, config.cloud_provider)
            
            # Calculate cost estimate
            cost = await self.cost_calc.calculate_cost(templates, config.cloud_provider, config.services)
            
            # Generate architecture diagram
            diagram = await self._generate_diagram(config.services, config.cloud_provider)
            
            result = {
                "job_id": config.job_id,
                "cloud_provider": config.cloud_provider,
                "environment": config.environment,
                "templates": templates,
                "validation": validation,
                "security": security,
                "cost_estimate": cost,
                "diagram": diagram,
                "generated_at": datetime.utcnow().isoformat(),
                "status": "generated"
            }
            
            # Cache result
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            raise RuntimeError(f"Infrastructure generation failed: {str(e)}")
    
    async def _generate_azure_templates(self, config: InfrastructureConfig) -> Dict[str, str]:
        """Generate Azure Bicep templates"""
        templates = {}
        
        # Main parameters file
        templates["parameters.bicep"] = f"""
@description('Environment name (dev, staging, prod)')
param environmentName string = '{config.environment}'

@description('Azure region')
param location string = '{config.region}'

@description('Resource tags')
param tags object = {json.dumps(config.tags or {})}
"""
        
        # Generate resources based on requested services
        if "app_service" in config.services or "compute" in config.services:
            templates["app_service.bicep"] = self._generate_azure_app_service(config)
        
        if "database" in config.services:
            templates["database.bicep"] = self._generate_azure_database(config)
        
        if "storage" in config.services:
            templates["storage.bicep"] = self._generate_azure_storage(config)
        
        if "secrets" in config.services:
            templates["key_vault.bicep"] = self._generate_azure_key_vault(config)
        
        if "monitoring" in config.services:
            templates["monitoring.bicep"] = self._generate_azure_monitoring(config)
        
        if "networking" in config.services:
            templates["networking.bicep"] = self._generate_azure_networking(config)
        
        # Main deployment file
        module_declarations = self._generate_module_declarations(list(templates.keys()))
        templates["main.bicep"] = f"""
@description('Infrastructure deployment for {config.job_id}')
targetScope = 'resourceGroup'

// Load parameters
param environmentName string
param location string
param tags object

// Module declarations
{module_declarations}
"""
        
        return templates
    
    def _generate_azure_app_service(self, config: InfrastructureConfig) -> str:
        """Generate Azure App Service template"""
        return f"""
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {{
  name: 'plan-${{environmentName}}'
  location: location
  sku: {{
    name: '{config.scaling.get("app_service_tier", "B1")}'
    tier: '{config.scaling.get("app_service_tier", "Basic")}'
  }}
  tags: tags
}}

resource appService 'Microsoft.Web/sites@2022-03-01' = {{
  name: 'app-${{environmentName}}'
  location: location
  properties: {{
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {{
      alwaysOn: true
      linuxFxVersion: '{config.scaling.get("runtime", "NODE|18-lts")}'
    }}
  }}
  tags: tags
}}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {{
  name: 'appi-${{environmentName}}'
  location: location
  kind: 'web'
  properties: {{
    Application_Type: 'web'
  }}
  tags: tags
}}
"""
    
    def _generate_azure_database(self, config: InfrastructureConfig) -> str:
        """Generate Azure Database template (Cosmos DB or PostgreSQL)"""
        db_type = config.scaling.get("database_type", "cosmosdb")
        
        if db_type == "cosmosdb":
            return f"""
resource cosmosDb 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {{
  name: 'cosmos-${{environmentName}}'
  location: location
  kind: 'GlobalDocumentDB'
  properties: {{
    databaseAccountOfferType: 'Standard'
    locations: [
      {{
        locationName: location
        failoverPriority: 0
      }}
    ]
    consistencyPolicy: {{
      defaultConsistencyLevel: '{config.scaling.get("consistency", "Session")}'
    }}
    enableAutomaticFailover: true
  }}
  tags: tags
}}

resource sqlDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-04-15' = {{
  name: 'cosmos-${{environmentName}}/app-db'
  properties: {{
    resource: {{
      id: 'app-db'
    }}
    options: {{
      throughput: {config.scaling.get("db_throughput", 400)}
    }}
  }}
}}
"""
        else:
            return f"""
resource postgreSql 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = {{
  name: 'postgres-${{environmentName}}'
  location: location
  sku: {{
    name: '{config.scaling.get("db_sku", "B_Standard_B1ms")}'
    tier: '{config.scaling.get("db_tier", "Burstable")}'
  }}
  properties: {{
    version: '{config.scaling.get("db_version", "14")}'
    administratorLogin: 'adminuser'
    administratorLoginPassword: '{config.scaling.get("db_password", "ChangeMe123!")}'
    storage: {{
      storageSizeGB: {config.scaling.get("db_storage", 32)}
    }}
    backup: {{
      backupRetentionDays: {config.scaling.get("backup_retention", 7)}
      geoRedundantBackup: 'Disabled'
    }}
    highAvailability: {{
      mode: 'Disabled'
    }}
  }}
  tags: tags
}}
"""
    
    def _generate_azure_storage(self, config: InfrastructureConfig) -> str:
        """Generate Azure Storage Account template"""
        return f"""
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {{
  name: 'st${{uniqueString(resourceGroup().id)}}'
  location: location
  sku: {{
    name: '{config.scaling.get("storage_tier", "Standard_LRS")}'
  }}
  kind: 'StorageV2'
  properties: {{
    accessTier: '{config.scaling.get("storage_access_tier", "Hot")}'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }}
  tags: tags
}}

resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {{
  name: '${{storageAccount.name}}/default/assets'
  properties: {{
    publicAccess: 'None'
  }}
}}
"""
    
    def _generate_azure_key_vault(self, config: InfrastructureConfig) -> str:
        """Generate Azure Key Vault template"""
        return f"""
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {{
  name: 'kv-${{environmentName}}'
  location: location
  properties: {{
    tenantId: subscription().tenantId
    sku: {{
      family: 'A'
      name: '{config.scaling.get("key_vault_sku", "standard")}'
    }}
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
  }}
  tags: tags
}}

resource secret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {{
  name: 'kv-${{environmentName}}/api-key'
  properties: {{
    value: '{config.scaling.get("api_key", "placeholder-key")}'
  }}
}}
"""
    
    def _generate_azure_monitoring(self, config: InfrastructureConfig) -> str:
        """Generate Azure Monitoring template"""
        return f"""
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {{
  name: 'logs-${{environmentName}}'
  location: location
  properties: {{
    retentionInDays: {config.scaling.get("log_retention", 30)}
  }}
  tags: tags
}}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {{
  name: 'appi-${{environmentName}}'
  location: location
  kind: 'web'
  properties: {{
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }}
  tags: tags
}}

resource alertRule 'Microsoft.Insights/metricAlerts@2018-03-01' = {{
  name: 'alert-${{environmentName}}'
  location: 'global'
  properties: {{
    severity: 2
    enabled: true
    scopes: [
      appService.id
    ]
    condition: {{
      operator: 'GreaterThan'
      threshold: 5
      timeAggregation: 'Total'
      metricName: 'Http5xx'
    }}
    actions: [
      {{
        actionGroupId: '/subscriptions/{{subscription().subscriptionId}}/resourceGroups/{{resourceGroup().name}}/providers/microsoft.insights/actiongroups/email'
      }}
    ]
  }}
}}
"""
    
    def _generate_azure_networking(self, config: InfrastructureConfig) -> str:
        """Generate Azure Networking template"""
        return f"""
resource vnet 'Microsoft.Network/virtualNetworks@2023-02-01' = {{
  name: 'vnet-${{environmentName}}'
  location: location
  properties: {{
    addressSpace: {{
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }}
    subnets: [
      {{
        name: 'default'
        properties: {{
          addressPrefix: '10.0.0.0/24'
        }}
      }}
    ]
  }}
  tags: tags
}}
"""
    
    def _generate_module_declarations(self, template_names: List[str]) -> str:
        """Generate module declarations for main.bicep"""
        declarations = []
        excluded = ["main.bicep", "parameters.bicep"]
        
        for name in template_names:
            if name not in excluded and name.endswith('.bicep'):
                module_name = name.replace('.bicep', '')
                declarations.append(f"""
module {module_name} '{name}' = {{
  name: '{module_name}-deployment'
  params: {{
    environmentName: environmentName
    location: location
    tags: tags
  }}
}}
""")
        return "\n".join(declarations)
    
    async def _generate_aws_templates(self, config: InfrastructureConfig) -> Dict[str, str]:
        """Generate AWS Terraform templates"""
        templates = {}
        
        # Main Terraform configuration
        templates["main.tf"] = f"""
terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{config.region}"
}}

locals {{
  environment = "{config.environment}"
  tags = {json.dumps(config.tags or {}, indent=2)}
}}
"""
        
        if "compute" in config.services:
            templates["ecs.tf"] = self._generate_aws_ecs(config)
        
        if "database" in config.services:
            templates["rds.tf"] = self._generate_aws_rds(config)
        
        if "storage" in config.services:
            templates["s3.tf"] = self._generate_aws_s3(config)
        
        if "networking" in config.services:
            templates["vpc.tf"] = self._generate_aws_vpc(config)
        
        if "monitoring" in config.services:
            templates["monitoring.tf"] = self._generate_aws_monitoring(config)
        
        templates["outputs.tf"] = self._generate_aws_outputs(config)
        
        return templates
    
    def _generate_aws_ecs(self, config: InfrastructureConfig) -> str:
        """Generate AWS ECS Terraform configuration"""
        return f"""
resource "aws_ecs_cluster" "main" {{
  name = "cluster-${{local.environment}}"
  tags = local.tags
}}

resource "aws_ecs_task_definition" "app" {{
  family                   = "app-${{local.environment}}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "{config.scaling.get("ecs_cpu", "256")}"
  memory                   = "{config.scaling.get("ecs_memory", "512")}"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn           = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {{
      name  = "app"
      image = "{config.scaling.get("container_image", "nginx:latest")}"
      portMappings = [
        {{
          containerPort = 80
          protocol      = "tcp"
        }}
      ]
    }}
  ])
}}

resource "aws_ecs_service" "app" {{
  name            = "service-${{local.environment}}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = {config.scaling.get("desired_count", 2)}
  launch_type     = "FARGATE"

  network_configuration {{
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }}
}}

resource "aws_iam_role" "ecs_execution" {{
  name = "ecs-execution-${{local.environment}}"
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "ecs-tasks.amazonaws.com"
        }}
      }}
    ]
  }})
}}

resource "aws_iam_role_policy_attachment" "ecs_execution" {{
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}}

resource "aws_iam_role" "ecs_task" {{
  name = "ecs-task-${{local.environment}}"
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "ecs-tasks.amazonaws.com"
        }}
      }}
    ]
  }})
}}

resource "aws_security_group" "ecs" {{
  name        = "ecs-${{local.environment}}"
  description = "ECS Security Group"
  vpc_id      = aws_vpc.main.id
  
  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  tags = local.tags
}}
"""
    
    def _generate_aws_rds(self, config: InfrastructureConfig) -> str:
        """Generate AWS RDS Terraform configuration"""
        return f"""
resource "aws_db_instance" "main" {{
  identifier     = "db-${{local.environment}}"
  engine         = "{config.scaling.get("db_engine", "postgres")}"
  engine_version = "{config.scaling.get("db_version", "15")}"
  instance_class = "{config.scaling.get("db_instance_class", "db.t3.micro")}"
  allocated_storage = {config.scaling.get("db_storage", 20)}
  
  db_name  = "appdb"
  username = "admin"
  password = random_password.db_password.result
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = {config.scaling.get("backup_retention", 7)}
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  storage_encrypted = true
  storage_type      = "gp3"
  
  skip_final_snapshot = {config.environment != "prod"}
  tags = local.tags
}}

resource "random_password" "db_password" {{
  length  = 16
  special = false
}}

resource "aws_db_subnet_group" "main" {{
  name       = "db-subnet-${{local.environment}}"
  subnet_ids = aws_subnet.private[*].id
  tags       = local.tags
}}

resource "aws_security_group" "rds" {{
  name        = "rds-${{local.environment}}"
  description = "RDS Security Group"
  vpc_id      = aws_vpc.main.id
  
  ingress {{
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }}
  
  tags = local.tags
}}
"""
    
    def _generate_aws_s3(self, config: InfrastructureConfig) -> str:
        """Generate AWS S3 Terraform configuration"""
        return f"""
resource "aws_s3_bucket" "main" {{
  bucket = "app-${{local.environment}}-${{random_id.bucket_suffix.hex}}"
  tags   = local.tags
}}

resource "random_id" "bucket_suffix" {{
  byte_length = 4
}}

resource "aws_s3_bucket_versioning" "main" {{
  bucket = aws_s3_bucket.main.id
  versioning_configuration {{
    status = "Enabled"
  }}
}}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {{
  bucket = aws_s3_bucket.main.id

  rule {{
    apply_server_side_encryption_by_default {{
      sse_algorithm = "AES256"
    }}
  }}
}}

resource "aws_s3_bucket_public_access_block" "main" {{
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}

resource "aws_s3_bucket_lifecycle_configuration" "main" {{
  bucket = aws_s3_bucket.main.id

  rule {{
    id     = "archive-old-files"
    status = "Enabled"

    transition {{
      days          = 30
      storage_class = "STANDARD_IA"
    }}
    
    transition {{
      days          = 90
      storage_class = "GLACIER"
    }}
    
    expiration {{
      days = 365
    }}
  }}
}}
"""
    
    def _generate_aws_vpc(self, config: InfrastructureConfig) -> str:
        """Generate AWS VPC Terraform configuration"""
        return f"""
resource "aws_vpc" "main" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = merge(local.tags, {{
    Name = "vpc-${{local.environment}}"
  }})
}}

resource "aws_subnet" "public" {{
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${{count.index}}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags = merge(local.tags, {{
    Name = "public-${{local.environment}}-${{count.index}}"
  }})
}}

resource "aws_subnet" "private" {{
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${{count.index + 10}}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = merge(local.tags, {{
    Name = "private-${{local.environment}}-${{count.index}}"
  }})
}}

resource "aws_internet_gateway" "main" {{
  vpc_id = aws_vpc.main.id
  tags   = local.tags
}}

resource "aws_route_table" "public" {{
  vpc_id = aws_vpc.main.id

  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }}

  tags = local.tags
}}

resource "aws_route_table_association" "public" {{
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}}

data "aws_availability_zones" "available" {{
  state = "available"
}}
"""
    
    def _generate_aws_monitoring(self, config: InfrastructureConfig) -> str:
        """Generate AWS Monitoring configuration"""
        return f"""
resource "aws_cloudwatch_log_group" "ecs" {{
  name              = "/ecs/${{local.environment}}"
  retention_in_days = {config.scaling.get("log_retention", 30)}
  tags              = local.tags
}}

resource "aws_cloudwatch_metric_alarm" "high_cpu" {{
  alarm_name          = "high-cpu-${{local.environment}}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name        = "CPUUtilization"
  namespace          = "AWS/ECS"
  period             = 300
  statistic          = "Average"
  threshold          = 80
  alarm_description  = "This metric monitors ecs cpu utilization"
  
  dimensions = {{
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.app.name
  }}
}}
"""
    
    def _generate_aws_outputs(self, config: InfrastructureConfig) -> str:
        """Generate AWS outputs"""
        return f"""
output "vpc_id" {{
  description = "VPC ID"
  value       = aws_vpc.main.id
}}

output "ecs_cluster_name" {{
  description = "ECS Cluster Name"
  value       = aws_ecs_cluster.main.name
}}

output "rds_endpoint" {{
  description = "RDS Endpoint"
  value       = aws_db_instance.main.endpoint
}}

output "s3_bucket_name" {{
  description = "S3 Bucket Name"
  value       = aws_s3_bucket.main.id
}}
"""
    
    async def _generate_gcp_templates(self, config: InfrastructureConfig) -> Dict[str, str]:
        """Generate GCP Terraform templates"""
        templates = {}
        
        templates["main.tf"] = f"""
terraform {{
  required_version = ">= 1.0"
  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "~> 5.0"
    }}
  }}
}}

provider "google" {{
  project = "{config.scaling.get("project_id", "my-project")}"
  region  = "{config.region}"
}}

locals {{
  environment = "{config.environment}"
  tags = {json.dumps(config.tags or {}, indent=2)}
}}
"""
        
        if "compute" in config.services:
            templates["cloud_run.tf"] = self._generate_gcp_cloud_run(config)
        
        if "database" in config.services:
            templates["cloud_sql.tf"] = self._generate_gcp_cloud_sql(config)
        
        if "storage" in config.services:
            templates["cloud_storage.tf"] = self._generate_gcp_cloud_storage(config)
        
        return templates
    
    def _generate_gcp_cloud_run(self, config: InfrastructureConfig) -> str:
        """Generate GCP Cloud Run Terraform configuration"""
        return f"""
resource "google_cloud_run_service" "app" {{
  name     = "app-${{local.environment}}"
  location = "{config.region}"
  
  template {{
    spec {{
      containers {{
        image = "{config.scaling.get("container_image", "gcr.io/cloudrun/hello")}"
        resources {{
          limits = {{
            cpu    = "{config.scaling.get("cpu", "1")}"
            memory = "{config.scaling.get("memory", "512Mi")}"
          }}
        }}
      }}
    }}
  }}
  
  traffic {{
    percent         = 100
    latest_revision = true
  }}
  
  autogenerate_revision_name = true
  depends_on = [google_project_service.run_api]
}}

resource "google_cloud_run_service_iam_member" "public" {{
  service  = google_cloud_run_service.app.name
  location = google_cloud_run_service.app.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}}

resource "google_project_service" "run_api" {{
  service = "run.googleapis.com"
  disable_on_destroy = false
}}

output "cloud_run_url" {{
  value = google_cloud_run_service.app.status[0].url
}}
"""
    
    def _generate_gcp_cloud_sql(self, config: InfrastructureConfig) -> str:
        """Generate GCP Cloud SQL Terraform configuration"""
        return f"""
resource "google_sql_database_instance" "main" {{
  name             = "db-${{local.environment}}"
  database_version = "{config.scaling.get("db_version", "POSTGRES_15")}"
  region           = "{config.region}"
  
  settings {{
    tier = "{config.scaling.get("db_tier", "db-f1-micro")}"
    
    ip_configuration {{
      ipv4_enabled    = false
      private_network = google_compute_network.main.id
    }}
    
    backup_configuration {{
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
    }}
    
    disk_size       = {config.scaling.get("db_disk_size", 10)}
    disk_type       = "PD_SSD"
    disk_autoresize = true
  }}
  
  deletion_protection = {config.environment == "prod"}
}}

resource "google_sql_database" "app" {{
  name     = "appdb"
  instance = google_sql_database_instance.main.name
}}

resource "random_password" "db_password" {{
  length  = 16
  special = false
}}

resource "google_sql_user" "app" {{
  name     = "appuser"
  instance = google_sql_database_instance.main.name
  password = random_password.db_password.result
}}
"""
    
    def _generate_gcp_cloud_storage(self, config: InfrastructureConfig) -> str:
        """Generate GCP Cloud Storage Terraform configuration"""
        return f"""
resource "google_storage_bucket" "main" {{
  name          = "app-${{local.environment}}-${{random_id.bucket_suffix.hex}}"
  location      = "{config.region}"
  force_destroy = {config.environment != "prod"}
  
  uniform_bucket_level_access = true
  
  versioning {{
    enabled = true
  }}
  
  encryption {{
    default_kms_key_name = google_kms_crypto_key.bucket_key.id
  }}
  
  lifecycle_rule {{
    condition {{
      age = 30
    }}
    action {{
      type = "Delete"
    }}
  }}
}}

resource "random_id" "bucket_suffix" {{
  byte_length = 4
}}

resource "google_kms_key_ring" "main" {{
  name     = "keyring-${{local.environment}}"
  location = "{config.region}"
}}

resource "google_kms_crypto_key" "bucket_key" {{
  name            = "bucket-key"
  key_ring        = google_kms_key_ring.main.id
  rotation_period = "7776000s"
  
  lifecycle {{
    prevent_destroy = false
  }}
}}
"""
    
    async def _generate_diagram(self, services: List[str], cloud_provider: str) -> str:
        """Generate Mermaid.js architecture diagram"""
        diagram = f"""
```mermaid
graph TB
    subgraph "Cloud: {cloud_provider.upper()}"
        User[🌐 Users] --> LB[⚖️ Load Balancer]
        LB --> Web[🌍 Web Tier]
        
        Web --> App[⚙️ Application Tier]
        App --> Cache[💾 Cache Layer]
        App --> DB[(🗄️ Database)]
        
        App --> Storage[📦 Storage]
        
        subgraph "Monitoring & Observability"
            Logs[📊 Logging]
            Metrics[📈 Metrics]
            Alerts[🔔 Alerts]
        end
        
        App --> Monitoring
        
        subgraph "Security"
            Vault[🔐 Key Vault]
            WAF[🛡️ WAF]
        end
        
        App --> Security
    end
    
    style User fill:#e1f5fe
    style LB fill:#fff3e0
    style Web fill:#e8f5e9
    style App fill:#f3e5f5
    style DB fill:#ffebee
"""
        
        # Add cloud-specific services
        if "app_service" in services or "compute" in services:
            diagram += "\n    style App fill:#f3e5f5"
        if "database" in services:
            diagram += "\n    style DB fill:#ffebee"
        if "storage" in services:
            diagram += "\n    style Storage fill:#fff9c4"
        
        return diagram
    
    async def deploy_infrastructure(self, job_id: str, templates: Dict, cloud_provider: str) -> Dict:
        """Deploy infrastructure to cloud"""
        return await self.deployer.deploy(job_id, templates, cloud_provider)
    
    async def get_cost_estimate(self, templates: Dict, cloud_provider: str, services: List[str]) -> Dict:
        """Get cost estimate for infrastructure"""
        return await self.cost_calc.calculate_cost(templates, cloud_provider, services)


if __name__ == "__main__":
    import asyncio
    import json
    
    async def test():
        agent = InfraAgent()
        
        config = InfrastructureConfig(
            job_id="test-123",
            cloud_provider="azure",
            services=["compute", "database", "storage", "monitoring"],
            scaling={
                "app_service_tier": "B1",
                "db_throughput": 400,
                "storage_tier": "Standard_LRS"
            }
        )
        
        result = await agent.generate_infrastructure(config)
        print(json.dumps(result, indent=2, default=str))
    
    asyncio.run(test())
