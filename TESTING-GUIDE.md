# Testing Guide - GitHub Actions Methods

This guide will help you test each method systematically, one by one.

## 📋 Pre-requisites

Before testing any method, ensure you have:

- ✅ GitHub repository: `charan3844/docker`
- ✅ Azure subscription with access
- ✅ Azure Container Registry: `tlcaimcpacr.azurecr.io`
- ✅ Azure Container App: `tlc-ai-mcp-container-app-dev`
- ✅ Resource Group: `rg-tlc-ai-dev-eus`

### Required Secrets (Set Once for All Methods)

Go to **Repository → Settings → Secrets and variables → Actions**

Add these secrets:
```
AZURE_CLIENT_ID          = <your-azure-client-id>
AZURE_TENANT_ID          = <your-azure-tenant-id>
AZURE_SUBSCRIPTION_ID    = <your-azure-subscription-id>
```

---

## 🧪 Testing Approach

### ✅ Use Your Existing `docker` Repository
We'll test all methods in your existing `charan3844/docker` repository by copying workflows to the root `.github/` folder one at a time.

**Why this works:**
- GitHub Actions only detects workflows in root `.github/workflows/`
- We'll test each method by temporarily using its workflows
- No need to create multiple repositories
- Easy to switch between methods

### Test Order:
1. ✅ **Method 1**: Composite Actions (Easiest)
2. ✅ **Method 2**: Parent & Child Workflows
3. ✅ **Method 3**: Reusable Workflows
4. ✅ **Method 4**: Multi-Team Setup (Optional - needs separate repos)
5. ✅ **Method 5**: Shared Composite Actions (Optional - needs separate repo)

---

## 1️⃣ Method 1: Composite Actions (Start Here)

**Location:** `Composite Actions/.github/`

### What This Tests
- Local composite actions within the same folder
- 6 actions working together in one workflow
- Building and deploying your MCP Agent

### Steps to Test

**Step 1: Verify Folder Structure**
```
Composite Actions/
├── .github/
│   ├── actions/
│   │   ├── acr-login/action.yml
│   │   ├── backup-tag/action.yml
│   │   ├── build-docker-image/action.yml
│   │   ├── push-docker-image/action.yml
│   │   ├── cleanup-old-tags/action.yml
│   │   └── update-aca/action.yml
│   └── workflows/
│       └── compositeactions.yml
└── MCPAgent/
    ├── dockerfile
    ├── mcp.py
    └── requirements.txt
```

**Step 2: Copy Method 1 Workflows to Root**

GitHub Actions only looks in the root `.github/` folder, so we'll copy there:

```powershell
# Navigate to docker repository root
cd "C:\Users\Saicharan.Devara\OneDrive - Neudesic\Documents\Project\GitHubActions\docker"

# Create root .github folder structure
New-Item -ItemType Directory -Force -Path ".github\workflows"
New-Item -ItemType Directory -Force -Path ".github\actions"

# Copy composite actions to root
Copy-Item -Path "Composite Actions\.github\actions\*" -Destination ".github\actions\" -Recurse -Force

# Copy workflow file
Copy-Item -Path "Composite Actions\.github\workflows\compositeactions.yml" -Destination ".github\workflows\" -Force

# Ensure MCPAgent exists at root (if not already there)
if (!(Test-Path "MCPAgent")) {
    Copy-Item -Path "Composite Actions\MCPAgent" -Destination ".\MCPAgent" -Recurse -Force
}

# Add, commit and push
git add .
git commit -m "Test Method 1: Composite Actions"
git push origin main
```

**Step 3: Trigger Workflow**
- Go to: `https://github.com/charan3844/docker/actions`
- Click on "Build & Deploy Docker Image to ACR and ACA"
- Click "Run workflow" → "Run workflow"

**Step 4: Monitor Execution**
Watch for:
- ✅ Checkout code
- ✅ Azure Login
- ✅ Login to ACR (composite action)
- ✅ Backup existing tag (composite action)
- ✅ Build Docker image (composite action)
- ✅ Push Docker image (composite action)
- ✅ Cleanup old tags (composite action)
- ✅ Update Azure Container App (composite action)

