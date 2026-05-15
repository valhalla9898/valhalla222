// Main Bicep Template for Agentic-IAM Deployment
// Deploys all required Azure resources for the application

param location string = resourceGroup().location
param environment string = 'prod'
param projectName string = 'agentic-iam'
param containerImageName string = 'agentic-iam'
param containerImageTag string = 'latest'

// Networking parameters
param vnetAddressPrefix string = '10.0.0.0/16'
param subnetAddressPrefix string = '10.0.0.0/24'

// Database parameters
param postgresqlAdminUser string = 'pgadmin'
param postgresqlDatabaseName string = 'agentic_iam'
param postgresqlSkuName string = 'Standard_B2s'

// Redis parameters
param redisSkuName string = 'Standard'
param redisCapacity int = 1

// Variables
var uniqueSuffix = uniqueString(resourceGroup().id)
var containerRegistryName = '${replace(projectName, '-', '')}${uniqueSuffix}'
var keyVaultName = '${projectName}-kv-${uniqueSuffix}'
var postgresqlServerName = '${projectName}-db-${uniqueSuffix}'
var redisName = '${projectName}-redis-${uniqueSuffix}'
var containerAppEnvName = '${projectName}-env-${uniqueSuffix}'
var appInsightsName = '${projectName}-insights-${uniqueSuffix}'
var logAnalyticsWorkspaceName = '${projectName}-logs-${uniqueSuffix}'

// Tags for all resources
var tags = {
  environment: environment
  project: projectName
  createdDate: utcNow('u')
  managedBy: 'Bicep'
}

// ============================================================================
// Log Analytics Workspace
// ============================================================================
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsWorkspaceName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ============================================================================
// Application Insights
// ============================================================================
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    RetentionInDays: 30
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ============================================================================
// Container Registry
// ============================================================================
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: containerRegistryName
  location: location
  tags: tags
  sku: {
    name: 'Standard'
  }
  properties: {
    adminUserEnabled: true
    publicNetworkAccess: 'Enabled'
    anonymousPullEnabled: false
    dataEndpointEnabled: false
    networkRuleBypassOptions: 'AzureServices'
    publicNetworkAccessEnabled: true
    zoneRedundancy: 'Disabled'
  }
}

// ============================================================================
// Key Vault
// ============================================================================
resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: reference(managedIdentity.id, '2018-11-30', 'Full').principalId
        permissions: {
          keys: ['get', 'list']
          secrets: ['get', 'list']
          certificates: ['get', 'list']
        }
      }
    ]
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: false
    softDeleteRetentionInDays: 7
  }
}

// ============================================================================
// Managed Identity for Container Apps
// ============================================================================
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${projectName}-identity-${uniqueSuffix}'
  location: location
  tags: tags
}

// ============================================================================
// Virtual Network
// ============================================================================
resource virtualNetwork 'Microsoft.Network/virtualNetworks@2023-02-01' = {
  name: '${projectName}-vnet-${uniqueSuffix}'
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressPrefix
      ]
    }
    subnets: [
      {
        name: 'container-apps'
        properties: {
          addressPrefix: subnetAddressPrefix
          delegations: [
            {
              name: 'Microsoft.App/environments'
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
        }
      }
    ]
  }
}

// ============================================================================
// Container Apps Environment
// ============================================================================
resource containerAppEnvironment 'Microsoft.App/managedEnvironments@2023-04-01-preview' = {
  name: containerAppEnvName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
    vnetConfiguration: {
      infrastructureSubnetId: '${virtualNetwork.id}/subnets/container-apps'
    }
    daprAIConnectionString: appInsights.properties.ConnectionString
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
    zoneRedundant: false
  }
}

// ============================================================================
// PostgreSQL Database
// ============================================================================
resource postgresqlServer 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = {
  name: postgresqlServerName
  location: location
  tags: tags
  sku: {
    name: postgresqlSkuName
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: postgresqlAdminUser
    administratorLoginPassword: keyVault.getSecret('postgresql-password')
    version: '14'
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    network: {
      delegatedSubnetResourceId: '${virtualNetwork.id}/subnets/container-apps'
      privateDnsZoneArmResourceId: privateDnsZone.id
    }
  }
  dependsOn: [
    privateDnsZone
  ]
}

// PostgreSQL Database
resource postgresqlDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2022-12-01' = {
  name: postgresqlDatabaseName
  parent: postgresqlServer
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// ============================================================================
// Private DNS Zone for PostgreSQL
// ============================================================================
resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: '${environment}.postgres.database.azure.com'
  location: 'global'
  tags: tags
}

resource privateDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: privateDnsZone
  name: '${projectName}-pdz-link'
  location: 'global'
  properties: {
    registrationEnabled: true
    virtualNetwork: {
      id: virtualNetwork.id
    }
  }
}

// ============================================================================
// Azure Cache for Redis
// ============================================================================
resource redis 'Microsoft.Cache/redis@2023-04-01' = {
  name: redisName
  location: location
  tags: tags
  properties: {
    sku: {
      name: redisSkuName
      family: 'C'
      capacity: redisCapacity
    }
    enableNonSslPort: false
    publicNetworkAccess: 'Enabled'
    minimumTlsVersion: '1.2'
  }
}

// ============================================================================
// Outputs
// ============================================================================
output containerRegistryLoginServer string = containerRegistry.properties.loginServer
output containerRegistryId string = containerRegistry.id
output keyVaultUri string = keyVault.properties.vaultUri
output postgresqlFqdn string = postgresqlServer.properties.fullyQualifiedDomainName
output redisPrimaryConnectionString string = '${redisName}.redis.cache.windows.net:6379,password=${redis.listKeys().primaryKey},ssl=True'
output containerAppEnvironmentId string = containerAppEnvironment.id
output managedIdentityClientId string = managedIdentity.properties.clientId
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString
