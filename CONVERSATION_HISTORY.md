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

## ❓ Important Q&A Throughout Conversation

### Q1: What is `charan3844/github-actions/.github/actions/acr-login@main`?

**Explanation**:
```
charan3844/github-actions             ← Repository (owner/repo-name)
/.github/actions/acr-login            ← Path to the specific action
@main                                 ← Branch/tag/commit to use
```

**How It Works**:
- GitHub clones the `charan3844/github-actions` repository
- Navigates to `.github/actions/acr-login/`
- Executes the `action.yml` file from the `main` branch

**Alternative Versions**:
- `@main` - Latest code
- `@v1.0.0` - Specific version tag
- `@abc123` - Specific commit SHA

### Q2: Where Can You Use Shared Actions?

**Answer**: ANY repository you own!

**Examples**:
- `charan3844/docker` - Current repo using shared actions
- `charan3844/api-service` - Another team's repo
- `charan3844/ml-model` - Another team's repo
- `charan3844/web-app` - Any future repo

**Central Location**: `charan3844/github-actions` (stores all composite actions)

**Consumer Repos**: Reference from `github-actions` repo (can use same actions everywhere)

### Q3: Why workflow_dispatch?

**Benefits**:
- ✅ Manual trigger from GitHub Actions UI
- ✅ "Run workflow" button available
- ✅ Deploy without code changes
- ✅ Emergency deployments
- ✅ Retry failed deployments

**Without workflow_dispatch**:
- ❌ Only runs on `git push`
- ❌ Cannot manually trigger
- ❌ Must make dummy commit to redeploy

**Use Case**: If Azure has issue and you need to redeploy, just click button (no code changes needed!)

### Q4: Composite Actions vs Reusable Workflows - When to Use Each?

**Composite Actions**:
- ✅ Small reusable steps (login, build, deploy)
- ✅ Can be used locally or from other repos
- ✅ More modular approach
- ✅ Easier to test
- ✅ **Recommended for**: Simple, focused tasks

**Reusable Workflows**:
- ✅ Entire complex workflow logic
- ✅ Can only be called from other repos
- ✅ Single entry point
- ✅ Can call other composite actions
- ✅ **Recommended for**: Complete pipelines

**Current Setup**:
- Using **Composite Actions** (6 separate actions) ← MODULAR & RECOMMENDED
- Also created **Reusable Workflow** as alternative ← ALL-IN-ONE

### Q5: Federated Identity vs Managed Identity - What's the Difference?

**Federated Identity (OIDC)**:
```
✅ Works ANYWHERE (GitHub Actions, local machine, any CI/CD)
✅ No client secrets stored
✅ Temporary tokens (1 hour expiry)
✅ Automatic token refresh
✅ More secure
✅ No credential rotation needed
✅ Your current setup
```

**Why We Use It**:
- No secrets to steal
- Works in GitHub Actions seamlessly
- Industry standard for CI/CD

**Managed Identity**:
```
✅ Only works on Azure resources (VMs, App Service, Container Apps)
❌ Cannot use from GitHub Actions
❌ Requires Azure-hosted compute
```

**Why NOT Managed Identity**:
- GitHub Actions runs outside Azure
- Can't directly access Azure managed identity
- Would need to store a token anyway
- Federated identity is cleaner

### Q6: How Does Environment Specification Work?

**Problem We Fixed**: 
Environment not accessible in reusable workflow

**Solution**:
```yaml
jobs:
  build-and-deploy:
    environment: dev     ← Specifies which GitHub environment
    runs-on: ubuntu-latest
```

**What It Does**:
- Accesses secrets from `dev` environment
- Can have approval rules per environment
- Different secrets for dev/staging/prod
- Adds security layer

**Example Multiple Environments**:
```yaml
dev:        # Automatic deployment
  secrets:  AZURE_CLIENT_ID, REPO, etc.

staging:    # Requires approval
  secrets:  Same as dev

production: # Requires manual approval + QA sign-off
  secrets:  Same as dev
```

### Q7: Why ACR Delete Command Syntax Changed?

**Original (WRONG)**:
```bash
az acr repository delete \
  --name ACR_NAME \
  --repository REPO \
  --tag TAG
```