**Expected Result:**
- All steps should be green ✅
- Docker image pushed to ACR
- Container App updated

**Troubleshooting:**
- If Azure login fails: Check your secrets
- If ACR login fails: Verify ACR name
- If build fails: Check MCPAgent/dockerfile exists

---

## 2️⃣ Method 2: Parent & Child Workflows

**Location:** `Parent&Child/.github/`

### What This Tests
- Parent workflow orchestrating child workflows
- Workflow calling other workflows with `workflow_call`
- Passing data between workflows

### Steps to Test

**Step 1: Verify Folder Structure**
```
Parent&Child/
├── .github/
│   └── workflows/
│       ├── main.yml      (Parent)
│       ├── build.yml     (Child)
│       └── deploy.yml    (Child)
└── MCPAgent/
```

**Step 2: Create New Repository**
```bash
cd "Parent&Child"
git init
git add .
git commit -m "Test: Parent & Child Workflows"
git branch -M main
git remote add origin https://github.com/charan3844/parent-child-test.git
git push -u origin main
```

**Step 3: Trigger Parent Workflow**
- Go to: `https://github.com/charan3844/parent-child-test/actions`
- Click on "Docker Build & Deploy - Parent Workflow"
- Click "Run workflow"

**Step 3: Monitor Execution**
Watch for:
- ✅ Parent workflow starts
- ✅ Calls `build.yml` (child)
- ⏳ Waits for build to complete
- ✅ Calls `deploy.yml` (child)
- ✅ Both children complete successfully

**Expected Result:**
- Parent shows 2 jobs: `call-build-workflow` and `call-deploy-workflow`
- Build runs first, then deploy
- All workflows green ✅

**Troubleshooting:**
- If child workflow not found: Ensure all 3 files (main.yml, build.yml, deploy.yml) are in `.github/workflows/`
- If workflows don't run: Check `workflow_call` trigger is set in child workflows

---

## 3️⃣ Method 3: Reusable Workflows

**Location:** `Reusable/.github/`

### What This Tests
- Reusable workflow with `workflow_call`
- Caller workflow invoking reusable workflow
- Similar to calling a function

### Steps to Test

**Step 1: Clear Previous Method & Copy Method 2**

```powershell
# Navigate to docker repository root
cd "C:\Users\Saicharan.Devara\OneDrive - Neudesic\Documents\Project\GitHubActions\docker"

# Clear previous workflows
Remove-Item -Path ".github\workflows\*" -Force
Remove-Item -Path ".github\actions\*" -Recurse -Force

# Copy Parent & Child workflows
Copy-Item -Path "Parent&Child\.github\workflows\*" -Destination ".github\workflows\" -Force

# Ensure MCPAgent exists at root
if (!(Test-Path "MCPAgent")) {
    Copy-Item -Path "Parent&Child\MCPAgent" -Destination ".\MCPAgent" -Recurse -Force
}

# Add, commit and push
git add .
git commit -m "Test Method 2: Parent & Child Workflows"
git push origin main
```

**Step 2: Trigger Parent Workflow**
- Go to: `https://github.com/charan3844/docker
- Click "Run workflow"

**Step 3: Monitor Execution**
Watch for:
- ✅ Caller workflow (`reusable_docker.yml`) starts
- ✅ Calls reusable workflow (`reusable.yml`)
- ✅ Reusable workflow executes all steps
- ✅ Returns control to caller

**Expected Result:**
- Workflow shows job calling reusable workflow
- All steps in reusable workflow execute
- Build and deploy complete

**Troubleshooting:**
- If "workflow not found": Check `uses: ./.github/workflows/reusable.yml` path is correct
- If secrets missing: Ensure `secrets: inherit` is in caller workflow

---

## 4️⃣ Method 4: Multi-Team Setup (Optional - Simulated)

**Location:** `Multi-Team-Setup/Team1-Docker-Build/`, `Team2-Container-Pushing/`, `Team3-Images-Maintenance/`

### What This Tests
- 3 separate teams with independent workflows
- Team 1: Build → Team 2: Deploy → Team 3: Maintain
- Scheduled maintenance workflow

### Option A: Test All in Same Repository (Simulated)

```powershell
# Navigate to docker repository root
cd "C:\Users\Saicharan.Devara\OneDrive - Neudesic\Documents\Project\GitHubActions\docker"

