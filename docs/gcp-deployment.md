# Deploy the Backend to Google Cloud

This guide prepares a Google Cloud project so the repository's GitHub Actions workflow can build the backend image, push it to Artifact Registry, and deploy it to Cloud Run. It covers setup in the Google Cloud Console and with the `gcloud` CLI on Windows PowerShell.

The workflow is `.github/workflows/deploy-backend-public.yml`. It uses Workload Identity Federation (WIF), so you do **not** create or store a service-account key file in GitHub.

> **Access and cost:** Cloud Run requires Google IAM authentication after the updated deployment succeeds; until then, an already-deployed service keeps its current access policy. A URL alone will not be sufficient to call the updated service. Only principals granted `roles/run.invoker` can invoke it. Authorized callers can still cause Vertex AI usage charges, so set billing budgets and alerts. For Swagger testing, use the authenticated `gcloud run services proxy` steps below.

## What You Need

- A Google account with permission to create projects or use an existing Google Cloud project, enable APIs, create service accounts, grant IAM roles, and configure Workload Identity Federation.
- Billing enabled for the project.
- A GitHub repository containing this application and the workflow on its `main` branch.
- The GitHub organization or username and repository name, for example `Hadjerkhd/production-ai-template`.
- Google Cloud CLI (`gcloud`) installed if you plan to use the CLI path.

Choose these values first and use them consistently:

| Value | Example | Meaning |
| --- | --- | --- |
| Project ID | `my-ai-project-123` | Stable project identifier; not the display name or project number |
| Region | `us-central1` | Region for Artifact Registry and Cloud Run; the workflow also uses it for Vertex AI |
| GitHub repository | `Hadjerkhd/production-ai-template` | Exact `OWNER/REPOSITORY`, including capitalization |
| Artifact Registry repository | `production-ai` | Already fixed in the workflow |
| Cloud Run service | `production-ai-api-public` | Existing workflow service name; IAM authentication will be required |
| WIF pool ID | `github-actions` | Choose a short ID; used in the provider resource name |
| WIF provider ID | `github` | Choose a short ID; used in the provider resource name |
| Deployer service account ID | `github-deployer` | Identity that GitHub Actions impersonates to deploy |
| Runtime service account ID | `production-ai-runtime` | Identity used by the running Cloud Run service to call Vertex AI |

## Setup in Google Cloud Console

### 1. Create or select a project

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Use the project selector in the top bar to select an existing project, or choose **New Project** and create one.
3. Open **Billing** and link an active billing account to the project.
4. Record the **Project ID**. You will use this for the GitHub variable `GCP_PROJECT_ID`.

### 2. Enable the required APIs

In the project, open **APIs & Services → Library** and enable:

- Cloud Run Admin API (`run.googleapis.com`)
- Artifact Registry API (`artifactregistry.googleapis.com`)
- Vertex AI API (`aiplatform.googleapis.com`)
- IAM API (`iam.googleapis.com`)
- IAM Service Account Credentials API (`iamcredentials.googleapis.com`)
- Security Token Service API (`sts.googleapis.com`)

If the Console asks you to enable Service Usage API (`serviceusage.googleapis.com`) to enable other APIs, enable it as well.

### 3. Create the Artifact Registry Docker repository

1. Open **Artifact Registry → Repositories**.
2. Choose **Create Repository**.
3. Set the repository name to `production-ai`.
4. Set **Format** to **Docker**.
5. Set **Location type** to **Region** and choose the same region you chose above, for example `us-central1`.
6. Create the repository.

The workflow constructs image names in this format:

```text
REGION-docker.pkg.dev/PROJECT_ID/production-ai/production-ai-api-public:GITHUB_SHA
```

### 4. Create the Cloud Run runtime service account

1. Open **IAM & Admin → Service Accounts** and choose **Create Service Account**.
2. Use `production-ai-runtime` as the service account ID. A typical email will be `production-ai-runtime@PROJECT_ID.iam.gserviceaccount.com`.
3. Create the account. Do not create a key.
4. Grant this account the **Vertex AI User** role (`roles/aiplatform.user`) on the project. In the Console, open **IAM & Admin → IAM**, choose **Grant Access**, enter the runtime service account email as the principal, and select **Vertex AI User**.

This is the identity Cloud Run uses when the app accesses Vertex AI.

### 5. Create the GitHub deployer service account

1. In **IAM & Admin → Service Accounts**, choose **Create Service Account**.
2. Use `github-deployer` as the service account ID. Its email will look like `github-deployer@PROJECT_ID.iam.gserviceaccount.com`.
3. Create the account. Do not create a key.
4. Grant this service account these project roles:
   - **Cloud Run Admin** (`roles/run.admin`)
   - **Artifact Registry Writer** (`roles/artifactregistry.writer`)
5. Also grant it **Service Account User** (`roles/iam.serviceAccountUser`) on the *runtime service account*. To do this, open the runtime account in **IAM & Admin → Service Accounts**, open its permissions/access panel, and grant the deployer service account that role.

The deployer identity needs to push the image and tell Cloud Run which runtime identity to use.

### 6. Configure Workload Identity Federation for GitHub

