# GitHub Actions Conversation History
**Date**: December 19, 2025  
**Topic**: Converting Azure DevOps Pipeline to GitHub Actions with Composite Actions & Reusable Workflows

---

## 📋 Conversation Overview

This document captures the complete conversation about setting up GitHub Actions for Docker build and deployment to Azure Container Apps.

---

## 🎯 Initial Request

**Goal**: Convert Azure DevOps (ADO) pipeline to GitHub Actions with:
- Composite actions
- Workflow calls & reusable workflows
- GitHub Actions runners
- Proper triggers (push, manual)
- Azure federated identity authentication

---

## 🏗️ Architecture Created

### Two Parallel Approaches:

#### 1. **Composite Actions Approach** (Local)
- **File**: `.github/workflows/docker-build-deploy.yml`
- **Uses**: 6 local composite actions
- **Benefits**: Modular, easier to test locally
- **Location**: `.github/actions/`

**Composite Actions Created**:
1. `acr-login` - Login to Azure Container Registry
2. `backup-tag` - Backup current image before updating
3. `build-docker-image` - Build Docker image from Dockerfile
4. `push-docker-image` - Push image to ACR
5. `cleanup-old-tags` - Remove old build tags (keep 10 most recent)
6. `update-aca` - Update Azure Container App with new image

#### 2. **Reusable Workflow Approach**
- **Caller**: `.github/workflows/reusable_docker.yml`
- **Workflow**: `.github/workflows/reusable.yml`
- **Benefits**: Centralized, easier for multi-team sharing
- **Uses**: Inline bash scripts

---

## 🔐 Azure Authentication Setup

### Federated Identity (OIDC) - NO Client Secrets
```
Service Principal: e89b8bf2-b8b1-4d73-bf7e-9bb238db0fda
Subject: repo:charan3844/docker:environment:dev
```

### Why Federated Identity?
- ✅ No client secrets stored in GitHub
- ✅ Temporary tokens (1 hour expiry)
- ✅ More secure than Service Principals with secrets
- ✅ Native Azure support (no extra tools needed)

### Role Assignments
- **Contributor**: Full access to subscription (a0d73355-79cc-4a88-8573-58637c79c6fb)
- **AcrPush**: Push/pull to ACR (tlcaimcpacr)

---

## 🔑 GitHub Secrets Configuration

### Environment: `dev`

| Secret | Value |
|--------|-------|
| AZURE_CLIENT_ID | e89b8bf2-b8b1-4d73-bf7e-9bb238db0fda |
| AZURE_TENANT_ID | [Your Tenant ID] |
| AZURE_SUBSCRIPTION_ID | a0d73355-79cc-4a88-8573-58637c79c6fb |
| ACR_NAME | tlcaimcpacr |
| ACR_LOGIN_SERVER | tlcaimcpacr.azurecr.io |
| REPO | mcp |
| ACA_NAME | tlc-ai-mcp-container-app-dev |
| ACA_RG | rg-tlc-ai-dev-eus |

---

## 🛠️ Workflow Triggers

### Automatic Triggers
1. **Push to main** - Automatically runs workflow
2. **Pull Requests** - (Optional, not configured)

### Manual Trigger
- **workflow_dispatch** - "Run workflow" button in GitHub Actions UI
- Allows re-deployment without code changes
- Useful for emergency hotfixes

---

## 🐛 Issues & Solutions

### Issue 1: OIDC Federated Credential Missing
**Error**: Subscription not accessible  
**Solution**: Created federated credential for `repo:charan3844/docker:environment:dev`

### Issue 2: Backup Tag Creating Duplicates
**Error**: Multiple backup tags with same name  
**Solution**: Added `github.run_id` to make each backup unique

### Issue 3: Container App Name Incorrect
**Error**: ACA not found  
**Solution**: Verified correct name: `tlc-ai-mcp-container-app-dev`

### Issue 4: Permissions Error in Reusable Workflow
**Error**: "id-token: write not allowed"  
**Solution**: Moved permissions from reusable workflow to caller workflow

### Issue 5: Environment Not Accessible
**Error**: Secrets not found (client-id and tenant-id missing)  
**Solution**: Added `environment: dev` to reusable workflow job

### Issue 6: Invalid Workflow YAML
**Error**: "environment is not defined in the referenced workflow"  
**Solution**: Moved `environment: dev` from caller to reusable workflow job

### Issue 7: ACR Delete Command Syntax Wrong
**Error**: "unrecognized arguments: --tag"  
**Solution**: Changed from `--repository` and `--tag` to `--image REPO:TAG`

### Issue 8: Manifest Not Found Error
**Error**: "manifest is not found" when deleting already-deleted tag  
**Solution**: Added error handling with `|| echo "Tag already deleted, skipping..."`

---

## 📚 Key Concepts Explained

### Composite Actions vs Reusable Workflows

| Feature | Composite Actions | Reusable Workflows |
|---------|-------------------|-------------------|
| **Definition** | Reusable job steps | Entire workflow logic |
| **File Location** | `.github/actions/` | `.github/workflows/` |
| **Scope** | Single job | Multiple jobs |
| **Usage** | Local or from other repos | From other repos only |
| **Approach** | Modular | Monolithic |

