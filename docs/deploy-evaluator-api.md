# Evaluator API Deployment

The Quantum Advantage Evaluator FastAPI service is packaged as a container and runs on **Azure Container Apps**. The website at https://wernerrall147.github.io/quantum-grand-challenges/evaluate calls this API.

The current live deployment responds at:

```
https://qgc-eval-api.jollysea-98a0f8cb.eastus.azurecontainerapps.io
```

## Container Image

Built from the repo-root [`Dockerfile`](../Dockerfile). Includes:

- Python 3.11 + FastAPI/uvicorn
- `azure-identity`, `azure-cosmos`, `azure-search-documents`, `openai`, `qsharp`
- **Azure CLI + Bicep**  required by `BicepWorkspaceGenerator.validate_bicep()` for `az bicep build` syntax validation

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET    | `/`                       | Health probe (returns `{"status":"ok"}`) |
| POST   | `/api/evaluate`           | Full evaluation pipeline (Troyer + DiVincenzo + workspace guidance + auto code-gen) |
| POST   | `/api/generate-code`      | Q# code generation + resource estimation |
| POST   | `/api/generate-bicep`     | Bicep workspace template (HPC / AI_ML / QUANTUM) |
| GET    | `/api/algorithms`         | List indexed quantum algorithms |
| GET    | `/api/reference-problems` | List active + archived reference problems |

## Automated Deployment (GitHub Actions)

Workflow: [`.github/workflows/deploy-evaluator-api.yml`](../.github/workflows/deploy-evaluator-api.yml)

### Triggers

- **Manual** via the Actions tab (`workflow_dispatch`)  recommended
- **Auto** on push to `main` when files in `agents/api/`, `agents/orchestrator/`, `agents/classifier/`, `agents/code_generator/`, `knowledge/search/`, or the `Dockerfile` change

### Required GitHub Settings

Configure under **Settings → Environments → `production-api`**:

**Secrets:**

| Name | Value |
|------|-------|
| `AZURE_CLIENT_ID` | Service principal client ID with `AcrPush` + `Container Apps Contributor` |
| `AZURE_CLIENT_SECRET` | Service principal secret |
| `AZURE_TENANT_ID` | Tenant containing the Container App |
| `AZURE_SUBSCRIPTION_ID` | Subscription containing the Container App |

> The current setup uses the `qgc-agent-sp` service principal (`072b655f-cf65-4897-951d-38e4735d1303`) which has Owner on subscription `82cd08af-0dac-4fc5-8a3a-f2ab9e4679c3`. Credentials are mirrored locally in `.azure/prod/.env` (gitignored).

**Variables:**

| Name | Default (override only if different) | Purpose |
|------|---------|---------|
| `ACR_NAME` | `qgcregistry` | Azure Container Registry name (no `.azurecr.io` suffix) |
| `ACR_IMAGE_NAME` | `qgc-evaluator` | Image repository name inside the ACR |
| `CONTAINER_APP_NAME` | `qgc-eval-api` | Container App resource name |
| `CONTAINER_APP_RG` | `qgc-evaluator` | Resource group containing the Container App |

> The workflow uses these defaults if the matching var is unset, so for the existing `qgc-eval-api` deployment in subscription `82cd08af-0dac-4fc5-8a3a-f2ab9e4679c3` (tenant `dc692f3e`) you only need the secrets.

**Federated Identity (alternative  more secure than client secret):**

If you prefer OIDC over a long-lived client secret, swap the workflow's `azure/login@v2` step to pass `client-id` / `tenant-id` / `subscription-id` (no `creds`), add `permissions: id-token: write`, and create a federated credential:

