# Shared Composite Actions Repository

This folder contains reusable composite actions that can be shared across multiple GitHub repositories.

## 📂 Folder Structure

```
Shared-Composite-Actions/
├── .github/
│   └── actions/
│       ├── acr-login/
│       │   └── action.yml          - Login to Azure Container Registry
│       ├── build-docker-image/
│       │   └── action.yml          - Build Docker image from Dockerfile
│       ├── push-docker-image/
│       │   └── action.yml          - Push Docker image to ACR
│       ├── backup-tag/
│       │   └── action.yml          - Backup image tags from ACR
│       └── cleanup-old-images/
│           └── action.yml          - Cleanup old/unused images
└── README.md
```

## 🎯 Use Cases

### Scenario 1: Use Locally (Same Repository)
If this folder is in your docker repo, use actions like this:

```yaml
# In docker/.github/workflows/build.yml
steps:
  - uses: ./Shared-Composite-Actions/.github/actions/acr-login
    with:
      acr-login-server: myacr.azurecr.io
```

### Scenario 2: Use from External Repository (Recommended)
Create a separate `github-actions` repository and reference it:

```yaml
# In docker/.github/workflows/build.yml
steps:
  - uses: charan3844/github-actions/.github/actions/acr-login@main
    with:
      acr-login-server: myacr.azurecr.io
```

---

## 🔧 Available Composite Actions

### 1. **acr-login** - Login to Azure Container Registry
```yaml
- uses: ./Shared-Composite-Actions/.github/actions/acr-login
  with:
    acr-login-server: 'tlcaimcpacr.azurecr.io'
```

**Inputs:**
- `acr-login-server` (required) - ACR login server URL
- `acr-username` (optional) - ACR username
- `acr-password` (optional) - ACR password

---

### 2. **build-docker-image** - Build Docker Image
```yaml
- uses: ./Shared-Composite-Actions/.github/actions/build-docker-image
  with:
    dockerfile-path: 'MCPAgent/dockerfile'
    image-name: 'mcp'
    image-tag: 'latest'
    build-context: '.'
```

**Inputs:**
- `dockerfile-path` (required) - Path to Dockerfile
- `image-name` (required) - Docker image name
- `image-tag` (optional, default: latest)
- `build-context` (optional, default: .)

**Outputs:**
- `image-full-name` - Full image name with tag

---

### 3. **push-docker-image** - Push to ACR
```yaml
- uses: ./Shared-Composite-Actions/.github/actions/push-docker-image
  with:
    acr-login-server: 'tlcaimcpacr.azurecr.io'
    image-name: 'mcp'
    image-tag: 'v1.0.0'
```

**Inputs:**
- `acr-login-server` (required)
- `image-name` (required)
- `image-tag` (optional, default: latest)

**Outputs:**
- `acr-image-url` - Full ACR image URL

---

### 4. **backup-tag** - Backup Image Tags
```yaml
- uses: ./Shared-Composite-Actions/.github/actions/backup-tag
  with:
    acr-login-server: 'tlcaimcpacr.azurecr.io'
    repo: 'mcp'
    backup-location: './backups'
```

**Inputs:**
- `acr-login-server` (required)
- `repo` (required) - Repository name in ACR
- `backup-location` (optional, default: ./acr-backup)

**Outputs:**
- `backup-file` - Path to backup file

---

### 5. **cleanup-old-images** - Cleanup Old Images
```yaml
- uses: ./Shared-Composite-Actions/.github/actions/cleanup-old-images
  with:
    acr-login-server: 'tlcaimcpacr.azurecr.io'
    repo: 'mcp'
    keep-count: '10'
    older-than-days: '30'
```

**Inputs:**
- `acr-login-server` (required)
- `repo` (required) - Repository name in ACR
- `keep-count` (optional, default: 10)
- `older-than-days` (optional, default: 30)

---

## 📋 Complete Example Workflow

```yaml
name: Build, Push & Cleanup

on:
  push:
    branches: [main]

jobs:
  build-push:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      # Use composite actions
      - uses: ./Shared-Composite-Actions/.github/actions/acr-login
        with:
          acr-login-server: tlcaimcpacr.azurecr.io
      
      - uses: ./Shared-Composite-Actions/.github/actions/build-docker-image
        with:
          dockerfile-path: MCPAgent/dockerfile
          image-name: mcp
          image-tag: ${{ github.sha }}
      
      - uses: ./Shared-Composite-Actions/.github/actions/push-docker-image
        with:
          acr-login-server: tlcaimcpacr.azurecr.io
          image-name: mcp
          image-tag: ${{ github.sha }}
      
      - uses: ./Shared-Composite-Actions/.github/actions/backup-tag
        with:
          acr-login-server: tlcaimcpacr.azurecr.io
          repo: mcp
      
      - uses: ./Shared-Composite-Actions/.github/actions/cleanup-old-images
        with:
          acr-login-server: tlcaimcpacr.azurecr.io
          repo: mcp
          keep-count: 10
          older-than-days: 30
```

---

## 🔄 Versioning (External Repository)

If you move this to external `github-actions` repo:

```bash
# Tag a release
git tag v1.0.0
git push origin v1.0.0

# Use in workflows
- uses: charan3844/github-actions/.github/actions/acr-login@v1.0.0
# OR use main for latest
- uses: charan3844/github-actions/.github/actions/acr-login@main
```

---

## ✅ Benefits

- ✅ DRY (Don't Repeat Yourself) - Write once, use everywhere
- ✅ Consistency - Same logic across all repos
- ✅ Easy Maintenance - Update in one place
- ✅ Reusability - Share across teams
- ✅ Version Control - Track changes via Git

---

## 📝 Notes

- Each action is self-contained and independent
- Use Azure CLI login before running ACR operations
- All actions run in a bash shell
- Actions support both local and external references
