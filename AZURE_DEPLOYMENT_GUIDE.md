# Azure Deployment Guide - Agentic-IAM

This guide walks you through deploying Agentic-IAM to Azure Container Apps.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Azure Subscription** — An active Azure subscription
2. **Azure CLI** — Install from [https://aka.ms/cli](https://aka.ms/cli)
3. **Azure Developer CLI** — Install from [https://aka.ms/azd](https://aka.ms/azd)
4. **Docker** — Install from [https://www.docker.com](https://www.docker.com)
5. **Python 3.11+** — For local testing
6. **PowerShell** — For running deployment scripts

### Quick Install (Windows)

```powershell
# Install Azure CLI
choco install azure-cli

# Install Azure Developer CLI
choco install azure-developer-cli

# Install Docker
choco install docker-desktop
```

---

## 🚀 Quick Deployment

### Option 1: Automated Script (Recommended)

```powershell
# Deploy to production
.\deploy-to-azure.ps1 -Environment prod -Location eastus

# Deploy to staging
.\deploy-to-azure.ps1 -Environment staging -Location eastus
```

### Option 2: Manual Deployment

#### Step 1: Authenticate with Azure

```bash
az login
az account show  # Verify you're in the right subscription
```

#### Step 2: Create Resource Group

```bash
az group create \
  --name agentic-iam-prod \
  --location eastus
```

#### Step 3: Build and Push Docker Image

```bash
# Create container registry
az acr create \
  --resource-group agentic-iam-prod \
  --name agenticiam \
  --sku Standard

# Login to registry
az acr login --name agenticiam

# Build image
docker build -t agenticiam.azurecr.io/agentic-iam:latest -f Dockerfile --target production .

# Push image
docker push agenticiam.azurecr.io/agentic-iam:latest
```

#### Step 4: Deploy Infrastructure

```bash
# Validate Bicep template
az bicep build ./infra/main.bicep

# Deploy
az deployment group create \
  --resource-group agentic-iam-prod \
  --template-file ./infra/main.bicep \
  --parameters \
    location=eastus \
    environment=prod \
    containerImageName=agentic-iam \
    containerRegistryUrl=agenticiam.azurecr.io
```

#### Step 5: Verify Deployment

```bash
# Check deployment status
az deployment group list --resource-group agentic-iam-prod

# Get container app URLs
az containerapp list --resource-group agentic-iam-prod --query "[].properties.configuration.ingress.fqdn"
```

---

## 📦 What Gets Deployed

The Bicep templates create:

### Compute
- **Azure Container Apps** (Dashboard + API)
- Auto-scaling (min: 1, max: 3 replicas)
- Internal networking

### Data
- **Azure Database for PostgreSQL** (Flexible Server)
  - SKU: Standard_B2s (burstable)
  - Storage: 32GB
  - 7-day backup retention
- **Azure Cache for Redis**
  - SKU: Standard
  - Capacity: 1 (1GB)

### Networking
- **Virtual Network** (10.0.0.0/16)
- **Private Endpoints** for secure database access
- **Private DNS Zone** for PostgreSQL

### Security
- **Azure Key Vault** for secrets management
- **Managed Identity** for authentication
- **HTTPS Ingress** for Container Apps

### Monitoring
- **Application Insights** for performance monitoring
- **Log Analytics Workspace** for centralized logging
- **Prometheus metrics** exposed on port 9090

---

## 🔐 Secrets Management

Secrets are stored in Azure Key Vault:

```bash
# List secrets
az keyvault secret list --vault-name agentic-iam-kv-xxx

# Get a secret
az keyvault secret show --vault-name agentic-iam-kv-xxx --name postgresql-password

# Set a secret
az keyvault secret set \
  --vault-name agentic-iam-kv-xxx \
  --name my-secret \
  --value "secret-value"
```

### Required Secrets

Create these in Key Vault before deployment:

```bash
# PostgreSQL password
az keyvault secret set \
  --vault-name $KEYVAULT_NAME \
  --name postgresql-password \
  --value "ComplexPassword123!@#"

# JWT secret
az keyvault secret set \
  --vault-name $KEYVAULT_NAME \
  --name jwt-secret \
  --value "your-jwt-secret-key"

# Encryption key
az keyvault secret set \
  --vault-name $KEYVAULT_NAME \
  --name encryption-key \
  --value "32-character-encryption-key!!!"
```

---

## 📊 Monitoring & Logging

### View Logs

```bash
# Container app logs
az containerapp logs show \
  --name agentic-iam-dashboard-xxx \
  --resource-group agentic-iam-prod \
  --follow

# PostgreSQL logs
az postgres flexible-server server-logs list \
  --resource-group agentic-iam-prod \
  --server-name agentic-iam-db-xxx

# Redis info
az redis list \
  --resource-group agentic-iam-prod
```

### Monitor Performance

```bash
# View metrics in Application Insights
az monitor metrics list \
  --resource-group agentic-iam-prod \
  --resource-type Microsoft.Insights/components \
  --resource agentic-iam-insights-xxx
```

---

## 🔄 Scaling

### Scale Container Apps

```bash
# Scale to 3 replicas
az containerapp update \
  --name agentic-iam-dashboard-xxx \
  --resource-group agentic-iam-prod \
  --min-replicas 3 \
  --max-replicas 5

# Check current scaling
az containerapp show \
  --name agentic-iam-dashboard-xxx \
  --resource-group agentic-iam-prod \
  --query "properties.template.scale"
```

### Scale PostgreSQL

```bash
# Upgrade to larger SKU
az postgres flexible-server update \
  --resource-group agentic-iam-prod \
  --name agentic-iam-db-xxx \
  --sku-name Standard_D2s_v3 \
  --tier GeneralPurpose
```

---

## 🔄 Updating the Application

### Deploy New Version

```bash
# Build new image
docker build -t agenticiam.azurecr.io/agentic-iam:v1.0.1 .

# Push to registry
docker push agenticiam.azurecr.io/agentic-iam:v1.0.1

# Update container app
az containerapp update \
  --name agentic-iam-api-xxx \
  --resource-group agentic-iam-prod \
  --image agenticiam.azurecr.io/agentic-iam:v1.0.1
```

---

## 🗑️ Cleanup

### Delete Resources

```bash
# Delete entire resource group
az group delete --name agentic-iam-prod

# Or delete individual resources
az containerapp delete --name agentic-iam-dashboard-xxx --resource-group agentic-iam-prod
az postgres flexible-server delete --name agentic-iam-db-xxx --resource-group agentic-iam-prod
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check container app status
az containerapp show \
  --name agentic-iam-dashboard-xxx \
  --resource-group agentic-iam-prod \
  --query "properties.provisioningState"

# View recent logs
az containerapp logs show \
  --name agentic-iam-dashboard-xxx \
  --resource-group agentic-iam-prod \
  --tail 50
```

### Database Connection Issues

```bash
# Check PostgreSQL server status
az postgres flexible-server show \
  --name agentic-iam-db-xxx \
  --resource-group agentic-iam-prod

# Check firewall rules
az postgres flexible-server firewall-rule list \
  --name agentic-iam-db-xxx \
  --resource-group agentic-iam-prod
```

### DNS Resolution Issues

```bash
# Check private DNS zone
az network private-dns zone list --resource-group agentic-iam-prod

# Check DNS records
az network private-dns record-set list \
  --zone-name prod.postgres.database.azure.com \
  --resource-group agentic-iam-prod
```

---

## 💰 Cost Estimation

Approximate monthly costs for the deployed infrastructure:

| Service | SKU | Cost |
|---------|-----|------|
| Container Apps | Consumption | ~$20-50 |
| PostgreSQL | Standard_B2s | ~$50-100 |
| Azure Cache for Redis | Standard (1GB) | ~$15-20 |
| Key Vault | Standard | ~$0.60 |
| Log Analytics | 5GB | ~$2.50 |
| **Total (Monthly)** | — | **~$88-170** |

---

## 📚 Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Bicep Language Reference](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/file)
- [Azure Developer CLI Documentation](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [PostgreSQL Flexible Server](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/)

---

## ✅ Deployment Checklist

- [ ] Azure subscription created and verified
- [ ] Azure CLI and Docker installed
- [ ] Logged into Azure with correct subscription
- [ ] Container registry created
- [ ] Docker image built and pushed
- [ ] PostgreSQL password set in Key Vault
- [ ] Bicep template validated
- [ ] Infrastructure deployed successfully
- [ ] Container apps are running
- [ ] Database accessible from containers
- [ ] Application health check passing
- [ ] Monitoring enabled in Application Insights

---

## 🆘 Support

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review container app logs: `az containerapp logs show ...`
3. Check Azure Monitor metrics
4. Open an issue in the repository

---

**Last Updated:** May 2026
