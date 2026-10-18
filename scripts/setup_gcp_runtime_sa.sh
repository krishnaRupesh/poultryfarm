#!/usr/bin/env bash
# ==============================================================================
# Setup Dedicated Cloud Run Runtime Service Account for BigQuery Access
# Usage:
#   ./scripts/setup_gcp_runtime_sa.sh <GCP_PROJECT_ID> [DEPLOYER_SA_EMAIL]
# Example:
#   ./scripts/setup_gcp_runtime_sa.sh my-poultry-project github-actions-sa@my-poultry-project.iam.gserviceaccount.com
# ==============================================================================

set -euo pipefail

PROJECT_ID="${1:-${GCP_PROJECT_ID:-}}"
if [ -z "$PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID is required as first argument or environment variable."
    echo "Usage: $0 <GCP_PROJECT_ID> [DEPLOYER_SA_EMAIL]"
    exit 1
fi

RUNTIME_SA="poultry-cloudrun-sa"
RUNTIME_SA_EMAIL="${RUNTIME_SA}@${PROJECT_ID}.iam.gserviceaccount.com"
DEPLOYER_SA="${2:-}"

echo "=================================================================="
echo "Configuring Cloud Run Runtime Service Account for BigQuery..."
echo "Project ID:           $PROJECT_ID"
echo "Runtime SA Name:      $RUNTIME_SA"
echo "Runtime SA Email:     $RUNTIME_SA_EMAIL"
if [ -n "$DEPLOYER_SA" ]; then
    echo "GitHub Deployer SA:   $DEPLOYER_SA"
fi
echo "=================================================================="

# 1. Enable required GCP APIs
echo "--> Enabling required APIs (run.googleapis.com, bigquery.googleapis.com, iam.googleapis.com)..."
gcloud services enable \
    run.googleapis.com \
    bigquery.googleapis.com \
    iam.googleapis.com \
    artifactregistry.googleapis.com \
    --project="$PROJECT_ID"

# 2. Create the runtime service account if it does not exist
echo "--> Checking if service account $RUNTIME_SA exists..."
if gcloud iam service-accounts describe "$RUNTIME_SA_EMAIL" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "    Service account $RUNTIME_SA already exists."
else
    echo "    Creating service account $RUNTIME_SA..."
    gcloud iam service-accounts create "$RUNTIME_SA" \
        --project="$PROJECT_ID" \
        --display-name="Poultry Farm Cloud Run Runtime Service Account"
    echo "    Service account created successfully."
fi

# 3. Grant BigQuery Job User (roles/bigquery.jobUser)
echo "--> Granting roles/bigquery.jobUser on project $PROJECT_ID..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${RUNTIME_SA_EMAIL}" \
    --role="roles/bigquery.jobUser" \
    --condition=None \
    --quiet

# 4. Grant BigQuery Data Editor (roles/bigquery.dataEditor)
echo "--> Granting roles/bigquery.dataEditor on project $PROJECT_ID..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${RUNTIME_SA_EMAIL}" \
    --role="roles/bigquery.dataEditor" \
    --condition=None \
    --quiet

# 5. Grant Service Account User (roles/iam.serviceAccountUser) to deployer if provided
if [ -n "$DEPLOYER_SA" ]; then
    echo "--> Allowing deployer ($DEPLOYER_SA) to attach $RUNTIME_SA to Cloud Run..."
    gcloud iam service-accounts add-iam-policy-binding "$RUNTIME_SA_EMAIL" \
        --member="serviceAccount:${DEPLOYER_SA}" \
        --role="roles/iam.serviceAccountUser" \
        --project="$PROJECT_ID" \
        --quiet
fi

echo "=================================================================="
echo "Setup Completed Successfully!"
echo "Cloud Run can now execute queries and write DML to BigQuery using:"
echo "  --service-account=${RUNTIME_SA_EMAIL}"
echo "=================================================================="
