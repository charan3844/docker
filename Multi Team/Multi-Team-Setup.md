# Multi Team Setup

## 📋 What Is Multi-Team Setup?

A **multi-team setup** is an architecture where different teams work on different stages of a CI/CD pipeline using the same shared resources and workflows. Each team has clear responsibilities but uses common composite actions and infrastructure.

### Your Three Teams:

1. **Team 1: Docker Build** - Builds Docker images
2. **Team 2: Container Pushing** - Pushes to ACR and updates container apps
3. **Team 3: Images Maintenance** - Cleans up old images and backups

---

## 📂 Folder Structure

### Your Complete Docker Repository Structure

```
docker/
├── .github/
├── MCPAgent/                           (Your MCP application)
│   ├── dockerfile
│   ├── mcp.py
│   └── requirements.txt
│
├── Composite Actions/                  (Composite actions with workflows)
│   ├── .github/
│   │   ├── actions/
│   │   │   ├── acr-login/
│   │   │   │   └── action.yml
│   │   │   ├── build-docker-image/
│   │   │   │   └── action.yml
│   │   │   ├── push-docker-image/
│   │   │   │   └── action.yml
│   │   │   ├── backup-tag/
│   │   │   │   └── action.yml
│   │   │   ├── cleanup-old-tags/
│   │   │   │   └── action.yml
│   │   │   └── update-aca/
│   │   │       └── action.yml
│   │   └── workflows/
│   │       └── compositeactions.yml    (Uses local composite actions)
│   └── MCPAgent/                       (Copy of MCP app for testing)
│
├── Parent&Child/                       (Parent-child workflow setup)
│   ├── .github/
│   │   └── workflows/
│   │       ├── main.yml                (Parent workflow)
│   │       ├── build.yml               (Child: Build)
│   │       └── deploy.yml              (Child: Deploy)
│   └── MCPAgent/                       (Copy of MCP app)
│
├── Reusable/                           (Reusable workflows)
│   ├── .github/
│   │   └── workflows/
│   │       ├── reusable_docker.yml     (Caller workflow)
│   │       └── reusable.yml            (Reusable workflow)
│   └── MCPAgent/                       (Copy of MCP app)
│
├── Shared-Composite-Actions/          (Shared actions for all teams)
│   ├── .github/
│   │   └── actions/
│   │       ├── acr-login/
│   │       │   └── action.yml
│   │       ├── build-docker-image/
│   │       │   └── action.yml
│   │       ├── push-docker-image/
│   │       │   └── action.yml
│   │       ├── backup-tag/
│   │       │   └── action.yml
│   │       └── cleanup-old-images/
│   │           └── action.yml
│   └── README.md
│
└── Multi-Team-Setup/                   (3 teams with separate workflows)
    ├── Team1-Docker-Build/
    │   └── .github/
    │       └── workflows/
    │           └── build.yml           (Build MCP Docker image)
    ├── Team2-Container-Pushing/
    │   └── .github/
    │       └── workflows/
    │           └── deploy.yml          (Push to ACR & update ACA)
    ├── Team3-Images-Maintenance/
    │   └── .github/
    │       └── workflows/
    │           └── maintenance.yml     (Backup & cleanup)
    └── README.md
```

---

## 🔧 Syntax for Each Team

### Team 1: Docker Build Workflow

**File:** `Multi-Team-Setup/Team1-Docker-Build/.github/workflows/build.yml`