# Clear previous workflows
Remove-Item -Path ".github\workflows\*" -Force
if (Test-Path ".github\actions") {
    Remove-Item -Path ".github\actions\*" -Recurse -Force
}

# Copy all 3 team workflows (to simulate multi-team)
Copy-Item -Path "Multi-Team-Setup\Team1-Docker-Build\.github\workflows\build.yml" -Destination ".github\workflows\team1-build.yml" -Force
Copy-Item -Path "Multi-Team-Setup\Team2-Container-Pushing\.github\workflows\deploy.yml" -Destination ".github\workflows\team2-deploy.yml" -Force
Copy-Item -Path "Multi-Team-Setup\Team3-Images-Maintenance\.github\workflows\maintenance.yml" -Destination ".github\workflows\team3-maintenance.yml" -Force

# Ensure MCPAgent exists at root
if (!(Test-Path "MCPAgent")) {
    Copy-Item -Path "Composite Actions\MCPAgent" -Destination ".\MCPAgent" -Recurse -Force
}

# Add, commit and push
git add .
git commit -m "Test Method 4: Multi-Team Setup (Simulated)"
git push origin main
```

**Testing:**
- Go to: `https://github.com/charan3844/docker/actions`
- You'll see 3 separate workflows:
  - Team 1: Build
  - Team 2: Deploy (requires image tag input)
  - Team 3: Maintenance
- Run them independently to simulate team separation

### Option B: Skip Multi-Team (Real Scenario Needs Separate Repos)

**Note:** True multi-team setup requires separate repositories for each team. You can skip this method for now and test it later when you need actual team separation.

---

## 5️⃣ Method 5: Shared Composite Actions

**Location:** `Shared-Composite-Actions/.github/`

### What This Tests
- Central repository of shared actions
- Other repositories referencing these actions
- External action usage

### Steps to Test

**Step 1: Create Shared Actions Repository**
```bash
cd "Shared-Composite-Actions"
git init
git add .
git commit -m "Shared Composite Actions"
git branch -M main
git remote add origin https://github.com/charan3844/github-actions.git
git push -u origin main
```

**Step 2: Tag the Release**
```bash
git tag v1.0.0
git push origin v1.0.0 (Optional - Advanced)

**Location:** `Shared-Composite-Actions/.github/`

### What This Tests
- Central repository of shared actions
- Testing shared actions locally first
- Understanding external action usage

### Test Shared Actions Locally First

```powershell
# Navigate to docker repository root
cd "C:\Users\Saicharan.Devara\OneDrive - Neudesic\Documents\Project\GitHubActions\docker"

# Clear previous workflows
Remove-Item -Path ".github\workflows\*" -Force
if (Test-Path ".github\actions") {
    Remove-Item -Path ".github\actions\*" -Recurse -Force
}

# Copy shared actions to root (testing locally)
Copy-Item -Path "Shared-Composite-Actions\.github\actions\*" -Destination ".github\actions\" -Recurse -Force

# Create a test workflow for shared actions
$testWorkflow = @"
name: Test Shared Actions Locally

on:
  workflow_dispatch:

permissions:
  contents: read
  id-token: write

env:
  ACR_SERVER: tlcaimcpacr.azurecr.io
  IMAGE_NAME: mcp

jobs:
  test-shared-actions:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: `${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: `${{ secrets.AZURE_TENANT_ID }}
          subscription-id: `${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      # Test shared actions locally
      - name: Login to ACR
        uses: ./.github/actions/acr-login
        with:
          acr-login-server: `${{ env.ACR_SERVER }}
      
      - name: Build Docker Image
        uses: ./.github/actions/build-docker-image
        with:
          dockerfile-path: MCPAgent/dockerfile
          image-name: `${{ env.IMAGE_NAME }}
          image-tag: `${{ github.sha }}
