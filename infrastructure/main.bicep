// Quantum Advantage Evaluator  Azure Infrastructure
// Deploys: Cosmos DB, AI Search, AI Foundry project, Azure Functions

@description('Location for all resources')
param location string = 'eastus'

@description('Unique suffix for resource names')
param uniqueSuffix string = 'qgc${uniqueString(resourceGroup().id)}'

// === Cosmos DB (Serverless)  Knowledge Store ===
resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: 'cosmos-${uniqueSuffix}'
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    capabilities: [{ name: 'EnableServerless' }]
    locations: [{ locationName: location, failoverPriority: 0 }]
  }
}

resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-05-15' = {
  parent: cosmosAccount
  name: 'quantum_kb'
  properties: {
    resource: { id: 'quantum_kb' }
  }
}

resource papersContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: cosmosDatabase
  name: 'scientific_papers'
  properties: {
    resource: {
      id: 'scientific_papers'
      partitionKey: { paths: ['/category'], kind: 'Hash' }
      indexingPolicy: {
        automatic: true
        includedPaths: [{ path: '/*' }]
      }
    }
  }
}

resource algorithmsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: cosmosDatabase
  name: 'algorithm_zoo'
  properties: {
    resource: {
      id: 'algorithm_zoo'
      partitionKey: { paths: ['/speedup_class'], kind: 'Hash' }
    }
  }
}

resource problemHistoryContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: cosmosDatabase
  name: 'problem_history'
  properties: {
    resource: {
      id: 'problem_history'
      partitionKey: { paths: ['/user_id'], kind: 'Hash' }
    }
  }
}

// === Azure AI Search (Basic)  Hybrid Search Index ===
resource searchService 'Microsoft.Search/searchServices@2024-03-01-preview' = {
  name: 'search-${uniqueSuffix}'
  location: location
  sku: { name: 'basic' }
  properties: {
    replicaCount: 1
    partitionCount: 1
    semanticSearch: 'standard'
  }
}

// === Storage Account (for Azure Functions) ===
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'st${uniqueSuffix}'
  location: location
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
}

// === Azure Functions (Consumption)  Daily Ingestion ===
resource functionAppPlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: 'plan-${uniqueSuffix}'
  location: location
  sku: { name: 'Y1', tier: 'Dynamic' }
  kind: 'functionapp'
}

resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: 'func-${uniqueSuffix}'
  location: location
  kind: 'functionapp'
  properties: {
    serverFarmId: functionAppPlan.id
    siteConfig: {
      appSettings: [
        { name: 'AzureWebJobsStorage', value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value}' }
        { name: 'FUNCTIONS_EXTENSION_VERSION', value: '~4' }
        { name: 'FUNCTIONS_WORKER_RUNTIME', value: 'python' }
        { name: 'COSMOS_CONNECTION_STRING', value: cosmosAccount.listConnectionStrings().connectionStrings[0].connectionString }
        { name: 'SEARCH_ENDPOINT', value: 'https://${searchService.name}.search.windows.net' }
        { name: 'SEARCH_KEY', value: searchService.listAdminKeys().primaryKey }
      ]
    }
  }
}

// === Outputs ===
output cosmosEndpoint string = cosmosAccount.properties.documentEndpoint
output searchEndpoint string = 'https://${searchService.name}.search.windows.net'
output functionAppName string = functionApp.name
