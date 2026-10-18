# ==============================================================================
# Setup Dedicated Cloud Run Runtime Service Account for BigQuery Access (PowerShell)
# Usage:
#   .\scripts\setup_gcp_runtime_sa.ps1 -ProjectId "YOUR_GCP_PROJECT_ID" [-DeployerSa "github-actions-sa@..."]
# ==============================================================================
param (
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,

    [Parameter(Mandatory = $false)]
    [string]$DeployerSa = ""
)

$ErrorActionPreference = "Stop"

$RuntimeSa = "poultry-cloudrun-sa"
$RuntimeSaEmail = "${RuntimeSa}@${ProjectId}.iam.gserviceaccount.com"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "Configuring Cloud Run Runtime Service Account for BigQuery..." -ForegroundColor Cyan
Write-Host "Project ID:         $ProjectId"
Write-Host "Runtime SA Name:    $RuntimeSa"
Write-Host "Runtime SA Email:   $RuntimeSaEmail"
if ($DeployerSa) {
    Write-Host "Deployer SA:        $DeployerSa"
}
Write-Host "=================================================================="

# 1. Enable APIs
Write-Host "--> Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com bigquery.googleapis.com iam.googleapis.com artifactregistry.googleapis.com --project=$ProjectId

# 2. Create Runtime SA
Write-Host "--> Checking if service account $RuntimeSa exists..." -ForegroundColor Yellow
$saExists = $false
try {
    gcloud iam service-accounts describe $RuntimeSaEmail --project=$ProjectId 2>$null
    if ($LASTEXITCODE -eq 0) { $saExists = $true }
} catch {
    $saExists = $false
}

if ($saExists) {
    Write-Host "    Service account $RuntimeSa already exists." -ForegroundColor Green
} else {
    Write-Host "    Creating service account $RuntimeSa..." -ForegroundColor Yellow
    gcloud iam service-accounts create $RuntimeSa --project=$ProjectId --display-name="Poultry Farm Cloud Run Runtime Service Account"
    Write-Host "    Service account created successfully." -ForegroundColor Green
}

# 3. Grant BigQuery Job User
Write-Host "--> Granting roles/bigquery.jobUser on project $ProjectId..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $ProjectId --member="serviceAccount:${RuntimeSaEmail}" --role="roles/bigquery.jobUser" --condition=None --quiet

# 4. Grant BigQuery Data Editor
Write-Host "--> Granting roles/bigquery.dataEditor on project $ProjectId..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $ProjectId --member="serviceAccount:${RuntimeSaEmail}" --role="roles/bigquery.dataEditor" --condition=None --quiet

# 5. Grant Service Account User to deployer
if ($DeployerSa) {
    Write-Host "--> Allowing deployer ($DeployerSa) to act as $RuntimeSa..." -ForegroundColor Yellow
    gcloud iam service-accounts add-iam-policy-binding $RuntimeSaEmail --member="serviceAccount:${DeployerSa}" --role="roles/iam.serviceAccountUser" --project=$ProjectId --quiet
}

Write-Host "==================================================================" -ForegroundColor Green
Write-Host "Setup Completed Successfully!" -ForegroundColor Green
Write-Host "Cloud Run can now execute queries and write DML to BigQuery using:" -ForegroundColor Green
Write-Host "  --service-account=${RuntimeSaEmail}" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