"@

$testWorkflow | Out-File -FilePath ".github\workflows\test-shared-actions.yml" -Encoding utf8

# Add, commit and push
git add .
git commit -m "Test Method 5: Shared Actions (Local)"
git push origin main
```

**Testing:**
- Go to: `https://github.com/charan3844/docker/actions`
- Click "Test Shared Actions Locally"
- Run workflow
- All shared actions should execute successfully

**Note:** For true external shared actions, you would need to:
1. Create a separate `github-actions` repository
2. Push the shared actions there
3. Tag with v1.0.0
4. Reference from other repos using `uses: charan3844/github-actions/.github/actions/action-name@v1.0.0`

**Skip this for now** - You've already tested the same functionality in Method 1!
- ✅ All teams work without blocking each other

### Method 5: Shared Actions
- ✅ Shared repository created
- ✅ Actions properly tagged
- ✅ External repos can reference actions
- ✅ Actions execute correctly

---

## 🔍 Debugging Tips

### View Workflow Logs
1. Go to Actions tab
2. Click on workflow run
3. Click on job name
4. Expand each step to see logs

### Enable Debug Logging
Add these secrets to see detailed logs:
```
ACTIONS_STEP_DEBUG = true
ACTIONS_RUNNER_DEBUG = true
```

### Common Issues

**Issue: Azure Login Fails**
```
Solution: 
1. Verify secrets are set correctly
2. Check service principal has permissions
3. Ensure subscription ID is correct
```

**Issue: Composite Action Not Found**
```
Solution:
1. Ensure actions/checkout@v4 runs first
2. Check path: ./.github/actions/action-name
3. Verify action.yml file exists
```

**Issue: Workflow Call Fails**
```
Solution:
1. Ensure on: workflow_call is set in child
2. Check uses: path is correct
3. Verify secrets: inherit if needed
```

---

## 📊 Testing Checklist

Create this checklist and mark as you test:

```markdown
## Testing Progress

- [ ] Pre-requisites completed
  - [ ] Secrets added to repository
  - [ ] Azure resources verified
  - [ ] Repository access confirmed

- [ ] Method 1: Composite Actions
  - [ ] Repository created
  - [ ] Workflow triggered
  - [ ] All actions executed
  - [ ] Docker image built
  - [ ] Image pushed to ACR

- [ ] Method 2: Parent & Child
  - [ ] Repository created
  - [ ] Parent workflow triggered
  - [ ] Build child executed
  - [ ] Deploy child executed
  - [ ] Workflows chained correctly

- [ ] Method 3: Reusable Workflows
  - [ ] Repository created
  - [ ] Caller workflow triggered
  - [ ] Reusable workflow executed
  - [ ] Function-like behavior confirmed

- [ ] Method 4: Multi-Team
  - [ ] 3 repositories created
  - [ ] Team 1 workflow tested
  - [ ] Team 2 workflow tested
  - [ ] Team 3 workflow tested
  - [ ] Teams work independently

- [ ] Method 5: Shared Actions
  - [ ] Shared repo created
  - [ ] Actions tagged (v1.0.0)
  - [ ] Test repo created
  - [ ] External actions work
  - [ ] Actions execute correctly
```

---

## 🎯 Next Steps After Testing

1. **Choose Your Preferred Method** based on testing results
2. **Implement in Production** using the method that works best
3. **Document Learnings** - what worked, what didn't
4. **Share with Team** - show them which method to use

---

## 🆘 Need Help?

If you encounter issues:
1. Check the specific method's .md file for detailed troubleshooting
2. Review GitHub Actions logs carefully
3. Verify all pre-requisites are met
4. Check Azure portal for resource issues
5. Test with a simple workflow first before complex ones

---

**Good luck with testing! Start with Method 1 (Composite Actions) as it's the simplest. 🚀**