```bash
# In the tenant hosting the Container App:
APP_ID=<your app registration client ID>
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-actions-deploy",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:WernerRall147/quantum-grand-challenges:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

### Pipeline Steps

1. Checkout repo
2. Resolve image tag (manual input or `vYYYYMMDD-<sha>`) and resource names (with sensible defaults)
3. Azure service principal login
4. `az acr build`  build image inside ACR (no local Docker daemon needed)
4. `az acr build`  Build image inside ACR (no local Docker daemon needed)
5. `az containerapp update`  Roll new revision
6. Wait up to 90s for `GET /` to return 200
7. Smoke-test: confirm `/api/generate-bicep` and `bicep_template` are in the OpenAPI spec

## Manual Deployment

If you need to deploy without GitHub Actions (e.g. local hotfix):

```powershell
# 1. Login as the qgc-agent-sp service principal (.azure/prod/.env contains creds)
Get-Content .azure\prod\.env | ForEach-Object {
  if ($_ -match '^([^#=]+)=(.*)$') { Set-Item -Path "env:$($matches[1])" -Value $matches[2] }
}
az login --service-principal -u $env:AZURE_CLIENT_ID -p $env:AZURE_CLIENT_SECRET --tenant $env:AZURE_TENANT_ID
az account set --subscription $env:AZURE_SUBSCRIPTION_ID

# 2. Build in ACR (no local Docker required)
$tag = "v$(Get-Date -Format yyyyMMdd)-$(git rev-parse --short HEAD)"
az acr build --registry qgcregistry --image "qgc-evaluator:$tag" --image qgc-evaluator:latest --file Dockerfile .

# 3. Update the Container App
az containerapp update `
  --name qgc-eval-api `
  --resource-group qgc-evaluator `
  --image "qgcregistry.azurecr.io/qgc-evaluator:$tag"

# 4. Verify
$fqdn = az containerapp show --name qgc-eval-api --resource-group qgc-evaluator `
  --query properties.configuration.ingress.fqdn -o tsv
curl "https://$fqdn/"
curl "https://$fqdn/openapi.json" | Select-String "generate-bicep"
```

## Local Development

To run the API locally without containers:

```powershell
$env:PYTHONUTF8 = "1"
pip install -r agents/api/requirements.txt
uvicorn agents.api.main:app --reload --port 8000
```

To build/run the container locally (requires Docker Desktop running):

```powershell
docker build -t qgc-eval-api:local -f Dockerfile .
docker run --rm -p 8000:8000 qgc-eval-api:local
```

## First-Time Provisioning

If you need to provision the Container App and ACR from scratch in a new subscription:

```powershell
$rg = "qgc-evaluator"
$loc = "eastus"
$acr = "qgcacr"      # must be globally unique
$env = "qgc-aca-env"
$app = "qgc-eval-api"

az group create --name $rg --location $loc
az acr create --resource-group $rg --name $acr --sku Basic --admin-enabled false
az containerapp env create --name $env --resource-group $rg --location $loc

# Build initial image
az acr build --registry $acr --image "qgc-eval-api:initial" --file Dockerfile .

# Create the app with system-assigned identity for ACR pull
az containerapp create `
  --name $app --resource-group $rg --environment $env `
  --image "$acr.azurecr.io/qgc-eval-api:initial" `
  --target-port 8000 --ingress external `
  --system-assigned `
  --min-replicas 0 --max-replicas 3 `
  --cpu 1.0 --memory 2.0Gi

# Grant the identity pull rights on ACR
$principalId = az containerapp show --name $app --resource-group $rg --query identity.principalId -o tsv
$acrId = az acr show --name $acr --query id -o tsv
az role assignment create --assignee $principalId --role "AcrPull" --scope $acrId

# Grant access to Azure OpenAI / Cosmos / AI Search
# (See infrastructure/ for the full Bicep reference)
```

After provisioning, update the website CORS list in [`agents/api/main.py`](../agents/api/main.py) and the API URL fallback in [`website/pages/evaluate.tsx`](../website/pages/evaluate.tsx).

## Troubleshooting

- **Revision fails to activate**: Check `az containerapp logs show --name qgc-eval-api --resource-group qgc-evaluator --tail 100`
- **`/api/evaluate` returns 500 with `Cognitive Services not authorized`**: Container App identity needs `Cognitive Services OpenAI User` role on the qgc-openai resource (RBAC propagation can take 5-15 min)
- **`/api/generate-bicep` returns empty `validation`**: The Azure CLI inside the container failed to install. Check Dockerfile RUN layer; verify the image tag pulled is post-Apr-2026
- **OpenAPI smoke check fails**: The deployed image is older than the `/api/generate-bicep` endpoint addition (Apr 2026). Manually trigger the deploy workflow.