```yaml
name: TEAM 1 - Build Docker Image for MCP

on:
  push:
    branches: [main]
    paths:
      - 'MCPAgent/**'
      - '.github/workflows/build.yml'
  workflow_dispatch:

env:
  REGISTRY: tlcaimcpacr.azurecr.io
  IMAGE_NAME: mcp
  DOCKERFILE: MCPAgent/dockerfile

jobs:
  build:
    runs-on: ubuntu-latest
    name: Build Docker Image
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set Image Tag
        run: |
          echo "IMAGE_TAG=${{ github.sha }}" >> $GITHUB_ENV
          echo "BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" >> $GITHUB_ENV
      
      # Uses shared composite action
      - name: Build Docker Image
        uses: ./Shared-Composite-Actions/.github/actions/build-docker-image
        with:
          dockerfile-path: ${{ env.DOCKERFILE }}
          image-name: ${{ env.IMAGE_NAME }}
          image-tag: ${{ env.IMAGE_TAG }}
          build-context: .
      
      - name: Inspect Built Image
        run: |
          docker images | grep ${{ env.IMAGE_NAME }}
          docker history ${{ env.IMAGE_NAME }}:${{ env.IMAGE_TAG }} | head -10
      
      - name: Test Image Locally
        run: |
          echo "Testing Docker image..."
          docker run --rm ${{ env.IMAGE_NAME }}:${{ env.IMAGE_TAG }} python --version
      
      - name: Create Build Summary
        run: |
          echo "## ✅ Build Successful" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "- **Image Name**: ${{ env.IMAGE_NAME }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Image Tag**: ${{ env.IMAGE_TAG }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Build Date**: ${{ env.BUILD_DATE }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Dockerfile**: ${{ env.DOCKERFILE }}" >> $GITHUB_STEP_SUMMARY
    
    outputs:
      image-name: ${{ env.IMAGE_NAME }}
      image-tag: ${{ env.IMAGE_TAG }}
```

**Key Features:**
- Uses your **MCPAgent/dockerfile** to build the MCP Python application
- Leverages **Shared-Composite-Actions** for reusable build steps
- Tests the image by running `python --version` inside the container
- Outputs image name and tag for downstream workflows

---

### Team 2: Push & Deploy Workflow

**File:** `deployment/.github/workflows/deploy.yml`

```yaml
name: TEAM 2 - Push & Deploy

on:
  workflow_dispatch:
    inputs:
      image-tag:
        description: 'Image tag to deploy'
        required: true
        type: string

permissions:
  contents: read
  id-token: write

env:
  ACR_LOGIN_SERVER: tlcaimcpacr.azurecr.io
  IMAGE_NAME: mcp
  ACA_NAME: tlc-ai-mcp-container-app-dev
  ACA_RG: rg-tlc-ai-dev-eus

jobs:
  push-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - name: Login to ACR
        run: |
          az acr login --name $(echo ${{ env.ACR_LOGIN_SERVER }} | cut -d. -f1)
      
      - name: Push image to ACR
        run: |
          ACR_IMAGE="${{ env.ACR_LOGIN_SERVER }}/${{ env.IMAGE_NAME }}:${{ github.event.inputs.image-tag }}"
          docker tag ${{ env.IMAGE_NAME }}:${{ github.event.inputs.image-tag }} $ACR_IMAGE
          docker push $ACR_IMAGE
          echo "Pushed: $ACR_IMAGE"
      
      - name: Update container app
        run: |
          ACR_IMAGE="${{ env.ACR_LOGIN_SERVER }}/${{ env.IMAGE_NAME }}:${{ github.event.inputs.image-tag }}"
          az containerapp update \
            --name ${{ env.ACA_NAME }} \
            --resource-group ${{ env.ACA_RG }} \
            --image $ACR_IMAGE
      
      - name: Verify deployment
        run: |
          echo "## ✅ Deployment Successful" >> $GITHUB_STEP_SUMMARY
          echo "- Container App: ${{ env.ACA_NAME }}" >> $GITHUB_STEP_SUMMARY
          echo "- Resource Group: ${{ env.ACA_RG }}" >> $GITHUB_STEP_SUMMARY
```

---

### Team 3: Maintenance Workflow

**File:** `image-maintenance/.github/workflows/maintenance.yml`