**Why It Failed**:
- `--repository` doesn't accept repository name alone
- `--tag` is not a recognized argument
- Correct syntax requires specifying image

**Fixed (CORRECT)**:
```bash
az acr repository delete \
  --name ACR_NAME \
  --image REPO:TAG \
  --yes
```

**With Error Handling**:
```bash
az acr repository delete \
  --name ACR_NAME \
  --image REPO:TAG \
  --yes || echo "Already deleted, skipping..."
```

### Q8: What About Already-Deleted Tags?

**Problem**: 
Manifest not found when trying to delete already-deleted tag

**Root Cause**:
- Multiple tags can point to same image
- Deleting one tag deletes all tags to same manifest
- Subsequent deletes fail because manifest gone

**Solution**:
Add `|| echo "Already deleted"` to handle gracefully

**Result**: 
Workflow continues even if tag already gone ✅

---

## 🔐 Federated Identity Setup Details

### Service Principal Created
```
Display Name: github-actions-sp
App ID: e89b8bf2-b8b1-4d73-bf7e-9bb238db0fda
Object ID: b06b3855-728c-4f00-8eed-443ab653e404
Tenant: [Your Tenant ID]
Subscription: a0d73355-79cc-4a88-8573-58637c79c6fb
```

### Federated Credential Created
```
Subject: repo:charan3844/docker:environment:dev
Audience: api://AzureADTokenExchange
Issuer: https://token.actions.githubusercontent.com
```

**What This Means**:
- Only GitHub Actions from `charan3844/docker` repo can authenticate
- Only when running in `dev` environment
- Using OIDC token from GitHub
- No stored credentials

### Role Assignments
```
1. Contributor
   Scope: Subscription (a0d73355-79cc-4a88-8573-58637c79c6fb)
   Purpose: Full access for deployment

2. AcrPush
   Scope: Container Registry (tlcaimcpacr)
   Purpose: Push/pull Docker images
```

### Why This Is Secure
1. No client secrets stored anywhere
2. Token expires in 1 hour
3. Only works for specific GitHub repo/environment
4. Azure tracks every authentication attempt
5. Can revoke access by deleting federated credential



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

## 📌 Conversation: Workflow File Placement & YAML Location (December 23, 2025)

### Questions Asked:
1. **Should the YML file be under the workflows folder?**
   - ✅ **Yes, it's MANDATORY**
   - GitHub Actions only discovers and executes workflow files in `.github/workflows/`
   - This is the designated directory for GitHub Actions workflows

2. **Is this placement mandatory?**
   - ✅ **Yes, absolutely mandatory**
   - Without the correct location, GitHub won't detect or execute the workflow
   - Files in other locations won't trigger automatically on events

3. **Can I place YAML outside of workflows folder?**
   - ❌ **No, it won't work as a standalone workflow**
   - Files outside `.github/workflows/` won't auto-run
   - **Exception**: You can place reusable workflows or composite actions elsewhere (e.g., `.github/actions/`) but they must be explicitly called from a workflow file in `.github/workflows/`

### What is a Workflow?

A **workflow** is essentially a **pipeline** (similar to Azure DevOps pipelines):
- An automated process triggered by events (push, pull request, schedule, manual trigger, etc.)
- Contains jobs with steps (commands to execute)
- Runs automatically when conditions are met

### Key Scenarios:

| Scenario | Location | Works? | Details |
|----------|----------|--------|---------|
| Auto-run workflow on push | `.github/workflows/` | ✅ Yes | GitHub detects and executes automatically |
| Standalone YAML file | `.github/actions/` or other | ❌ No | Won't auto-run unless called |
| Composite action/reusable workflow | `.github/actions/` | ✅ Yes (if called) | Must be explicitly referenced with `uses:` |
| Local script execution | Outside repo | ✅ Yes | Can run manually, but not via GitHub Actions |

### Summary:
- **Only files in `.github/workflows/` will automatically run as pipelines**
- Other YAML files can exist but must be called explicitly from a workflow
- If you want GitHub to auto-execute your script on events, it **must be in `.github/workflows/`**

---

**End of Conversation History**  
*Last Updated: December 23, 2025*
