# backend/agents/infra_agent/utils/template_generator.py
"""
Template generation utilities for infrastructure as code
"""
import json
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TemplateGenerator:
    """Generate infrastructure templates for various cloud providers"""
    
    def __init__(self):
        self.template_cache = {}
        
    def generate_azure_bicep(self, resources: List[str], config: Dict) -> Dict[str, str]:
        """Generate Azure Bicep templates"""
        templates = {}
        
        # Generate main template
        templates["main.bicep"] = self._generate_azure_main(config)
        
        # Generate resource-specific templates
        for resource in resources:
            if resource == "app_service":
                templates["app_service.bicep"] = self._generate_azure_app_service(config)
            elif resource == "cosmos_db":
                templates["cosmos_db.bicep"] = self._generate_azure_cosmos_db(config)
            elif resource == "storage":
                templates["storage.bicep"] = self._generate_azure_storage(config)
            elif resource == "key_vault":
                templates["key_vault.bicep"] = self._generate_azure_key_vault(config)
            elif resource == "vnet":
                templates["vnet.bicep"] = self._generate_azure_vnet(config)
            elif resource == "aks":
                templates["aks.bicep"] = self._generate_azure_aks(config)
            elif resource == "function_app":
                templates["function_app.bicep"] = self._generate_azure_function_app(config)
                
        return templates
    
    def _generate_azure_main(self, config: Dict) -> str:
        """Generate main Azure Bicep file"""
        return f"""
@description('Environment name (dev, staging, prod)')
param environmentName string = '{config.get("environment", "dev")}'

@description('Azure region')
param location string = '{config.get("region", "eastus")}'

@description('Resource tags')
param tags object = {json.dumps(config.get("tags", {}))}

targetScope = 'resourceGroup'

// Import resource modules
{self._generate_azure_imports(config.get("resources", []))}
"""
    
    def _generate_azure_imports(self, resources: List[str]) -> str:
        """Generate module imports for Azure resources"""
        imports = []
        for resource in resources:
            imports.append(f"""
module {resource} '{resource}.bicep' = {{
  name: '{resource}-deployment'
  params: {{
    environmentName: environmentName
    location: location
    tags: tags
  }}
}}
""")
        return "\n".join(imports)
    
    def _generate_azure_app_service(self, config: Dict) -> str:
        """Generate Azure App Service template"""
        return f"""
@description('Environment name')
param environmentName string

@description('Location')
param location string

@description('Resource tags')
param tags object

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {{
  name: 'plan-${{environmentName}}'
  location: location
  sku: {{
    name: '{config.get("app_service_sku", "B1")}'
    tier: '{config.get("app_service_tier", "Basic")}'
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
      linuxFxVersion: '{config.get("runtime", "NODE|18-lts")}'
    }}
  }}
  tags: tags
}}

output appServiceName string = appService.name
output appServiceUrl string = 'https://${{appService.name}}.azurewebsites.net'
"""
    
    def _generate_azure_cosmos_db(self, config: Dict) -> str:
        """Generate Azure Cosmos DB template"""
        return f"""
@description('Environment name')
param environmentName string

@description('Location')
param location string

@description('Resource tags')
param tags object

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
      defaultConsistencyLevel: '{config.get("consistency", "Session")}'
    }}
    enableAutomaticFailover: true
    publicNetworkAccess: '{config.get("public_access", "Disabled")}'
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
      throughput: {config.get("throughput", 400)}
    }}
  }}
}}

output cosmosDbEndpoint string = cosmosDb.properties.documentEndpoint
output cosmosDbKey string = cosmosDb.listKeys().primaryMasterKey
"""
    
    def _generate_azure_storage(self, config: Dict) -> str:
        """Generate Azure Storage Account template"""
        return f"""
@description('Environment name')
param environmentName string

@description('Location')
param location string

@description('Resource tags')
param tags object

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {{
  name: 'st${{uniqueString(resourceGroup().id)}}'
  location: location
  sku: {{
    name: '{config.get("storage_sku", "Standard_LRS")}'
  }}
  kind: 'StorageV2'
  properties: {{
    accessTier: '{config.get("access_tier", "Hot")}'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }}
  tags: tags
}}

resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {{
  name: '${{storageAccount.name}}/default/${{environmentName}}-assets'
  properties: {{
    publicAccess: 'None'
  }}
}}

output storageAccountName string = storageAccount.name
output storageConnectionString string = storageAccount.properties.primaryEndpoints.blob
"""
    
    def _generate_azure_key_vault(self, config: Dict) -> str:
        """Generate Azure Key Vault template"""
        return f"""
@description('Environment name')
param environmentName string

@description('Location')
param location string

@description('Resource tags')
param tags object

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {{
  name: 'kv-${{environmentName}}'
  location: location
  properties: {{
    tenantId: subscription().tenantId
    sku: {{
      family: 'A'
      name: '{config.get("key_vault_sku", "standard")}'
    }}
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enabledForDeployment: true
    enabledForDiskEncryption: true
    enabledForTemplateDeployment: true
  }}
  tags: tags
}}

resource apiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {{
  name: 'kv-${{environmentName}}/api-key'
  properties: {{
    value: '{config.get("api_key", "placeholder-api-key")}'
  }}
}}

output keyVaultUri string = keyVault.properties.vaultUri
"""
    
    def _generate_azure_vnet(self, config: Dict) -> str:
        """Generate Azure Virtual Network template"""
        return f"""
@description('Environment name')
param environmentName string

@description('Location')
param location string

@description('Resource tags')
param tags object

resource vnet 'Microsoft.Network/virtualNetworks@2023-02-01' = {{
  name: 'vnet-${{environmentName}}'
  location: location
  properties: {{
    addressSpace: {{
      addressPrefixes: [
        '{config.get("vnet_cidr", "10.0.0.0/16")}'
      ]
    }}
    subnets: [
      {{
        name: 'subnet-web'
        properties: {{
          addressPrefix: '{config.get("web_subnet", "10.0.1.0/24")}'
        }}
      }}
      {{
        name: 'subnet-app'
        properties: {{
          addressPrefix: '{config.get("app_subnet", "10.0.2.0/24")}'
        }}
      }}
      {{
        name: 'subnet-db'
        properties: {{
          addressPrefix: '{config.get("db_subnet", "10.0.3.0/24")}'
        }}
      }}
    ]
  }}
  tags: tags
}}

output vnetId string = vnet.id
"""
    
    def _generate_azure_aks(self, config: Dict) -> str:
        """Generate Azure Kubernetes Service template"""
        return f"""
@description('Environment name')
param environmentName string

@description('Location')
param location string

@description('Resource tags')
param tags object

resource aks 'Microsoft.ContainerService/managedClusters@2023-05-02-preview' = {{
  name: 'aks-${{environmentName}}'
  location: location
  properties: {{
    kubernetesVersion: '{config.get("k8s_version", "1.27")}'
    dnsPrefix: 'aks-${{environmentName}}'
    agentPoolProfiles: [
      {{
        name: 'agentpool'
        count: {config.get("node_count", 3)}
        vmSize: '{config.get("node_size", "Standard_D2s_v3")}'
        osType: 'Linux'
        mode: 'System'
      }}
    ]
    networkProfile: {{
      networkPlugin: 'azure'
      networkPolicy: 'azure'
    }}
    enableRBAC: true
    addonProfiles: {{
      monitoring: {{
        enabled: true
      }}
    }}
  }}
  tags: tags
}}

output aksName string = aks.name
output aksKubeconfig string = aks.listClusterAdminCredential().kubeconfigs[0].value
"""
    
    def _generate_azure_function_app(self, config: Dict) -> str:
        """Generate Azure Functions template"""
        return f"""
@description('Environment name')
param environmentName string

@description('Location')
param location string

@description('Resource tags')
param tags object

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {{
  name: 'func${{uniqueString(resourceGroup().id)}}'
  location: location
  sku: {{
    name: 'Standard_LRS'
  }}
  kind: 'StorageV2'
  tags: tags
}}

resource functionApp 'Microsoft.Web/sites@2022-03-01' = {{
  name: 'func-${{environmentName}}'
  location: location
  kind: 'functionapp'
  properties: {{
    serverFarmId: appServicePlan.id
    siteConfig: {{
      appSettings: [
        {{
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${{storageAccount.name}};AccountKey=${{storageAccount.listKeys().keys[0].value}};EndpointSuffix=core.windows.net'
        }}
        {{
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }}
        {{
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: '{config.get("runtime", "node")}'
        }}
      ]
    }}
    httpsOnly: true
  }}
  tags: tags
}}

output functionAppName string = functionApp.name
"""
    
    def generate_terraform_templates(self, cloud: str, resources: List[str], config: Dict) -> Dict[str, str]:
        """Generate Terraform templates for AWS/GCP"""
        templates = {}
        
        # Provider configuration
        templates["provider.tf"] = f"""
provider "{cloud}" {{
  region = "{config.get("region", "us-east-1")}"
}}
"""
        
        # Variables
        templates["variables.tf"] = f"""
variable "environment" {{
  description = "Environment name"
  type        = string
  default     = "{config.get("environment", "dev")}"
}}

variable "tags" {{
  description = "Resource tags"
  type        = map(string)
  default     = {json.dumps(config.get("tags", {}))}
}}
"""
        
        # Outputs
        templates["outputs.tf"] = """
output "resource_ids" {
  description = "IDs of created resources"
  value       = module.main.resource_ids
}
"""
        
        # Main module
        templates["main.tf"] = f"""
module "main" {{
  source      = "./modules/{cloud}"
  environment = var.environment
  tags        = var.tags
}}
"""
        
        return templates


class TemplateLoader:
    """Load and cache templates from files"""
    
    def __init__(self, template_dir: Path = None):
        self.template_dir = template_dir or Path(__file__).parent.parent / "templates"
        self.cache = {}
        
    def load_template(self, name: str, cloud: str) -> str:
        """Load a template file"""
        cache_key = f"{cloud}_{name}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        template_path = self.template_dir / cloud / f"{name}.bicep"
        if not template_path.exists():
            template_path = self.template_dir / cloud / f"{name}.tf"
        
        if template_path.exists():
            with open(template_path, 'r') as f:
                content = f.read()
                self.cache[cache_key] = content
                return content
        
        return ""
    
    def render_template(self, template: str, variables: Dict) -> str:
        """Render template with variables"""
        result = template
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result