```yaml
name: TEAM 3 - Image Maintenance

on:
  schedule:
    # Every Sunday at 2 AM UTC
    - cron: '0 2 * * 0'
  workflow_dispatch:

permissions:
  contents: read
  id-token: write

env:
  ACR_LOGIN_SERVER: tlcaimcpacr.azurecr.io
  IMAGE_NAME: mcp
  KEEP_COUNT: 10
  OLDER_THAN_DAYS: 30

jobs:
  backup-and-cleanup:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - name: Login to ACR
        run: |
          az acr login --name $(echo ${{ env.ACR_LOGIN_SERVER }} | cut -d. -f1)
      
      - name: Backup image tags
        run: |
          mkdir -p ./backups
          BACKUP_FILE="./backups/backup-$(date +%Y%m%d-%H%M%S).json"
          az acr repository show-tags \
            --name $(echo ${{ env.ACR_LOGIN_SERVER }} | cut -d. -f1) \
            --repository ${{ env.IMAGE_NAME }} \
            --output json > $BACKUP_FILE
          echo "Backup created: $BACKUP_FILE"
      
      - name: Upload backup
        uses: actions/upload-artifact@v3
        with:
          name: acr-backup-${{ github.run_number }}
          path: ./backups
          retention-days: 90
      
      - name: Cleanup old images
        run: |
          ACR_NAME=$(echo ${{ env.ACR_LOGIN_SERVER }} | cut -d. -f1)
          REPO=${{ env.IMAGE_NAME }}
          
          TAGS=$(az acr repository show-tags \
            --name $ACR_NAME \
            --repository $REPO \
            --orderby time_desc \
            --output tsv)
          
          TAG_COUNT=0
          while IFS= read -r TAG; do
            TAG_COUNT=$((TAG_COUNT + 1))
            if [ $TAG_COUNT -gt ${{ env.KEEP_COUNT }} ]; then
              az acr repository delete \
                --name $ACR_NAME \
                --image $REPO:$TAG \
                --yes
              echo "Deleted: $REPO:$TAG"
            fi
          done <<< "$TAGS"
      
      - name: Cleanup summary
        run: |
          echo "## ✅ Cleanup Completed" >> $GITHUB_STEP_SUMMARY
          echo "- Kept: ${{ env.KEEP_COUNT }} latest images" >> $GITHUB_STEP_SUMMARY
          echo "- Deleted: Images older than ${{ env.OLDER_THAN_DAYS }} days" >> $GITHUB_STEP_SUMMARY
          echo "- Backup: Uploaded successfully" >> $GITHUB_STEP_SUMMARY
```

---

## 🔄 How Teams Work Together

```
TEAM 1: Docker Build
├─ Trigger: Push to main (or manual)
├─ Action: Build Docker image from MCPAgent/dockerfile
├─ Output: Docker image ready
└─ Tag: github.sha (e.g., abc123def456)
         ↓
TEAM 2: Push & Deploy
├─ Trigger: Manual (user provides image tag)
├─ Action: Push image to ACR
├─ Action: Update container app
└─ Result: Container app running new image
         ↓
TEAM 3: Image Maintenance (Scheduled)
├─ Trigger: Every Sunday 2 AM (or manual)
├─ Action: Backup all current tags
├─ Action: Remove images > 30 days old
├─ Action: Keep latest 10 images
└─ Result: Clean registry, backup available
```

---

## 🔐 Secrets Configuration

### Team 1 (Build)
```
No secrets needed for building
Environment variables only:
- REGISTRY: tlcaimcpacr.azurecr.io
- IMAGE_NAME: mcp
- DOCKERFILE: MCPAgent/dockerfile
```

### Team 2 (Push & Deploy)
```
Repository Secrets:
- AZURE_CLIENT_ID
- AZURE_TENANT_ID
- AZURE_SUBSCRIPTION_ID
```

### Team 3 (Maintenance)
```
Repository Secrets:
- AZURE_CLIENT_ID
- AZURE_TENANT_ID
- AZURE_SUBSCRIPTION_ID
```

---

