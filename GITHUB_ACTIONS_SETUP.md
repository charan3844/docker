# GitHub Actions Setup Guide

This GitHub Actions workflow converts the Azure DevOps pipeline for building and deploying Docker images to Azure Container Apps.

## 📁 Workflow Structure

```
.github/
├── workflows/
│   ├── docker-build-deploy.yml          # Main workflow (triggered on push to main)
│   └── reusable-docker-deploy.yml       # Reusable workflow for other repos
└── actions/
    ├── acr-login/action.yml             # Login to Azure Container Registry
    ├── backup-tag/action.yml            # Backup the current latest tag
    ├── build-docker-image/action.yml    # Build Docker image
    ├── push-docker-image/action.yml     # Push image to ACR
    ├── cleanup-old-tags/action.yml      # Clean up old backup tags
    └── update-aca/action.yml            # Update Azure Container App
```

## 🔑 Required Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AZURE_CLIENT_ID` | Azure Service Principal Client ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `AZURE_TENANT_ID` | Azure Tenant ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `AZURE_SUBSCRIPTION_ID` | Azure Subscription ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `ACR_NAME` | Azure Container Registry name (without .azurecr.io) | `myregistry` |
| `ACR_LOGIN_SERVER` | ACR login server URL | `myregistry.azurecr.io` |
| `REPO` | Repository name in ACR | `mcp-agent` |
| `ACA_NAME` | Azure Container App name | `my-container-app` |
| `ACA_RG` | Resource group containing the ACA | `my-resource-group` |

## 🚀 How to Use

### Option 1: Main Workflow (Recommended)
The `docker-build-deploy.yml` workflow:
- **Triggers**: Automatically on push to the `main` branch
- **Uses**: Composite actions for modularity
- **Features**: Each step is separated into reusable composite actions

```yaml
# Automatically triggered when you push to main
git push origin main
```

### Option 2: Reusable Workflow
The `reusable-docker-deploy.yml` can be called from other repositories:

```yaml
# In another repository's workflow file
jobs:
  deploy:
    uses: your-org/docker/.github/workflows/reusable-docker-deploy.yml@main
    secrets:
      AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
      AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      ACR_NAME: ${{ secrets.ACR_NAME }}
      ACR_LOGIN_SERVER: ${{ secrets.ACR_LOGIN_SERVER }}
      REPO: ${{ secrets.REPO }}
      ACA_NAME: ${{ secrets.ACA_NAME }}
      ACA_RG: ${{ secrets.ACA_RG }}
```

## 📋 Workflow Steps

1. **Checkout**: Downloads your repository code
2. **Azure Login**: Authenticates with Azure using OIDC (Federated Identity)
3. **ACR Login**: Logs into Azure Container Registry
4. **Backup Tag**: Creates a backup of the current `latest` tag as `build-{run_id}`
5. **Build Docker Image**: Builds the Docker image from `MCPAgent/dockerfile`
6. **Push Docker Image**: Pushes the image to ACR with `latest` tag
7. **Cleanup Old Tags**: Removes old backup tags, keeping only 10 most recent
8. **Update ACA**: Updates the Azure Container App with the new image

## 🔐 Setting Up Azure OIDC (Federated Identity)

For enhanced security, use federated identity instead of client secrets:

```bash
# Create an application in Azure AD
az ad app create --display-name "github-mcp-deploy"

# Get the application ID and create a service principal
APP_ID=$(az ad app list --display-name "github-mcp-deploy" --query [0].id -o tsv)
az ad sp create --id $APP_ID

# Create a federated credential for your GitHub repository
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-mcp-deploy",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:your-org/docker:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Assign roles to the service principal
OBJECT_ID=$(az ad sp show --id $APP_ID --query id -o tsv)
az role assignment create \
  --assignee $OBJECT_ID \
  --role "Contributor" \
  --scope "/subscriptions/{subscription-id}"
```

## 🛠 Troubleshooting

### Workflow fails at Azure Login
- Verify `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID` are correct
- Ensure the service principal has proper role assignments

### Docker image not pushing to ACR
- Check `ACR_NAME` and `ACR_LOGIN_SERVER` are correct
- Verify service principal has `AcrPush` role

### Azure Container App not updating
- Verify `ACA_NAME` and `ACA_RG` are correct
- Ensure service principal has permissions to update container apps

## 📝 Key Differences from ADO Pipeline

| ADO | GitHub Actions |
|-----|-----------------|
| `$(serviceconnection)` | Azure Login with OIDC |
| Variables group | GitHub Secrets |
| `Build.BuildId` | `${{ github.run_id }}` |
| Multiple tasks | Composite actions |
| - | Reusable workflows |

## 🔄 Extending the Workflow

To use the reusable workflow from another repository:

1. Create a new workflow in your repository
2. Call the reusable workflow:
   ```yaml
   - uses: your-org/docker/.github/workflows/reusable-docker-deploy.yml@main
     secrets: inherit
   ```

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Azure Login Action](https://github.com/Azure/login)
- [Composite Actions](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
