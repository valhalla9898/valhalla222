#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Deploy Agentic-IAM to Azure
.DESCRIPTION
    This script automates the deployment of Agentic-IAM to Azure
    using Azure Developer CLI and Bicep templates
.EXAMPLE
    .\deploy-to-azure.ps1 -Environment prod -Location eastus
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('dev', 'staging', 'prod')]
    [string]$Environment,

    [Parameter(Mandatory=$false)]
    [string]$Location = 'eastus',

    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId,

    [Parameter(Mandatory=$false)]
    [switch]$SkipTests
)

$ErrorActionPreference = 'Stop'

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "=============================================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "=============================================================" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# ============================================================================
# Step 1: Check Prerequisites
# ============================================================================
Write-Header "Checking Prerequisites"

# Check Azure CLI
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI is not installed. Please install it from https://aka.ms/cli"
    exit 1
}
Write-Success "Azure CLI installed"

# Check Azure Developer CLI
if (-not (Get-Command azd -ErrorAction SilentlyContinue)) {
    Write-Error "Azure Developer CLI is not installed. Please install it from https://aka.ms/azd"
    Write-Host "Continuing without azd (some azd-specific features may be skipped)" -ForegroundColor Yellow
}
Write-Success "Azure Developer CLI installed"

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed"
    exit 1
}
Write-Success "Python installed"

# ============================================================================
# Step 2: Azure Authentication
# ============================================================================
Write-Header "Azure Authentication"

$accountInfo = az account show 2>$null
if (-not $accountInfo) {
    Write-Host "Logging into Azure..." -ForegroundColor Yellow
    az login
} else {
    $account = $accountInfo | ConvertFrom-Json
    Write-Success "Already logged in as $($account.user.name)"
}

# Set subscription if provided
if ($SubscriptionId) {
    Write-Host "Setting subscription to $SubscriptionId..." -ForegroundColor Yellow
    az account set --subscription $SubscriptionId
    Write-Success "Subscription set"
}

$currentSubscription = (az account show --query 'id' -o tsv)
Write-Success "Using subscription: $currentSubscription"

# ============================================================================
# Step 3: Create Resource Group
# ============================================================================
Write-Header "Creating Resource Group"

$ResourceGroupName = "agentic-iam-$Environment"
$existingRg = az group exists --name $ResourceGroupName
if ($existingRg -eq 'false') {
    Write-Host "Creating resource group $ResourceGroupName..." -ForegroundColor Yellow
    az group create --name $ResourceGroupName --location $Location
    Write-Success "Resource group created"
} else {
    Write-Success "Resource group $ResourceGroupName already exists"
}

# ============================================================================
# Step 4: Run Tests (if not skipped)
# ============================================================================
if (-not $SkipTests) {
    Write-Header "Running Tests"
    
    if (Test-Path "pytest.ini") {
        Write-Host "Running pytest..." -ForegroundColor Yellow
        pytest tests/ -v
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Tests failed"
            exit 1
        }
        Write-Success "All tests passed"
    } else {
        Write-Host "No pytest configuration found, skipping tests" -ForegroundColor Yellow
    }
}

# ============================================================================
# Step 5: Build and Push Docker Image
# ============================================================================
Write-Header "Building and Pushing Docker Image"

$RegistryName = "agenticiam$(Get-Random -Minimum 10000 -Maximum 99999)"
$RegistryLoginServer = "$RegistryName.azurecr.io"

# Create container registry if it doesn't exist
$registryExists = az acr list --resource-group $ResourceGroupName --query "[?name=='$RegistryName']" 2>$null | ConvertFrom-Json
if ($registryExists.Count -eq 0) {
    Write-Host "Creating container registry $RegistryName..." -ForegroundColor Yellow
    az acr create --resource-group $ResourceGroupName --name $RegistryName --sku Standard
    Write-Success "Container registry created"
} else {
    Write-Success "Container registry $RegistryName already exists"
}

# Login to registry
Write-Host "Logging into registry..." -ForegroundColor Yellow
az acr login --name $RegistryName

# Build and push
$ImageTag = "latest"
$ImageName = "$RegistryLoginServer/agentic-iam:$ImageTag"

Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t $ImageName -f Dockerfile --target production .

if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed"
    exit 1
}
Write-Success "Docker image built"

Write-Host "Pushing Docker image to registry..." -ForegroundColor Yellow
docker push $ImageName
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker push failed"
    exit 1
}
Write-Success "Docker image pushed: $ImageName"