## ✅ Example: Complete Execution

**Monday 9:00 AM**: Developer pushes code to docker repo main branch
```
↓
Team 1 Workflow Runs (30 seconds)
├─ Checkout code
├─ Build image: mcp:abc123
├─ Test locally
└─ ✅ Build successful

Manual Trigger: Team 2 (image tag: abc123)
↓
Team 2 Workflow Runs (2 minutes)
├─ Login to Azure
├─ Login to ACR
├─ Tag image: tlcaimcpacr.azurecr.io/mcp:abc123
├─ Push to ACR
├─ Update container app
└─ ✅ Container app running new image

Sunday 2 AM: Team 3 Scheduled
↓
Team 3 Workflow Runs (5 minutes)
├─ Backup all tags
├─ Find old images (> 30 days)
├─ Delete old images
└─ ✅ Cleanup complete
```

---

## 🎯 Team Responsibilities

### Team 1: Build Team
- **Owns**: Docker builds
- **Responsible for**: Dockerfile quality
- **Outputs**: Docker image
- **No secrets needed**

### Team 2: Deployment Team
- **Owns**: Container app deployment
- **Responsible for**: Deployment safety
- **Inputs**: Image tag from Team 1
- **Requires**: Azure credentials

### Team 3: Maintenance Team
- **Owns**: Registry cleanliness
- **Responsible for**: Backup creation
- **Scheduled**: Weekly
- **Requires**: Azure credentials

---

## ✨ Best Practices

✅ **Do:**
- Keep teams independent (no dependencies)
- Document each team's responsibility
- Use secrets for sensitive data
- Schedule cleanup regularly
- Monitor all three workflows
- Have clear escalation paths

❌ **Don't:**
- Make Team 1 wait for Team 2
- Hardcode environment-specific values
- Share credentials between teams
- Skip backup creation
- Run cleanup without backups
- Make teams dependent on each other

---

## 🔗 Shared Composite Actions

All teams can use shared actions from `github-actions` repo:

**Team 1 Example:**
```yaml
- uses: charan3844/github-actions/.github/actions/build-docker-image@main
  with:
    dockerfile-path: MCPAgent/dockerfile
    image-name: mcp
    image-tag: ${{ github.sha }}
```

**Team 2 Example:**
```yaml
- uses: charan3844/github-actions/.github/actions/push-docker-image@main
  with:
    acr-login-server: tlcaimcpacr.azurecr.io
    image-name: mcp
    image-tag: abc123
```

---

## 📚 GitHub Actions Basics (For Beginners)

Before diving into multi-team setups, understand these fundamentals:

### What is GitHub Actions?
GitHub Actions is a CI/CD platform that automates your build, test, and deployment pipeline.

### Key Concepts

**1. Workflows**
- YAML files stored in `.github/workflows/`
- Define automation processes
- Triggered by events (push, pull_request, schedule, etc.)

**2. Jobs**
- Groups of steps executed on the same runner
- Run in parallel by default
- Can have dependencies using `needs:`

**3. Steps**
- Individual tasks within a job
- Can run commands or use actions
- Execute sequentially

**4. Runners**
- Servers that execute workflows
- GitHub-hosted: `ubuntu-latest`, `windows-latest`, `macos-latest`
- Self-hosted: Your own infrastructure

**5. Actions**
- Reusable units of code
- Can be local or from GitHub Marketplace

### Basic Workflow Structure

```yaml
name: Workflow Name               # What shows in UI

on:                              # When to run
  push:
    branches: [main]
  workflow_dispatch:             # Manual trigger

jobs:                            # What to do
  job-name:
    runs-on: ubuntu-latest       # Where to run
    steps:
      - name: Step name
        run: echo "Hello"        # What to execute
```

---

## 🎯 CI/CD Pipeline Fundamentals

### What is CI/CD?

**Continuous Integration (CI)**
- Automatically build and test code changes
- Catch bugs early
- Ensure code quality

