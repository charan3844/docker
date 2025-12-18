# Shared Composite Actions Repository - Multi-Team Setup

This guide shows how to create and use a **shared composite actions repository** across multiple teams/projects.

---

## Architecture Overview

```
charan3844/github-actions (Shared Actions Repo)
├── .github/actions/
│   ├── acr-login/
│   ├── backup-tag/
│   ├── build-docker-image/
│   ├── push-docker-image/
│   ├── cleanup-old-tags/
│   └── update-aca/
└── README.md

TEAM A:
charan3844/docker (uses shared actions)
└── .github/workflows/build.yml

TEAM B:
charan3844/api-service (uses shared actions)
└── .github/workflows/build.yml

TEAM C:
charan3844/ml-model (uses shared actions)
└── .github/workflows/build.yml
```

---

## Step 1: Create Shared Actions Repository

```bash
# Create on GitHub
Repository Name: github-actions
Organization: charan3844
Description: Shared GitHub Actions for Docker deployments

# Clone locally
git clone https://github.com/charan3844/github-actions.git
cd github-actions
```

---

## Step 2: Set Up Shared Actions Structure

Create folder structure:
```
github-actions/
├── .github/
│   └── actions/
│       ├── acr-login/
│       │   └── action.yml
│       ├── backup-tag/
│       │   └── action.yml
│       ├── build-docker-image/
│       │   └── action.yml
│       ├── push-docker-image/
│       │   └── action.yml
│       ├── cleanup-old-tags/
│       │   └── action.yml
│       └── update-aca/
│           └── action.yml
├── README.md
└── VERSION
```

Copy all `action.yml` files from `docker/.github/actions/*` to `github-actions/.github/actions/*`

---

## Step 3: Setup Each Team's Repo

### TEAM A: docker repo

**File:** `docker/.github/workflows/build.yml`

```yaml
name: Build & Deploy (Team A - MCP)

on:
  push:
    branches: [main]

env:
  ACR_NAME: ${{ secrets.ACR_NAME }}
  ACR_LOGIN_SERVER: ${{ secrets.ACR_LOGIN_SERVER }}
  REPO: ${{ secrets.REPO }}
  ACA_NAME: ${{ secrets.ACA_NAME }}
  ACA_RG: ${{ secrets.ACA_RG }}
  AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    environment: dev
    permissions:
      contents: read
      id-token: write

    steps:
      - uses: actions/checkout@v4

      - uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      # Using SHARED composite actions
      - uses: charan3844/github-actions/.github/actions/acr-login@main
      - uses: charan3844/github-actions/.github/actions/backup-tag@main
      - uses: charan3844/github-actions/.github/actions/build-docker-image@main
      - uses: charan3844/github-actions/.github/actions/push-docker-image@main
      - uses: charan3844/github-actions/.github/actions/cleanup-old-tags@main
      - uses: charan3844/github-actions/.github/actions/update-aca@main
```

---

### TEAM B: api-service repo

**File:** `api-service/.github/workflows/build.yml`

```yaml
name: Build & Deploy (Team B - API Service)

on:
  push:
    branches: [main]

env:
  ACR_NAME: ${{ secrets.ACR_NAME }}
  ACR_LOGIN_SERVER: ${{ secrets.ACR_LOGIN_SERVER }}
  REPO: ${{ secrets.REPO }}
  ACA_NAME: ${{ secrets.ACA_NAME }}
  ACA_RG: ${{ secrets.ACA_RG }}
  AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    environment: staging
    permissions:
      contents: read
      id-token: write

    steps:
      - uses: actions/checkout@v4

      - uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      # Using SHARED composite actions
      - uses: charan3844/github-actions/.github/actions/acr-login@main
      - uses: charan3844/github-actions/.github/actions/backup-tag@main
      - uses: charan3844/github-actions/.github/actions/build-docker-image@main
      - uses: charan3844/github-actions/.github/actions/push-docker-image@main
      - uses: charan3844/github-actions/.github/actions/cleanup-old-tags@main
      - uses: charan3844/github-actions/.github/actions/update-aca@main
```

---

### TEAM C: ml-model repo

**File:** `ml-model/.github/workflows/build.yml`

```yaml
name: Build & Deploy (Team C - ML Model)

on:
  push:
    branches: [main]

env:
  ACR_NAME: ${{ secrets.ACR_NAME }}
  ACR_LOGIN_SERVER: ${{ secrets.ACR_LOGIN_SERVER }}
  REPO: ${{ secrets.REPO }}
  ACA_NAME: ${{ secrets.ACA_NAME }}
  ACA_RG: ${{ secrets.ACA_RG }}
  AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    environment: production
    permissions:
      contents: read
      id-token: write

    steps:
      - uses: actions/checkout@v4

      - uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      # Using SHARED composite actions
      - uses: charan3844/github-actions/.github/actions/acr-login@main
      - uses: charan3844/github-actions/.github/actions/backup-tag@main
      - uses: charan3844/github-actions/.github/actions/build-docker-image@main
      - uses: charan3844/github-actions/.github/actions/push-docker-image@main
      - uses: charan3844/github-actions/.github/actions/cleanup-old-tags@main
      - uses: charan3844/github-actions/.github/actions/update-aca@main
```