### workflow_dispatch
- Allows manual trigger via GitHub Actions UI
- Perfect for deployments
- Doesn't require code changes
- Shows "Run workflow" button

### environment: dev
- Specifies which GitHub environment to use
- Accesses secrets stored in that environment
- Different secrets for dev/staging/prod
- Restricts access via environment approval rules

### Federated Identity vs Managed Identity
- **Federated**: Works anywhere (GitHub Actions, local, CI/CD)
- **Managed**: Only for Azure-hosted resources (VMs, App Service)

---

## ✅ Workflow Execution Steps

### Both Workflows Do:
1. ✅ Checkout code
2. ✅ Authenticate to Azure (federated identity)
3. ✅ Login to Azure Container Registry
4. ✅ Backup current image tag
5. ✅ Build Docker image with labels
6. ✅ Push image to ACR
7. ✅ Cleanup old build tags (keep 10 most recent)
8. ✅ Update Azure Container App
9. ✅ Display current revisions

---

## 🚀 How to Execute

### Option 1: Automatic (Push Trigger)
```bash
git add .
git commit -m "Your changes"
git push origin main
```
→ Workflow automatically runs

### Option 2: Manual (workflow_dispatch)
1. Go to: https://github.com/charan3844/docker/actions
2. Click workflow name
3. Click "Run workflow" button
4. Select branch
5. Click "Run workflow"

---

## 📁 Repository Structure

```
docker/
├── .github/
│   ├── workflows/
│   │   ├── compositeactions.yml          ← Composite actions approach
│   │   ├── reusable_docker.yml           ← Caller workflow
│   │   └── reusable.yml                  ← Reusable workflow
│   └── actions/
│       ├── acr-login/action.yml
│       ├── backup-tag/action.yml
│       ├── build-docker-image/action.yml
│       ├── push-docker-image/action.yml
│       ├── cleanup-old-tags/action.yml
│       └── update-aca/action.yml
├── MCPAgent/
│   ├── dockerfile
│   └── mcp.py
├── GITHUB_ACTIONS_SETUP.md
├── SETUP_SHARED_ACTIONS_REPO.md
├── MULTI_TEAM_SHARED_ACTIONS.md
└── CONVERSATION_HISTORY.md              ← This file
```

---

## 🎓 Learning Points

### 1. GitHub Actions Best Practices
- Use `workflow_dispatch` for deployments
- Specify `environment` for secrets access
- Use composite actions for modularity
- Add error handling with `||` in scripts

### 2. Azure Authentication
- Federated Identity > Service Principals with secrets
- OIDC tokens are temporary (1 hour)
- No need to rotate credentials
- Subject format: `repo:OWNER/REPO:environment:ENV`

### 3. ACR Management
- Use `--image REPO:TAG` syntax for delete
- Keep only recent build tags
- Backup before updating
- Handle already-deleted manifests gracefully

### 4. YAML Syntax
- Indentation matters (2 spaces in YAML)
- `environment:` at job level accesses secrets
- Permissions can be at workflow or job level
- Reusable workflows can't define their own permissions

---

## 📊 Comparison: Which Approach to Use?

### Use **Composite Actions** When:
- ✅ Building within single repo
- ✅ Want modular, reusable steps
- ✅ Easy to test and debug locally
- ✅ **Current recommendation**: Simple, modular approach

### Use **Reusable Workflows** When:
- ✅ Sharing across multiple repos
- ✅ Entire workflow is complex
- ✅ Want single entry point
- ✅ Building multi-team platform

---

## 🔄 Multi-Team Setup (Future)

For multiple teams (Team A, Team B, Team C):

1. **Shared Repository**: `charan3844/github-actions`
   - Contains all composite actions
   - Single source of truth

2. **Team Repositories**: `charan3844/docker`, `charan3844/api-service`, etc.
   - Reference shared actions: `charan3844/github-actions/.github/actions/*@main`
   - Each team has own secrets in their environment

3. **Benefits**:
   - One update fixes all teams
   - Consistent tooling
   - Easy versioning with tags

---

## 🎉 What We Accomplished

✅ Converted ADO pipeline to GitHub Actions  
✅ Set up federated identity authentication  
✅ Created 6 reusable composite actions  
✅ Implemented both workflow approaches  
✅ Fixed 8+ issues and edge cases  
✅ Documented complete setup  
✅ Ready for multi-team usage  

---

## 📞 Next Steps

### Option 1: Expand Multi-Team
- Create separate `github-actions` repo with shared actions
- Set up Team B and Team C repos
- Each team references shared actions

### Option 2: Add More Environments
- Create `staging` and `production` environments
- Different secrets per environment
- Environment approval rules

### Option 3: Enhancements
- Add notifications (Slack, Teams)
- Add test step before deployment
- Add rollback capability
- Add monitoring/alerting

---

## 🔗 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Azure Login Action](https://github.com/Azure/login)
- [Azure CLI Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/get-started-existing-container-image)
- [Federated Identity Setup](https://docs.microsoft.com/en-us/azure/active-directory/workload-identities/workload-identity-federation)

---

## 📝 Notes

- All code is in `charan3844/docker` GitHub repository
- Federated identity configured and tested
- Both workflow approaches are functional
- Ready for production deployment
- Error handling in place for edge cases

---

**End of Conversation History**  
*Last Updated: December 19, 2025*