WIF trusts GitHub's short-lived OIDC identity tokens. Restrict the provider to your exact repository and the `main` branch.

1. Open **IAM & Admin → Workload Identity Federation**.
2. Choose **Create Pool**. Use pool ID `github-actions`, then create the pool.
3. Within that pool, choose **Add Provider** and select **OpenID Connect (OIDC)**.
4. Use provider ID `github` and issuer URL:

   ```text
   https://token.actions.githubusercontent.com
   ```

5. Configure these attribute mappings:

   | Google attribute | OIDC assertion |
   | --- | --- |
   | `google.subject` | `assertion.sub` |
   | `attribute.repository` | `assertion.repository` |
   | `attribute.ref` | `assertion.ref` |

6. Set an attribute condition restricting access to your repository's `main` branch. Replace the example owner and repository with yours:

   ```text
   assertion.repository == 'Hadjerkhd/production-ai-template' && assertion.ref == 'refs/heads/main'
   ```

7. Save the provider.
8. Grant the provider's repository identity permission to impersonate the deployer service account. In **IAM & Admin → Service Accounts**, open the deployer account, choose **Permissions / Grant Access**, and grant **Workload Identity User** (`roles/iam.workloadIdentityUser`) to this principal:

   ```text
   principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/attribute.repository/OWNER/REPOSITORY
   ```

   Replace `PROJECT_NUMBER` with the numeric project number (not the project ID) and `OWNER/REPOSITORY` with the exact GitHub repository. You can find the project number on **Home → Dashboard** or the project details page.

9. Copy the provider's full resource name. It has this form and becomes `GCP_WIF_PROVIDER`:

   ```text
   projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/providers/github
   ```

### 7. Add GitHub Actions repository variables

In GitHub, open the repository and go to **Settings → Secrets and variables → Actions → Variables → New repository variable**. Add these five variables:

| Variable name | Value |
| --- | --- |
| `GCP_PROJECT_ID` | The Google Cloud project ID |
| `GCP_REGION` | The chosen region, e.g. `us-central1` |
| `GCP_WIF_PROVIDER` | The full provider resource name from step 6 |
| `GCP_DEPLOYER_SERVICE_ACCOUNT` | Deployer service account email, e.g. `github-deployer@PROJECT_ID.iam.gserviceaccount.com` |
| `GCP_RUNTIME_SERVICE_ACCOUNT` | Runtime service account email, e.g. `production-ai-runtime@PROJECT_ID.iam.gserviceaccount.com` |

These values are identifiers, not passwords. Do not add a service-account key or Vertex AI key; this workflow uses WIF and the Cloud Run runtime identity.

### 8. Run the deployment

The workflow runs automatically when you push to `main`. You can also open the repository's **Actions** tab, select **Deploy Backend to GCP**, choose **Run workflow**, select `main`, and start it.

A successful run should show the image being pushed and Cloud Run being deployed. The service name is `production-ai-api-public`.

### 9. Grant yourself access and test Swagger

After deployment, open **Cloud Run → Services → production-ai-api-public → Permissions**. Grant your Google account the **Cloud Run Invoker** role (`roles/run.invoker`). If `allUsers` is listed with that role from an earlier public deployment, remove that grant. Do not grant `allUsers` access again.

For the Console-only path, use the service's **Permissions** panel to grant your own Google account. For the CLI path, after `gcloud auth login`, set `$CALLER` to the account shown by `gcloud config get-value account`, then run:

```powershell
$CALLER = gcloud config get-value account

gcloud run services add-iam-policy-binding production-ai-api-public `
  --project $PROJECT_ID `
  --region $REGION `
  --member "user:$CALLER" `
  --role "roles/run.invoker"
```

If `allUsers` still has the Cloud Run Invoker role from a previous deployment, remove it in the service's **Permissions** panel or run:

```powershell
gcloud run services remove-iam-policy-binding production-ai-api-public `
  --project $PROJECT_ID `
  --region $REGION `
  --member "allUsers" `
  --role "roles/run.invoker"
```

A normal browser request to the Cloud Run URL will not automatically include a Google identity token. To use Swagger, run this command in a terminal where you have authenticated with `gcloud auth login` and have the Invoker role:

```powershell
gcloud run services proxy production-ai-api-public `
  --project $PROJECT_ID `
  --region $REGION `
  --port 8080
```

Keep the proxy running and open [http://localhost:8080/docs](http://localhost:8080/docs). Swagger requests will go through the authenticated local proxy. The health endpoint is `/api/v1/health`.

If the workflow fails, inspect the failed GitHub Actions step and verify variable values, the WIF repository condition, deployer roles, region, billing, and enabled APIs.

## Setup with Google Cloud CLI (PowerShell)

Run these commands in Windows PowerShell after installing the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install). Replace the values in the first block. The account used by `gcloud` must have permissions to enable APIs, create IAM resources, and grant project roles. Never paste credentials or service-account keys into this script.

### 1. Sign in and choose project values

```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

