# Multi-Team Setup - Shared Actions Implementation

This folder demonstrates how **3 separate teams** can use the same shared composite actions with different responsibilities.

## 🏢 Three Teams Overview

```
┌──────────────────────────────────────────────────────────────┐
│              SHARED COMPOSITE ACTIONS REPO                   │
│          (github-actions repository - central hub)            │
│  - acr-login, build-docker-image, push-docker-image, etc     │
└──────────────────────────────────────────────────────────────┘
         ▲                    ▲                    ▲
         │                    │                    │
         │                    │                    │
    ┌────┴────┐          ┌────┴────┐          ┌───┴────┐
    │  TEAM 1 │          │  TEAM 2 │          │ TEAM 3 │
    │ BUILD   │          │  PUSH   │          │CLEANUP │
    │         │          │         │          │        │
    └─────────┘          └─────────┘          └────────┘
```

---

## 👥 Team Structure

### **Team 1: Docker Build Team** 🐳
**Responsibility**: Build Docker images

```
Team1-Docker-Build/
├── .github/
│   └── workflows/
│       └── build.yml              ← Builds Docker image
└── README.md
```

**Triggers**: 
- On push to main (when MCPAgent/ changes)
- Manual trigger via `workflow_dispatch`

**Output**: 
- Built Docker image ready for next team

---

### **Team 2: Container Pushing Team** 🚀
**Responsibility**: Push images to ACR & update container app

```
Team2-Container-Pushing/
├── .github/
│   └── workflows/
│       └── deploy.yml             ← Pushes & deploys
└── README.md
```

**Triggers**: 
- After Team 1 completes (`workflow_run`)
- Manual trigger with specific image tag

**Output**: 
- Image in ACR
- Container app updated with new image

---

### **Team 3: Images Maintenance Team** 🧹
**Responsibility**: Backup & cleanup old images

```
Team3-Images-Maintenance/
├── .github/
│   └── workflows/
│       └── maintenance.yml        ← Cleanup & backup
└── README.md
```

**Triggers**: 
- Scheduled weekly (Sunday 2 AM UTC)
- Manual trigger anytime

**Output**: 
- Backup of all image tags
- Old images removed

---

## 🔄 Workflow Sequence

```
TEAM 1: BUILD
├─ Trigger: Push to main
├─ Step 1: Checkout code
├─ Step 2: Build Docker image (from MCPAgent/dockerfile)
├─ Step 3: Test locally
└─ Output: Docker image ready (e.g., mcp:abc123)
           ↓
TEAM 2: PUSH & DEPLOY
├─ Trigger: After Team 1 completes
├─ Step 1: Azure login
├─ Step 2: ACR login
├─ Step 3: Push image to ACR (mcp:abc123 → acr.io/mcp:abc123)
├─ Step 4: Update container app with new image
└─ Output: Container app running new image
           ↓
TEAM 3: CLEANUP (Weekly or Manual)
├─ Trigger: Sunday 2 AM or manual
├─ Step 1: Azure login
├─ Step 2: Backup all current tags
├─ Step 3: Remove images older than 30 days
└─ Output: Clean registry with backups
```

---

## 📂 File Organization

### Team 1: Build

**File**: `Team1-Docker-Build/.github/workflows/build.yml`

```yaml
Key Points:
- Builds from MCPAgent/dockerfile
- Creates image tag from github.sha
- Tests image locally
- Outputs: image-name, image-tag
- No Azure auth needed (just Docker)
```

### Team 2: Push & Deploy

**File**: `Team2-Container-Pushing/.github/workflows/deploy.yml`

```yaml
Key Points:
- Listens for Team 1 completion
- Requires Azure credentials
- Uses shared action: acr-login
- Uses shared action: push-docker-image
- Updates container app
- Verifies deployment
```

### Team 3: Maintenance

**File**: `Team3-Images-Maintenance/.github/workflows/maintenance.yml`

```yaml
Key Points:
- Scheduled: Every Sunday 2 AM
- Uses shared action: backup-tag
- Uses shared action: cleanup-old-images
- Keeps 10 latest images
- Removes images > 30 days old
- Uploads backup as artifact
```

---

## 🔐 Secrets Configuration

Each team needs these secrets configured in their repository settings:

### Team 1 (Build) - No secrets needed!
```
No authentication required for building
Just needs environment variables:
- REGISTRY: tlcaimcpacr.azurecr.io
- IMAGE_NAME: mcp
- DOCKERFILE: MCPAgent/dockerfile
```

### Team 2 (Push & Deploy)
```
Secrets Required:
- AZURE_CLIENT_ID
- AZURE_TENANT_ID
- AZURE_SUBSCRIPTION_ID
```

### Team 3 (Maintenance)
```
Secrets Required:
- AZURE_CLIENT_ID
- AZURE_TENANT_ID
- AZURE_SUBSCRIPTION_ID
```

---

## 📊 Shared Actions Used

