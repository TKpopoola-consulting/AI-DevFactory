// infra/resources.bicep
param location string = 'eastus'
param frontendAgentImage string

resource frontendAgent 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: 'frontend-agent'
  location: location
  properties: {
    containers: [
      {
        name: 'frontend-generator'
        properties: {
          image: frontendAgentImage
          ports: [{ port: 5000 }]
          resources: {
            requests: {
              cpu: 2
              memoryInGB: 4
            }
          }
          environmentVariables: [
            {
              name: 'GEMINI_API_KEY'
              value: keyVault.getSecret('gemini-api-key')
            }
            {
              name: 'FLASK_ENV'
              value: 'production'
            }
          ]
        }
      }
    ]
    osType: 'Linux'
    ipAddress: {
      type: 'Public'
      ports: [
        {
          protocol: 'TCP'
          port: 5000
        }
      ]
    }
  }
}