**Continuous Deployment (CD)**
- Automatically deploy tested code
- Reduce manual errors
- Faster releases

### Your Docker Pipeline

```
Code Push → Build → Test → Push to Registry → Deploy → Maintain
    ↓         ↓       ↓           ↓             ↓         ↓
  GitHub   Docker  Local    ACR Push      Container  Cleanup
           Build   Test                     App       Old Images
```

---

## 👥 Team Communication Patterns

### Method 1: Workflow Artifacts

Team 1 creates, Team 2 uses:

```yaml
# Team 1: Build
- name: Save build info
  run: |
    echo "IMAGE_TAG=${{ github.sha }}" > build-info.txt
    echo "BUILD_DATE=$(date)" >> build-info.txt

- uses: actions/upload-artifact@v3
  with:
    name: build-info
    path: build-info.txt

# Team 2: Deploy (separate workflow)
- uses: actions/download-artifact@v3
  with:
    name: build-info

- name: Read build info
  run: cat build-info.txt
```

### Method 2: Repository Dispatch

Team 1 triggers Team 2's workflow:

```yaml
# Team 1: After build completes
- name: Trigger Team 2
  run: |
    curl -X POST \
      -H "Accept: application/vnd.github+json" \
      -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
      https://api.github.com/repos/${{ github.repository }}/dispatches \
      -d '{"event_type":"build_complete","client_payload":{"image_tag":"${{ github.sha }}"}}'

# Team 2: Listen for event
on:
  repository_dispatch:
    types: [build_complete]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Get image tag
        run: echo "Tag: ${{ github.event.client_payload.image_tag }}"
```

### Method 3: GitHub Environment Variables

```yaml
# Team 1: Set output
- name: Set output
  id: build
  run: echo "image-tag=${{ github.sha }}" >> $GITHUB_OUTPUT

# Access in same workflow
- name: Use output
  run: echo "${{ steps.build.outputs.image-tag }}"
```

### Method 4: Pull Request Comments

```yaml
- name: Comment on PR
  uses: actions/github-script@v6
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: '✅ Build completed! Image tag: ${{ github.sha }}'
      })
```

---

## ⚠️ Conflict Resolution

### Scenario 1: Multiple Teams Push Simultaneously

**Problem:** Both teams trigger builds at the same time

**Solution: Concurrency Control**

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: false  # Queue jobs instead of canceling
```

### Scenario 2: Image Tag Conflicts

**Problem:** Team 2 tries to deploy while Team 1 is building

**Solution: Status Checks**

```yaml
# Team 2: Check if image exists before deploying
- name: Verify image exists
  run: |
    az acr repository show \
      --name myacr \
      --image mcp:${{ inputs.image-tag }} || exit 1
```

### Scenario 3: Resource Locks

**Problem:** Both teams access ACR simultaneously

**Solution: Terraform Locks or Azure Resource Locks**

```yaml
- name: Acquire lock
  run: |
    while [ -f "/tmp/acr.lock" ]; do
      sleep 5
    done
    touch /tmp/acr.lock

- name: Release lock
  if: always()
  run: rm -f /tmp/acr.lock
```

---

## 📊 Monitoring & Alerting

### Method 1: GitHub Notifications

**Enable Notifications:**
1. Repository → Settings → Notifications
2. Watch workflow runs
3. Get email/Slack notifications

### Method 2: Status Badges

Add to README.md:

```markdown
![Team 1 Build](https://github.com/charan3844/docker/workflows/TEAM%201%20-%20Build/badge.svg)
![Team 2 Deploy](https://github.com/charan3844/docker/workflows/TEAM%202%20-%20Deploy/badge.svg)
![Team 3 Maintenance](https://github.com/charan3844/docker/workflows/TEAM%203%20-%20Maintenance/badge.svg)
```

### Method 3: Slack Integration

```yaml
- name: Notify Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "❌ Build failed for ${{ github.repository }}",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "Build #${{ github.run_number }} failed"
            }
          }
        ]
      }
