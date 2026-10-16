#!/usr/bin/env bash
# Google Cloud Storage Static Website Deployment Script (Bash)
set -e

BUCKET_NAME="$1"
PROJECT_ID="${2:-$GCP_PROJECT_ID}"
CLOUD_RUN_URL="$3"

if [ -z "$BUCKET_NAME" ]; then
    echo "Usage: ./deploy-gcs.sh <bucket-name> [project-id] [cloud-run-url]"
    exit 1
fi

echo "Deploying Frontend to gs://$BUCKET_NAME in project ${PROJECT_ID:-default}..."

# 1. Create bucket if not exists
if ! gcloud storage buckets describe "gs://$BUCKET_NAME" >/dev/null 2>&1; then
    echo "Creating bucket gs://$BUCKET_NAME..."
    gcloud storage buckets create "gs://$BUCKET_NAME" --project="$PROJECT_ID" --location=US
fi

# 2. Configure bucket website configuration
echo "Configuring bucket website properties..."
gcloud storage buckets update "gs://$BUCKET_NAME" --web-main-page-suffix=index.html --web-error-page=index.html

# 3. Grant public read permissions (allUsers)
echo "Setting public read access..."
gcloud storage buckets add-iam-policy-binding "gs://$BUCKET_NAME" --member="allUsers" --role="roles/storage.objectViewer"

# 4. Inject Cloud Run URL if provided
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -n "$CLOUD_RUN_URL" ]; then
    echo "Configuring API Base URL: $CLOUD_RUN_URL"
    echo "window.API_BASE_URL = '$CLOUD_RUN_URL';" > "$SCRIPT_DIR/js/api-config.js"
fi

# 5. Sync files
echo "Syncing static files to gs://$BUCKET_NAME..."
gcloud storage rsync -r "$SCRIPT_DIR" "gs://$BUCKET_NAME"

echo "Frontend deployed successfully!"
echo "URL: http://storage.googleapis.com/$BUCKET_NAME/index.html"
