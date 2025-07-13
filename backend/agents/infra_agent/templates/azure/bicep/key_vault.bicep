param location string = resourceGroup().location
param keyVaultName string = 'kv-${uniqueString(resourceGroup().id)}'

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      name: 'standard'
      family: 'A'
    }
    tenantId: subscription().tenantId
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: userAssignedIdentity.properties.principalId
        permissions: {
          secrets: [
            'get'
            'list'
          ]
          certificates: [
            'get'
            'list'
          ]
          keys: [
            'get'
            'list'
          ]
        }
      }
    ]
    enableRbacAuthorization: false
  }
}

resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-${keyVaultName}'
  location: location
}