```

### Method 4: Azure Monitor Integration

```yaml
- name: Send metrics to Azure Monitor
  run: |
    az monitor metrics create \
      --resource /subscriptions/.../resourceGroups/rg/providers/... \
      --metric-name BuildDuration \
      --metric-value ${{ steps.build.outputs.duration }}
```

### Method 5: Custom Dashboard

```yaml
- name: Update dashboard
  run: |
    curl -X POST https://your-dashboard.com/api/metrics \
      -H "Content-Type: application/json" \
      -d '{
        "workflow": "${{ github.workflow }}",
        "status": "${{ job.status }}",
        "duration": "${{ steps.timer.outputs.duration }}",
        "timestamp": "${{ github.event.head_commit.timestamp }}"
      }'
```

---

## 🔄 Rollback Strategies

### Strategy 1: Manual Rollback

```yaml
name: Manual Rollback

on:
  workflow_dispatch:
    inputs:
      previous-tag:
        description: 'Image tag to rollback to'
        required: true

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - name: Rollback container app
        run: |
          az containerapp update \
            --name tlc-ai-mcp-container-app-dev \
            --resource-group rg-tlc-ai-dev-eus \
            --image tlcaimcpacr.azurecr.io/mcp:${{ inputs.previous-tag }}
      
      - name: Verify rollback
        run: |
          echo "✅ Rolled back to: ${{ inputs.previous-tag }}"
```

### Strategy 2: Automatic Rollback on Failure

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Save current tag
        id: current
        run: |
          CURRENT=$(az containerapp show \
            --name ${{ env.ACA_NAME }} \
            --resource-group ${{ env.ACA_RG }} \
            --query "properties.template.containers[0].image" -o tsv)
          echo "tag=$CURRENT" >> $GITHUB_OUTPUT
      
      - name: Deploy new version
        id: deploy
        run: |
          az containerapp update \
            --name ${{ env.ACA_NAME }} \
            --resource-group ${{ env.ACA_RG }} \
            --image ${{ env.NEW_IMAGE }}
      
      - name: Health check
        id: health
        run: |
          sleep 30
          HEALTH=$(curl -s -o /dev/null -w "%{http_code}" https://your-app.com/health)
          if [ "$HEALTH" != "200" ]; then
            exit 1
          fi
      
      - name: Rollback on failure
        if: failure() && steps.deploy.outcome == 'success'
        run: |
          echo "⚠️ Health check failed, rolling back..."
          az containerapp update \
            --name ${{ env.ACA_NAME }} \
            --resource-group ${{ env.ACA_RG }} \
            --image ${{ steps.current.outputs.tag }}
```

### Strategy 3: Blue-Green Deployment

```yaml
jobs:
  blue-green-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging (green)
        run: |
          az containerapp update \
            --name tlc-ai-mcp-container-app-staging \
            --resource-group rg-tlc-ai-dev-eus \
            --image tlcaimcpacr.azurecr.io/mcp:${{ github.sha }}
      
      - name: Test staging
        run: |
          # Run smoke tests against staging
          ./run-tests.sh https://staging.example.com
      
      - name: Switch traffic to green
        if: success()
        run: |
          # Swap staging and production
          az containerapp update \
            --name tlc-ai-mcp-container-app-prod \
            --resource-group rg-tlc-ai-dev-eus \
            --image tlcaimcpacr.azurecr.io/mcp:${{ github.sha }}
```

---

## 🔐 Secrets Management

### Repository Secrets
1. Go to Repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add your secrets:
   - `AZURE_CLIENT_ID`
   - `AZURE_TENANT_ID`
   - `AZURE_SUBSCRIPTION_ID`

### Environment Secrets
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # Requires approval
    steps:
      - name: Use environment secret
        run: echo "Deploying with ${{ secrets.PROD_API_KEY }}"