---

## Step 4: Configure Secrets for Each Team

### TEAM A (docker) - Development
```
Environment: dev

Secrets:
AZURE_CLIENT_ID=e89b8bf2-b8b1-4d73-bf7e-9bb238db0fda
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=a0d73355-79cc-4a88-8573-58637c79c6fb
ACR_NAME=tlcaimcpacr
ACR_LOGIN_SERVER=tlcaimcpacr.azurecr.io
REPO=mcp
ACA_NAME=tlc-ai-mcp-container-app-dev
ACA_RG=rg-tlc-ai-dev-eus
```

### TEAM B (api-service) - Staging
```
Environment: staging

Secrets:
AZURE_CLIENT_ID=different-client-id-for-api
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=a0d73355-79cc-4a88-8573-58637c79c6fb
ACR_NAME=tlcaimcpacr
ACR_LOGIN_SERVER=tlcaimcpacr.azurecr.io
REPO=api-service
ACA_NAME=api-service-staging
ACA_RG=rg-api-staging-eus
```

### TEAM C (ml-model) - Production
```
Environment: production

Secrets:
AZURE_CLIENT_ID=different-client-id-for-ml
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=a0d73355-79cc-4a88-8573-58637c79c6fb
ACR_NAME=tlcaimcpacr
ACR_LOGIN_SERVER=tlcaimcpacr.azurecr.io
REPO=ml-model
ACA_NAME=ml-model-prod
ACA_RG=rg-ml-prod-eus
```

---

## Step 5: Versioning Strategy

### Tag Releases in github-actions repo:

```bash
# v1.0.0 - Initial release
git tag -a v1.0.0 -m "Initial Docker composite actions"
git push origin v1.0.0

# v1.1.0 - Bug fix for backup-tag
git tag -a v1.1.0 -m "Fix: Handle existing backup tags"
git push origin v1.1.0
```

### Reference Versions:

```yaml
# Use specific version
- uses: charan3844/github-actions/.github/actions/acr-login@v1.0.0

# Use latest
- uses: charan3844/github-actions/.github/actions/acr-login@main

# Use branch
- uses: charan3844/github-actions/.github/actions/acr-login@develop
```

---

## Step 6: Benefits of This Approach

```
✅ Single Source of Truth
   ├── All teams use same actions
   ├── Bug fixes benefit everyone
   └── Version control for updates

✅ Consistency
   ├── Same Docker build process
   ├── Same ACR login mechanism
   └── Same backup strategy

✅ Easy Maintenance
   ├── Fix once, used by all
   ├── Update versioned release
   └── Teams choose when to upgrade

✅ Scalability
   ├── Add new teams easily
   ├── Just copy workflow + secrets
   └── No code duplication
```

---

## Repository Structure Summary

```
Organization: charan3844
│
├── github-actions (SHARED - Central)
│   ├── .github/actions/*
│   └── Versioned releases (v1.0.0, v1.1.0, etc.)
│
├── docker (TEAM A)
│   ├── Uses: github-actions@main
│   └── Environment: dev
│
├── api-service (TEAM B)
│   ├── Uses: github-actions@main
│   └── Environment: staging
│
└── ml-model (TEAM C)
    ├── Uses: github-actions@main
    └── Environment: production
```

---

## Deployment Flow

```
TEAM A - docker repo
    ↓ (push to main)
    ↓ (triggers workflow)
    ↓ (uses github-actions@main)
    ↓ (builds & deploys MCP)

TEAM B - api-service repo
    ↓ (push to main)
    ↓ (triggers workflow)
    ↓ (uses github-actions@main)
    ↓ (builds & deploys API)

TEAM C - ml-model repo
    ↓ (push to main)
    ↓ (triggers workflow)
    ↓ (uses github-actions@main)
    ↓ (builds & deploys ML)
```

---

## Maintenance

### Update Shared Actions:
1. Edit in `github-actions` repo
2. Test changes
3. Tag new version: `v1.2.0`
4. Teams update reference: `@v1.2.0`

### Common Changes:
- Docker build optimization
- ACR login method changes
- Cleanup strategy updates
- Azure CLI version updates

All teams benefit automatically when using `@main`, or explicitly when upgrading version!

---

## Quick Start Checklist

- [ ] Create `charan3844/github-actions` repo
- [ ] Copy all `.github/actions/` from docker repo
- [ ] Test with docker repo first
- [ ] Add api-service repo workflow
- [ ] Add ml-model repo workflow
- [ ] Configure secrets for each team
- [ ] Tag first release v1.0.0
- [ ] Document in each repo's README

---

This is the enterprise-grade setup! 🚀
