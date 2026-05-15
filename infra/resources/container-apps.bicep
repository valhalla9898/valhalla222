// Container Apps for Agentic-IAM
// Deploys dashboard and API containers

param location string = resourceGroup().location
param environment string = 'prod'
param projectName string = 'agentic-iam'
param containerImageName string = 'agentic-iam'
param containerImageTag string = 'latest'
param containerRegistryUrl string
param managedIdentityClientId string
param containerAppEnvironmentId string
param postgresqlHost string
param postgresqlUser string
param postgresqlPassword string
param postgresqlDatabase string
param redisHost string
param redisPassword string

// Variables
var uniqueSuffix = uniqueString(resourceGroup().id)
var dashboardAppName = '${projectName}-dashboard-${uniqueSuffix}'
var apiAppName = '${projectName}-api-${uniqueSuffix}'

var tags = {
  environment: environment
  project: projectName
}

// ============================================================================
// Dashboard Container App (Streamlit)
// ============================================================================
resource dashboardContainerApp 'Microsoft.App/containerApps@2023-04-01-preview' = {
  name: dashboardAppName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '/subscriptions/${subscription().subscriptionId}/resourceGroups/${resourceGroup().name}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/${projectName}-identity-${uniqueSuffix}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8501
        transport: 'Auto'
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: [
        {
          server: containerRegistryUrl
          identity: managedIdentityClientId
        }
      ]
      secrets: [
        {
          name: 'postgresql-connection-string'
          value: 'postgresql://${postgresqlUser}:${postgresqlPassword}@${postgresqlHost}:5432/${postgresqlDatabase}'
        }
        {
          name: 'redis-url'
          value: 'redis://:${redisPassword}@${redisHost}:6379/0'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'agentic-iam-dashboard'
          image: '${containerRegistryUrl}/${containerImageName}:${containerImageTag}'
          command: [
            'streamlit'
            'run'
            'app.py'
            '--server.port=8501'
            '--server.address=0.0.0.0'
          ]
          env: [
            {
              name: 'AGENTIC_IAM_ENVIRONMENT'
              value: environment
            }
            {
              name: 'AGENTIC_IAM_DATABASE_URL'
              secretRef: 'postgresql-connection-string'
            }
            {
              name: 'AGENTIC_IAM_REDIS_URL'
              secretRef: 'redis-url'
            }
            {
              name: 'AGENTIC_IAM_ENABLE_TRUST_SCORING'
              value: 'true'
            }
            {
              name: 'AGENTIC_IAM_ENABLE_AUDIT_LOGGING'
              value: 'true'
            }
            {
              name: 'AGENTIC_IAM_ENABLE_MFA'
              value: 'true'
            }
          ]
          resources: {
            cpu: '0.5'
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          {
            name: 'http-requests'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
}

// ============================================================================
// API Container App (FastAPI)
// ============================================================================
resource apiContainerApp 'Microsoft.App/containerApps@2023-04-01-preview' = {
  name: apiAppName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '/subscriptions/${subscription().subscriptionId}/resourceGroups/${resourceGroup().name}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/${projectName}-identity-${uniqueSuffix}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'Auto'
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: [
        {
          server: containerRegistryUrl
          identity: managedIdentityClientId
        }
      ]
      secrets: [
        {
          name: 'postgresql-connection-string'
          value: 'postgresql://${postgresqlUser}:${postgresqlPassword}@${postgresqlHost}:5432/${postgresqlDatabase}'
        }
        {
          name: 'redis-url'
          value: 'redis://:${redisPassword}@${redisHost}:6379/0'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'agentic-iam-api'
          image: '${containerRegistryUrl}/${containerImageName}:${containerImageTag}'
          command: [
            'uvicorn'
            'api.main:app'
            '--host=0.0.0.0'
            '--port=8000'
          ]
          env: [
            {
              name: 'AGENTIC_IAM_ENVIRONMENT'
              value: environment
            }
            {
              name: 'AGENTIC_IAM_DATABASE_URL'
              secretRef: 'postgresql-connection-string'
            }
            {
              name: 'AGENTIC_IAM_REDIS_URL'
              secretRef: 'redis-url'
            }
            {
              name: 'AGENTIC_IAM_ENABLE_TRUST_SCORING'
              value: 'true'
            }
            {
              name: 'AGENTIC_IAM_ENABLE_AUDIT_LOGGING'
              value: 'true'
            }
          ]
          resources: {
            cpu: '0.5'
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          {
            name: 'http-requests'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================
output dashboardUrl string = 'https://${dashboardContainerApp.properties.configuration.ingress.fqdn}'
output apiUrl string = 'https://${apiContainerApp.properties.configuration.ingress.fqdn}'
output dashboardAppName string = dashboardContainerApp.name
output apiAppName string = apiContainerApp.name