$PROJECT_ID = "YOUR_PROJECT_ID"
$REGION = "us-central1"
$GITHUB_REPOSITORY = "OWNER/REPOSITORY"
$POOL_ID = "github-actions"
$PROVIDER_ID = "github"
$DEPLOYER_SA_ID = "github-deployer"
$RUNTIME_SA_ID = "production-ai-runtime"
```

Use the project ID for both `gcloud config set project` and `$PROJECT_ID`. If you need to create a new project, create it in the Console first, select/link billing for it, then continue.

### 2. Enable APIs and create the image repository

```powershell
gcloud services enable run.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com iam.googleapis.com iamcredentials.googleapis.com sts.googleapis.com --project $PROJECT_ID

gcloud artifacts repositories create production-ai `
  --project $PROJECT_ID `
  --location $REGION `
  --repository-format docker `
  --description "Docker images for the production AI backend"
```

If the repository already exists in that region, the create command will report that; keep the existing repository and continue.

### 3. Create service accounts and grant their roles

```powershell
gcloud iam service-accounts create $RUNTIME_SA_ID `
  --project $PROJECT_ID `
  --display-name "Production AI Cloud Run runtime"

gcloud iam service-accounts create $DEPLOYER_SA_ID `
  --project $PROJECT_ID `
  --display-name "GitHub Actions deployer"

$RUNTIME_SA = "${RUNTIME_SA_ID}@${PROJECT_ID}.iam.gserviceaccount.com"
$DEPLOYER_SA = "${DEPLOYER_SA_ID}@${PROJECT_ID}.iam.gserviceaccount.com"

# Let the running application call Vertex AI.
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member "serviceAccount:$RUNTIME_SA" `
  --role "roles/aiplatform.user"

# Let GitHub Actions push images and deploy Cloud Run.
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member "serviceAccount:$DEPLOYER_SA" `
  --role "roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member "serviceAccount:$DEPLOYER_SA" `
  --role "roles/run.admin"

# Let the deployer attach the runtime identity to the Cloud Run service.
gcloud iam service-accounts add-iam-policy-binding $RUNTIME_SA `
  --project $PROJECT_ID `
  --member "serviceAccount:$DEPLOYER_SA" `
  --role "roles/iam.serviceAccountUser"
```

If either service account already exists, skip its create command and confirm the email in **IAM & Admin → Service Accounts**.

### 4. Create the Workload Identity Federation pool and provider

```powershell
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"

gcloud iam workload-identity-pools create $POOL_ID `
  --project $PROJECT_ID `
  --location global `
  --display-name "GitHub Actions"

gcloud iam workload-identity-pools providers create-oidc $PROVIDER_ID `
  --project $PROJECT_ID `
  --location global `
  --workload-identity-pool $POOL_ID `
  --display-name "GitHub repository provider" `
  --issuer-uri "https://token.actions.githubusercontent.com" `
  --attribute-mapping "google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref" `
  --attribute-condition "assertion.repository == '$GITHUB_REPOSITORY' && assertion.ref == 'refs/heads/main'"

gcloud iam service-accounts add-iam-policy-binding $DEPLOYER_SA `
  --project $PROJECT_ID `
  --role "roles/iam.workloadIdentityUser" `
  --member "principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_ID/attribute.repository/$GITHUB_REPOSITORY"
```

Save the WIF provider resource name for GitHub:

```powershell
$WIF_PROVIDER = "projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_ID/providers/$PROVIDER_ID"
$WIF_PROVIDER
$DEPLOYER_SA
$RUNTIME_SA
```

The final three commands print the provider path and service account emails needed in the next step.

### 5. Add the GitHub repository variables

In GitHub, open **Settings → Secrets and variables → Actions → Variables** and add:

| Variable name | PowerShell value |
| --- | --- |
| `GCP_PROJECT_ID` | `$PROJECT_ID` |
| `GCP_REGION` | `$REGION` |
| `GCP_WIF_PROVIDER` | `$WIF_PROVIDER` |
| `GCP_DEPLOYER_SERVICE_ACCOUNT` | `$DEPLOYER_SA` |
| `GCP_RUNTIME_SERVICE_ACCOUNT` | `$RUNTIME_SA` |

Copy each variable's printed value into GitHub. Do not include the `$` sign.

### 6. Deploy and verify

Push a commit to `main`, or run **Deploy Backend to GCP** from the GitHub **Actions** tab. When the job succeeds, grant your Google account `roles/run.invoker` if you have not already, then test Swagger through the authenticated proxy at `http://localhost:8080/docs`.

## What the Workflow Sets on Cloud Run

The deployment command sets these application environment variables:

- `GCP_PROJECT_ID`: the selected project ID.
- `VERTEX_AI_LOCATION`: the selected region.

`VERTEX_AI_MODEL` is not explicitly set by the workflow, so the application uses the default in `app/config.py` (`gemini-2.0-flash-001`) unless you change the code or update the deployment configuration.

The API is protected by Cloud Run IAM because the deployment uses `--no-allow-unauthenticated`. Grant `roles/run.invoker` only to intended callers. The Streamlit UI is not deployed by this workflow; it remains local or can be run with Docker Compose, but it is not configured to authenticate to the protected Cloud Run service.
