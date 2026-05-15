# Pre-Deployment Checklist - Agentic-IAM Azure Deployment

**Status:** Ready to Deploy ✓  
**Validation Status:** PASSED ✓  
**Date:** May 8, 2026

---

## 📋 Pre-Deployment Requirements

### ✓ Azure Account & Subscription

- [ ] You have an active Azure subscription
- [ ] You have Owner or Contributor role on the subscription
- [ ] You know your subscription ID: `_____________________`

### ✓ Azure Tools Installation

- [ ] Azure CLI installed (check: `az --version`)
- [ ] Azure Developer CLI installed (check: `azd --version`)
- [ ] Docker Desktop installed (check: `docker --version`)
- [ ] PowerShell 5.1+ installed

### ✓ Local Authentication

- [ ] You are logged into Azure CLI: `az login`
- [ ] Correct subscription is selected: `az account show`
- [ ] Docker is logged into Azure Container Registry (will be set up during deployment)

### ✓ Resource Constraints

- [ ] Your subscription has quota for:
  - [ ] Container Apps (Standard pricing)
  - [ ] PostgreSQL Flexible Server
  - [ ] Azure Cache for Redis
  - [ ] Azure Container Registry

### ✓ Naming & Location

- [ ] Deployment region chosen: **eastus** (default, can be changed)
- [ ] Project name: **agentic-iam** (change if needed)
- [ ] Environment: **prod**, **staging**, or **dev** (choose one)

### ✓ Configuration

- [ ] PostgreSQL admin password is secure (will be generated)
- [ ] All secrets will be stored in Azure Key Vault
- [ ] HTTPS will be enforced on all endpoints

---

## 🚀 Quick Start Deployment

### Option 1: Fully Automated Script (Recommended)

```powershell
# Navigate to project directory
cd C:\Users\Lenovo\Desktop\Agentic-IAM-main

# Run deployment script
.\deploy-to-azure.ps1 -Environment prod -Location eastus
```

**What this does:**
- Checks all prerequisites
- Authenticates with Azure
- Creates resource group
- Builds Docker image
- Pushes to Container Registry
- Deploys infrastructure with Bicep
- Configures Container Apps
- Verifies health checks

**Estimated time:** 15-20 minutes

### Option 2: Step-by-Step Manual Deployment

See [AZURE_DEPLOYMENT_GUIDE.md](./AZURE_DEPLOYMENT_GUIDE.md) for detailed manual steps.

---

## 💰 Estimated Costs

### Monthly Cost Breakdown

| Resource | Tier | Est. Cost |
|----------|------|-----------|
| Container Apps | Consumption | $30-50 |
| PostgreSQL | Standard_B2s | $60-80 |
| Redis | Standard 1GB | $15-20 |
| Container Registry | Standard | $10-15 |
| Key Vault | Standard | $0.60 |
| Application Insights | 5GB | $2.50 |
| **Monthly Total** | — | **~$120-170** |

💡 **Cost Saving Tips:**
- Use `dev` environment for non-production testing
- Scale down Container Apps replicas when not in use
- Set up Azure Cost Alerts to monitor spending
- Use Reserved Instances for PostgreSQL if committed long-term

---

## ⚠️ Important Notes

### Before You Deploy

1. **Secrets & Passwords**
   - A strong PostgreSQL password will be generated automatically
   - Store it securely in Azure Key Vault
   - Do NOT hardcode passwords in environment variables

2. **Network Security**
   - PostgreSQL uses private endpoints (not exposed to internet)
   - Container Apps have public HTTPS endpoints
   - Azure Firewall recommendations provided in deployment guide

3. **Data Persistence**
   - Database data is persisted in Azure PostgreSQL
   - Regular backups enabled (7-day retention)
   - Backup configuration can be modified post-deployment

4. **Monitoring**
   - Application Insights enabled for performance tracking
   - Logs retained for 30 days
   - Custom metrics available in Azure Portal

---

## 🔍 Verification Steps (After Deployment)

After deployment completes, verify:

```bash
# 1. Check Container Apps are running
az containerapp list --resource-group agentic-iam-prod

# 2. Test API health endpoint
curl https://agentic-iam-api-xxx.azurecontainerapps.io/health

# 3. Access dashboard in browser
# https://agentic-iam-dashboard-xxx.azurecontainerapps.io

# 4. Check logs for errors
az containerapp logs show \
  --name agentic-iam-dashboard-xxx \
  --resource-group agentic-iam-prod
```

---

## 🆘 Troubleshooting

### Common Issues

**Issue: Container won't start**
```bash
az containerapp logs show --name <app-name> --resource-group agentic-iam-prod
```

**Issue: Database connection failed**
- Check private DNS zone is linked to VNet
- Verify PostgreSQL firewall rules
- Check connection string in Key Vault

**Issue: Deployment times out**
- Check Azure Container Registry availability
- Verify Docker image was pushed successfully
- Check resource quotas in subscription

See [AZURE_DEPLOYMENT_GUIDE.md](./AZURE_DEPLOYMENT_GUIDE.md) for detailed troubleshooting.

---

## 📞 Support

If you encounter issues:

1. Check deployment logs: `az deployment group show --resource-group agentic-iam-prod`
2. Review Container App logs: `az containerapp logs show ...`
3. Check Application Insights: Azure Portal → Resource Group → Application Insights
4. Run diagnostics: `az containerapp diagnose --name <app-name> ...`

---

## ✅ Deployment Readiness Checklist

- [x] Bicep templates validated
- [x] Docker image configuration ready
- [x] Python dependencies verified
- [x] Deployment scripts prepared
- [x] Documentation complete
- [ ] **User confirms prerequisites met**
- [ ] **Ready to execute deployment**

---

## 🎯 Next Steps

### To Deploy Now:

```powershell
.\deploy-to-azure.ps1 -Environment prod -Location eastus
```

### To Review Configuration First:

1. Review `azure.yaml` configuration
2. Review `infra/main.bicep` template
3. Review `AZURE_DEPLOYMENT_GUIDE.md` documentation
4. Then run deployment script

---

**Ready to deploy? Run the command above or confirm you want to proceed!**

Estimated deployment time: **15-20 minutes**  
Estimated monthly cost: **$120-170**