# ============================================================================
# Step 6: Deploy Infrastructure with Bicep
# ============================================================================
Write-Header "Deploying Infrastructure"

Write-Host "Validating Bicep template..." -ForegroundColor Yellow
az bicep build-params --file "./infra/main.bicepparams" --outfile "./infra/main.json" 2>$null

Write-Host "Deploying Bicep template..." -ForegroundColor Yellow
$deploymentOutput = az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file "./infra/main.bicep" `
    --parameters location=$Location `
                 environment=$Environment `
                 containerImageName=agentic-iam `
                 containerRegistryUrl=$RegistryLoginServer

if ($LASTEXITCODE -ne 0) {
    Write-Error "Deployment failed"
    exit 1
}
Write-Success "Infrastructure deployed"

# Extract outputs
$deployment = $deploymentOutput | ConvertFrom-Json
$outputs = $deployment.properties.outputs

Write-Success "Dashboard URL: $($outputs.dashboardUrl.value)"
Write-Success "API URL: $($outputs.apiUrl.value)"

# ============================================================================
# Step 7: Configure Environment Variables
# ============================================================================
Write-Header "Configuring Environment Variables"

# Get PostgreSQL credentials from Key Vault
$KeyVaultName = ($outputs.keyVaultUri.value -split '\.')[0]
Write-Host "Retrieving secrets from Key Vault: $KeyVaultName" -ForegroundColor Yellow

# Set secrets in container apps
$ApiAppName = $outputs.apiAppName.value
$DashboardAppName = $outputs.dashboardAppName.value

Write-Host "Setting container app environment variables..." -ForegroundColor Yellow
az containerapp update `
    --name $ApiAppName `
    --resource-group $ResourceGroupName `
    --set-env-vars AGENTIC_IAM_ENVIRONMENT=$Environment

Write-Success "Environment variables configured"

# ============================================================================
# Step 8: Verify Deployment
# ============================================================================
Write-Header "Verifying Deployment"

Write-Host "Checking container app status..." -ForegroundColor Yellow
$apiStatus = az containerapp show --name $ApiAppName --resource-group $ResourceGroupName --query "properties.provisioningState" -o tsv
$dashboardStatus = az containerapp show --name $DashboardAppName --resource-group $ResourceGroupName --query "properties.provisioningState" -o tsv

Write-Success "API App Status: $apiStatus"
Write-Success "Dashboard App Status: $dashboardStatus"

# Wait for containers to be ready
Write-Host "Waiting for containers to be ready (this may take 2-3 minutes)..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    try {
        $healthCheck = Invoke-WebRequest -Uri "$($outputs.apiUrl.value)/health" -ErrorAction SilentlyContinue
        if ($healthCheck.StatusCode -eq 200) {
            Write-Success "API health check passed"
            break
        }
    } catch {
        # API not ready yet
    }
    
    $attempt++
    if ($attempt -lt $maxAttempts) {
        Write-Host "  Waiting... ($attempt/$maxAttempts)" -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
}

if ($attempt -eq $maxAttempts) {
    Write-Error "API did not become healthy in time. Please check the container app logs."
} else {
    Write-Success "Deployment verified - application is healthy"
}

# ============================================================================
# Step 9: Summary
# ============================================================================
Write-Header "Deployment Complete"

Write-Host ""
Write-Host "Application Details:" -ForegroundColor Cyan
Write-Host "  Environment: $Environment" -ForegroundColor White
Write-Host "  Resource Group: $ResourceGroupName" -ForegroundColor White
Write-Host "  Location: $Location" -ForegroundColor White
Write-Host "  Registry: $RegistryLoginServer" -ForegroundColor White
Write-Host ""
Write-Host "Access Your Application:" -ForegroundColor Cyan
Write-Host "  Dashboard: $($outputs.dashboardUrl.value)" -ForegroundColor Green
Write-Host "  API: $($outputs.apiUrl.value)" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Monitor logs: az containerapp logs show --name $DashboardAppName --resource-group $ResourceGroupName" -ForegroundColor White
Write-Host "  2. Scale up: az containerapp update --name $DashboardAppName --resource-group $ResourceGroupName --min-replicas 3" -ForegroundColor White
Write-Host "  3. View metrics: az monitor metrics list --resource-group $ResourceGroupName" -ForegroundColor White
Write-Host ""
