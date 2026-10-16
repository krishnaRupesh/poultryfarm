# Google Cloud Platform & GitHub Actions Deployment Guide

This guide walks you step-by-step through setting up Google Cloud Platform (GCP) and GitHub Actions to deploy the Poultry Farm Management application with:
- **Google BigQuery**: Partitioned & clustered data warehouse tables.
- **Google Cloud Run**: Serverless container running Flask + Gunicorn (scales to 0 when idle = **$0 cost**).
- **GitHub Actions**: Fully automated CI/CD pipeline on `git push`.

---

## 1. Prerequisites Checklist

Before running the GitHub Actions deployment workflow, you will need:
1. A **Google Cloud Platform (GCP) Account** (with active billing enabled; all services used operate well within GCP's permanent Free Tier).
2. A **GCP Project ID** (e.g. `poultry-farm-prod` or `my-poultry-app-421500`).
3. The **`gcloud` CLI** installed locally (or you can use **Google Cloud Shell** directly in your browser).
4. Administrator permissions on your **GitHub repository** (to add Repository Secrets).

---

## 2. Step-by-Step GCP Setup Commands

Open **Google Cloud Shell** in your browser at [https://shell.cloud.google.com](https://shell.cloud.google.com) (or open your local terminal with `gcloud` installed), and run the following commands:

### Step 2.1: Set Your Project ID
```bash
export PROJECT_ID="YOUR_GCP_PROJECT_ID"
gcloud config set project $PROJECT_ID
```

---

### Step 2.2: Enable Required Google APIs
Enable Cloud Run, Artifact Registry, BigQuery, and Resource Manager APIs:
```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  bigquery.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iam.googleapis.com
```

---

### Step 2.3: Create a Service Account for GitHub Actions
Create a dedicated deployment service account:
```bash
gcloud iam service-accounts create github-deployer \
  --display-name="GitHub Actions CI/CD Deployer"
```

---

### Step 2.4: Grant Necessary IAM Roles to the Service Account
Grant permissions to deploy to Cloud Run, push Docker images to Artifact Registry, manage BigQuery, and act as a runtime service account:

```bash
SA_EMAIL="github-deployer@${PROJECT_ID}.iam.gserviceaccount.com"

# 1. Cloud Run Admin (to deploy and manage Cloud Run services)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

# 2. Artifact Registry Writer (to push Docker images to Artifact Registry)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.writer"

# 3. Storage Admin (for deployment storage access)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

# 4. BigQuery Admin (to create dataset and manage BigQuery tables)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/bigquery.admin"

# 5. Service Account User (to allow Cloud Run to run using the default compute service account)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"
```

---

### Step 2.5: Generate the Service Account JSON Key
Download the key file containing the service account credentials:
```bash
gcloud iam service-accounts keys create gcp-key.json \
  --iam-account="${SA_EMAIL}"
```

Display the contents of the key file (you will copy this into GitHub):
```bash
cat gcp-key.json
```

*(You can delete the local `gcp-key.json` file once copied to GitHub).*

---

## 3. Add GitHub Repository Secrets

Go to your GitHub repository in your web browser:
1. Navigate to: **Settings** -> **Secrets and variables** -> **Actions**
2. Click **New repository secret** and add the following two secrets:

| Secret Name | Value | Description |
| :--- | :--- | :--- |
| `GCP_PROJECT_ID` | e.g. `your-project-id` | Your exact Google Cloud Project ID string. |
| `GCP_SA_KEY` | Contents of `gcp-key.json` | The entire JSON string starting with `{"type": "service_account", ...}`. |

---

## 4. Trigger Deployment

Once your secrets are saved in GitHub, deployment is completely automated:

### Automatic Trigger:
Simply push code to the `main` branch:
```bash
git add .
git commit -m "Deploy to GCP Cloud Run and BigQuery"
git push origin main
```

### Manual Trigger:
1. Go to your GitHub repository -> **Actions** tab.
2. Click **Deploy to Google Cloud (Cloud Run & BigQuery)** in the left sidebar.
3. Click **Run workflow** -> Select `main` -> Click **Run workflow**.

---

## 5. What Happens During Deployment

The GitHub Actions workflow will automatically:
1. **Authenticate**: Securely connect to Google Cloud using your Service Account key.
2. **BigQuery DDL**: Create the `poultry_farm` dataset, partitioned tables (`feed_items`, `feed_purchases`, `daily_flock_status`, `daily_feed_consumption`, `daily_egg_operations`, etc.), and the analytical view `v_daily_cost_and_profitability_summary`.
3. **Docker Build**: Build the production container image with `gunicorn` and multi-threaded concurrency.
4. **Push Container**: Upload the image to Google Container Registry (`gcr.io/$PROJECT_ID/poultry-farm-app`).
5. **Deploy Cloud Run**: Deploy the container with `--min-instances 0` (**scales to zero when idle = $0/month cost**).
6. **Print URLs**: Outputs your live application URL (e.g. `https://poultry-farm-app-xyz.a.run.app`) and Swagger docs URL (`https://poultry-farm-app-xyz.a.run.app/apidocs`).