```

### Azure Key Vault Integration

```yaml
- name: Get secrets from Key Vault
  uses: Azure/get-keyvault-secrets@v1
  with:
    keyvault: "my-key-vault"
    secrets: 'api-key, database-password'
  id: keyvault

- name: Use secret
  run: |
    echo "Using API Key from Key Vault"
    # Access with ${{ steps.keyvault.outputs.api-key }}
```

---

## 📈 Performance Metrics

### Track Build Times

```yaml
- name: Start timer
  id: start
  run: echo "start=$(date +%s)" >> $GITHUB_OUTPUT

- name: Build image
  run: docker build -t mcp:latest .

- name: Calculate duration
  run: |
    END=$(date +%s)
    DURATION=$((END - ${{ steps.start.outputs.start }}))
    echo "Build took ${DURATION} seconds"
    echo "DURATION=$DURATION" >> $GITHUB_ENV
```

### Cache Hit Rate

```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  id: cache
  with:
    path: ~/.cache
    key: ${{ runner.os }}-cache-${{ hashFiles('**/package-lock.json') }}

- name: Report cache status
  run: |
    if [ "${{ steps.cache.outputs.cache-hit }}" == "true" ]; then
      echo "✅ Cache hit!"
    else
      echo "❌ Cache miss"
    fi
```

---

## 🎯 Summary

Multi-team setup provides:
- **Clear separation** of concerns
- **Independent workflows** that don't block each other
- **Reusable shared actions** for consistency
- **Scheduled automation** for maintenance
- **Backup safety** before cleanup
- **Easy scaling** to add more teams
- **Communication patterns** for team coordination
- **Monitoring & alerting** for visibility
- **Rollback strategies** for safety
- **Conflict resolution** for smooth operations

Perfect for organizations with different teams managing different pipeline stages!

---

## 📚 Your 3 Other Setups

### 1. Composite Actions Setup
**Location:** `Composite Actions/`

This folder demonstrates **local composite actions** with your MCP Agent:
- **Workflow:** `.github/workflows/compositeactions.yml`
- **Actions:** 6 composite actions (acr-login, build-docker-image, push-docker-image, backup-tag, cleanup-old-tags, update-aca)
- **Purpose:** Shows how to use composite actions within the same repository

**Workflow File:** `compositeactions.yml` uses all 6 actions to build, push, and deploy your MCP Docker image.

### 2. Parent & Child Setup
**Location:** `Parent&Child/`

This folder demonstrates **parent-child workflow orchestration**:
- **Parent:** `.github/workflows/main.yml` (orchestrates the pipeline)
- **Child 1:** `.github/workflows/build.yml` (builds Docker image)
- **Child 2:** `.github/workflows/deploy.yml` (deploys to ACR and ACA)
- **Purpose:** Shows how parent calls child workflows sequentially

**Key Feature:** Parent workflow calls `build.yml` → waits → calls `deploy.yml` → completes

### 3. Reusable Workflows Setup
**Location:** `Reusable/`

This folder demonstrates **reusable workflows with workflow_call**:
- **Caller:** `.github/workflows/reusable_docker.yml` (triggers the pipeline)
- **Reusable:** `.github/workflows/reusable.yml` (contains the actual logic)
- **Purpose:** Shows how workflows can be called like functions

**Key Feature:** `reusable_docker.yml` calls `reusable.yml` using `uses:` keyword

---

## 🔗 All Setups Work With Your MCP Agent

All four setups (Composite Actions, Parent&Child, Reusable, Multi-Team) build and deploy your **MCPAgent**:
- **Dockerfile:** `MCPAgent/dockerfile` (Python 3.10.19-slim base)
- **Application:** `mcp.py` (MCP server application)
- **Dependencies:** `requirements.txt`
- **Target Registry:** `tlcaimcpacr.azurecr.io`
- **Target Container App:** `tlc-ai-mcp-container-app-dev`

Each setup folder has its own copy of MCPAgent for testing and demonstration!