| Action | Team 1 | Team 2 | Team 3 |
|--------|--------|--------|--------|
| acr-login | ❌ | ✅ | ✅ |
| build-docker-image | ✅ | ❌ | ❌ |
| push-docker-image | ❌ | ✅ | ❌ |
| backup-tag | ❌ | ❌ | ✅ |
| cleanup-old-images | ❌ | ❌ | ✅ |

---

## 📋 Step-by-Step Implementation

### Step 1: Create Separate Repositories

```bash
# Create Team 1 repo (Docker Build)
git clone https://github.com/charan3844/docker.git
cd docker
mkdir -p Team1-Docker-Build/.github/workflows

# Create Team 2 repo (Container Pushing)
git clone https://github.com/charan3844/container-app-deploy.git
cd container-app-deploy
mkdir -p Team2-Container-Pushing/.github/workflows

# Create Team 3 repo (Image Maintenance)
git clone https://github.com/charan3844/image-maintenance.git
cd image-maintenance
mkdir -p Team3-Images-Maintenance/.github/workflows

# Create shared actions repo
git clone https://github.com/charan3844/github-actions.git
cd github-actions
mkdir -p .github/actions
```

### Step 2: Copy Files

```bash
# Copy Team 1 workflow
cp Multi-Team-Setup/Team1-Docker-Build/.github/workflows/build.yml \
   docker/.github/workflows/build.yml

# Copy Team 2 workflow
cp Multi-Team-Setup/Team2-Container-Pushing/.github/workflows/deploy.yml \
   container-app-deploy/.github/workflows/deploy.yml

# Copy Team 3 workflow
cp Multi-Team-Setup/Team3-Images-Maintenance/.github/workflows/maintenance.yml \
   image-maintenance/.github/workflows/maintenance.yml

# Copy shared actions
cp -r Shared-Composite-Actions/.github/actions/* \
   github-actions/.github/actions/
```

### Step 3: Update Workflow References

In each team's workflow, update the reference to shared actions:

```yaml
# From local reference:
uses: ./Shared-Composite-Actions/.github/actions/acr-login

# To external reference:
uses: charan3844/github-actions/.github/actions/acr-login@main
```

### Step 4: Configure Secrets

For each repository, go to Settings → Secrets and add required secrets.

### Step 5: Test Workflows

1. **Team 1**: Push to main branch to trigger build
2. **Team 2**: Wait for Team 1 to complete, then verify deployment
3. **Team 3**: Manual trigger to test cleanup

---

## ✨ Key Features

### 🔗 Workflow Chaining
- Team 1 → Team 2 automatic handoff via `workflow_run`
- Team 2 can also be triggered manually with specific image tag
- Team 3 runs on schedule or manual

### 🔄 Reusability
- All teams use same composite actions
- Actions located in centralized `github-actions` repo
- Update once, benefit all teams

### 📊 Separation of Concerns
- Team 1: Focuses on building
- Team 2: Focuses on deployment
- Team 3: Focuses on maintenance
- No conflicts or overlap

### 🚀 Scalability
- Easy to add Team 4, 5, 6...
- Each new team uses same shared actions
- No code duplication

---

## 📈 Benefits of This Structure

| Benefit | Your Use Case |
|---------|---------------|
| **Independent Teams** | Each team owns their workflow |
| **No Conflicts** | Teams work in isolation |
| **Shared Logic** | DRY principle - reuse actions |
| **Easy Updates** | Fix issues once in shared repo |
| **Clear Responsibilities** | Each team knows what they do |
| **Audit Trail** | Each team's actions logged separately |
| **Parallel Development** | Teams don't block each other |

---

## 🔍 Monitoring & Troubleshooting

### Check Team 1 Build Status
```bash
gh run list -w build.yml
```

### Check Team 2 Deployment Status
```bash
gh run list -w deploy.yml
```

### Check Team 3 Cleanup Status
```bash
gh run list -w maintenance.yml
```

### View Detailed Logs
```bash
gh run view <run-id> --log
```

---

## 📝 Example: Complete Flow

**Monday 9 AM**: Developer pushes code to main
```
↓ Team 1 builds image: mcp:abc123456
↓ Team 2 pushes to ACR and updates container app
↓ Container app running new version
↓ Old container gracefully shut down
```

**Sunday 2 AM**: Weekly maintenance runs
```
↓ Team 3 backups all current tags
↓ Team 3 removes images older than 30 days
↓ Backup artifact stored for 90 days
```

---

## ✅ Checklist

- [ ] Create 3 separate repositories (docker, deploy, maintenance)
- [ ] Create 1 shared actions repository (github-actions)
- [ ] Copy workflow files to each team's repo
- [ ] Copy composite actions to shared repo
- [ ] Configure Azure secrets for Team 2 & 3
- [ ] Update workflow references from local to external
- [ ] Test Team 1 build workflow
- [ ] Test Team 2 deployment workflow
- [ ] Test Team 3 cleanup workflow
- [ ] Document each team's responsibilities
- [ ] Train teams on their workflows
