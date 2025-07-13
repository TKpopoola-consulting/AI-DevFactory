param location string = resourceGroup().location
param accountName string = 'cosmos-${uniqueString(resourceGroup().id)}'

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: accountName
  location: location
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
  }
}

resource sqlDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-04-15' = {
  name: '${cosmosAccount.name}/sqldb'
  properties: {
    resource: {
      id: '${appName}-db'
    }
  }
}