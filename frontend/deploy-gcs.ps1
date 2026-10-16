# Google Cloud Storage Static Website Deployment Script (PowerShell)
param(
    [Parameter(Mandatory=$true)]
    [string]$BucketName,

    [Parameter(Mandatory=$false)]
    [string]$ProjectId = $env:GCP_PROJECT_ID,

    [Parameter(Mandatory=$false)]
    [string]$CloudRunUrl = ""
)

Write-Host "Deploying Poultry Farm Frontend to Google Cloud Storage bucket: gs://$BucketName" -ForegroundColor Cyan

# 1. Ensure bucket exists
Write-Host "1. Checking/Creating bucket..." -ForegroundColor Yellow
$bucketExists = gcloud storage buckets describe "gs://$BucketName" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating bucket gs://$BucketName in project $ProjectId..."
    gcloud storage buckets create "gs://$BucketName" --project=$ProjectId --location=US
}

# 2. Configure bucket website configuration
Write-Host "2. Configuring bucket website properties..." -ForegroundColor Yellow
gcloud storage buckets update "gs://$BucketName" --web-main-page-suffix=index.html --web-error-page=index.html

# 3. Grant public read permissions (allUsers)
Write-Host "3. Setting public read access..." -ForegroundColor Yellow
gcloud storage buckets add-iam-policy-binding "gs://$BucketName" --member="allUsers" --role="roles/storage.objectViewer"

# 4. Optional: Set API Base URL for remote Cloud Run
$FrontendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($CloudRunUrl -ne "") {
    Write-Host "Configuring API Base URL to: $CloudRunUrl" -ForegroundColor Green
    $configContent = "window.API_BASE_URL = '$CloudRunUrl';"
    Set-Content -Path (Join-Path $FrontendDir "js\api-config.js") -Value $configContent
}

# 5. Sync static files
Write-Host "4. Uploading HTML, CSS, and JS assets..." -ForegroundColor Yellow
gcloud storage rsync -r "$FrontendDir" "gs://$BucketName"

Write-Host "`nDeployment completed successfully!" -ForegroundColor Green
Write-Host "Website URL (HTTP): http://storage.googleapis.com/$BucketName/index.html" -ForegroundColor Cyan
