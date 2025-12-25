# Shared Composite Actions

## 📋 What Are Shared Composite Actions?

**Shared composite actions** are reusable building blocks stored in a **central repository** that multiple projects can reference and use. Instead of duplicating action code, you create it once and share it across all your repositories.

### Key Concepts
- ✅ Created in a dedicated `github-actions` repository
- ✅ Each team/project references them
- ✅ Single source of truth
- ✅ Centralized maintenance

---

## 📂 Folder Structure

### Your Complete Setup

```
docker/
├── MCPAgent/                           (Your MCP Python application)
│   ├── dockerfile                      (Python 3.10.19-slim base)
│   ├── mcp.py                          (MCP server application)
│   └── requirements.txt                (Python dependencies)
│
├── Composite Actions/                  (Local composite actions demo)
│   ├── .github/
│   │   ├── actions/                    (6 composite actions)
│   │   │   ├── acr-login/
│   │   │   ├── build-docker-image/
│   │   │   ├── push-docker-image/
│   │   │   ├── backup-tag/
│   │   │   ├── cleanup-old-tags/
│   │   │   └── update-aca/
│   │   └── workflows/
│   │       └── compositeactions.yml    (Uses local actions)
│   └── MCPAgent/                       (Copy of MCP app)
│
├── Parent&Child/                       (Parent-child demo)
│   ├── .github/
│   │   └── workflows/
│   │       ├── main.yml                (Parent)
│   │       ├── build.yml               (Child)
│   │       └── deploy.yml              (Child)
│   └── MCPAgent/
│
├── Reusable/                           (Reusable workflows demo)
│   ├── .github/
│   │   └── workflows/
│   │       ├── reusable_docker.yml     (Caller)
│   │       └── reusable.yml            (Reusable)
│   └── MCPAgent/
│
└── Shared-Composite-Actions/          (Shared actions for all teams)
    ├── .github/
    │   └── actions/
    │       ├── acr-login/
    │       │   └── action.yml
    │       ├── build-docker-image/
    │       │   └── action.yml
    │       ├── push-docker-image/
    │       │   └── action.yml
    │       ├── backup-tag/
    │       │   └── action.yml
    │       └── cleanup-old-images/
    │           └── action.yml
    └── README.md
```

---

## 🔧 Shared Action Syntax

### Basic Template

```yaml
name: 'Action Name'
description: 'Clear description of what it does'

# Inputs from workflow
inputs:
  input-name:
    description: 'Input description'
    required: true
    default: 'optional-default'

# Outputs from action
outputs:
  output-name:
    description: 'Output description'
    value: ${{ steps.step-id.outputs.output-name }}

# Steps to execute
runs:
  using: 'composite'
  steps:
    - name: Step name
      id: step-id
      shell: bash
      run: |
        echo "Doing something"
        echo "output-name=value" >> $GITHUB_OUTPUT
```

---

## ✅ Your 5 Shared Actions

### Action 1: acr-login/action.yml

```yaml
name: 'ACR Login'
description: 'Login to Azure Container Registry'

inputs:
  acr-login-server:
    description: 'ACR login server (e.g., myacr.azurecr.io)'
    required: true

runs:
  using: 'composite'
  steps:
    - name: Login to ACR
      shell: bash
      run: |
        ACR_NAME=$(echo ${{ inputs.acr-login-server }} | cut -d. -f1)
        az acr login --name $ACR_NAME
        echo "✅ Logged in to ACR"
```

**Usage in Workflow:**
```yaml
- uses: charan3844/github-actions/.github/actions/acr-login@main
  with:
    acr-login-server: tlcaimcpacr.azurecr.io
```

---

### Action 2: build-docker-image/action.yml

```yaml
name: 'Build Docker Image'
description: 'Build Docker image from Dockerfile'

inputs:
  dockerfile-path:
    description: 'Path to Dockerfile'
    required: true
  image-name:
    description: 'Docker image name'
    required: true
  image-tag:
    description: 'Docker image tag'
    required: false
    default: 'latest'

outputs:
  image-full-name:
    description: 'Full image name with tag'
    value: ${{ steps.build.outputs.image-full-name }}

runs:
  using: 'composite'
  steps:
    - name: Build Docker Image
      id: build
      shell: bash
      run: |
        IMAGE_FULL_NAME="${{ inputs.image-name }}:${{ inputs.image-tag }}"
        docker build -f ${{ inputs.dockerfile-path }} -t $IMAGE_FULL_NAME .
        echo "image-full-name=$IMAGE_FULL_NAME" >> $GITHUB_OUTPUT
        echo "✅ Built: $IMAGE_FULL_NAME"
```

**Usage in Workflow:**
```yaml
- uses: charan3844/github-actions/.github/actions/build-docker-image@main
  with:
    dockerfile-path: MCPAgent/dockerfile
    image-name: mcp
    image-tag: ${{ github.sha }}
```

---

### Action 3: push-docker-image/action.yml

```yaml
name: 'Push Docker Image to ACR'
description: 'Push Docker image to Azure Container Registry'

inputs:
  acr-login-server:
    description: 'ACR login server'
    required: true
  image-name:
    description: 'Docker image name'
    required: true
  image-tag:
    description: 'Docker image tag'
    required: false
    default: 'latest'

outputs:
  acr-image-url:
    description: 'Full ACR image URL'
    value: ${{ steps.push.outputs.acr-image-url }}

runs:
  using: 'composite'
  steps:
    - name: Push Image to ACR
      id: push
      shell: bash
      run: |
        ACR_IMAGE_URL="${{ inputs.acr-login-server }}/${{ inputs.image-name }}:${{ inputs.image-tag }}"
        docker tag ${{ inputs.image-name }}:${{ inputs.image-tag }} $ACR_IMAGE_URL
        docker push $ACR_IMAGE_URL
        echo "acr-image-url=$ACR_IMAGE_URL" >> $GITHUB_OUTPUT
        echo "✅ Pushed: $ACR_IMAGE_URL"
```

**Usage in Workflow:**
```yaml
- uses: charan3844/github-actions/.github/actions/push-docker-image@main
  with:
    acr-login-server: tlcaimcpacr.azurecr.io
    image-name: mcp
    image-tag: abc123
```

---

### Action 4: backup-tag/action.yml

```yaml
name: 'Backup Docker Image Tags'
description: 'Backup current Docker image tags from ACR'

inputs:
  acr-login-server:
    description: 'ACR login server'
    required: true
  repo:
    description: 'Repository name in ACR'
    required: true
  backup-location:
    description: 'Backup file location'
    required: false
    default: './acr-backup'

outputs:
  backup-file:
    description: 'Path to backup file'
    value: ${{ steps.backup.outputs.backup-file }}

runs:
  using: 'composite'
  steps:
    - name: Create Backup Directory
      shell: bash
      run: mkdir -p ${{ inputs.backup-location }}
    
    - name: Backup Image Tags
      id: backup
      shell: bash
      run: |
        BACKUP_FILE="${{ inputs.backup-location }}/backup-${{ inputs.repo }}-$(date +%Y%m%d-%H%M%S).json"
        ACR_NAME=$(echo ${{ inputs.acr-login-server }} | cut -d. -f1)
        
        az acr repository show-tags \
          --name $ACR_NAME \
          --repository ${{ inputs.repo }} \
          --output json > $BACKUP_FILE
        
        echo "backup-file=$BACKUP_FILE" >> $GITHUB_OUTPUT
        echo "✅ Backup created: $BACKUP_FILE"
```

**Usage in Workflow:**
```yaml
- uses: charan3844/github-actions/.github/actions/backup-tag@main
  with:
    acr-login-server: tlcaimcpacr.azurecr.io
    repo: mcp
    backup-location: ./backups
```

---

### Action 5: cleanup-old-images/action.yml

```yaml
name: 'Cleanup Old Docker Images'
description: 'Remove old Docker images from ACR based on retention policy'

inputs:
  acr-login-server:
    description: 'ACR login server'
    required: true
  repo:
    description: 'Repository name in ACR'
    required: true
  keep-count:
    description: 'Number of images to keep'
    required: false
    default: '10'
  older-than-days:
    description: 'Delete images older than X days'
    required: false
    default: '30'

runs:
  using: 'composite'
  steps:
    - name: Cleanup Old Images
      shell: bash
      run: |
        ACR_NAME=$(echo ${{ inputs.acr-login-server }} | cut -d. -f1)
        REPO=${{ inputs.repo }}
        
        TAGS=$(az acr repository show-tags \
          --name $ACR_NAME \
          --repository $REPO \
          --orderby time_desc \
          --output tsv)
        
        TAG_COUNT=0
        DELETED_COUNT=0
        
        while IFS= read -r TAG; do
          TAG_COUNT=$((TAG_COUNT + 1))
          
          if [ $TAG_COUNT -gt ${{ inputs.keep-count }} ]; then
            az acr repository delete \
              --name $ACR_NAME \
              --image $REPO:$TAG \
              --yes
            DELETED_COUNT=$((DELETED_COUNT + 1))
            echo "Deleted: $REPO:$TAG"
          fi
        done <<< "$TAGS"
        
        echo "✅ Cleanup completed!"
        echo "Kept: ${{ inputs.keep-count }} images"
        echo "Deleted: $DELETED_COUNT images"
```

**Usage in Workflow:**
```yaml
- uses: charan3844/github-actions/.github/actions/cleanup-old-images@main
  with:
    acr-login-server: tlcaimcpacr.azurecr.io
    repo: mcp
    keep-count: 10
    older-than-days: 30
```

---

## 📝 How to Set Up Shared Actions

### Step 1: Create github-actions Repository

```bash
# On GitHub, create new repo: charan3844/github-actions
git clone https://github.com/charan3844/github-actions.git
cd github-actions

# Create folder structure
mkdir -p .github/actions/acr-login
mkdir -p .github/actions/build-docker-image
mkdir -p .github/actions/push-docker-image
mkdir -p .github/actions/backup-tag
mkdir -p .github/actions/cleanup-old-images
```

### Step 2: Add action.yml Files

Create each `action.yml` in its folder (as shown above)

### Step 3: Commit and Push

```bash
git add .
git commit -m "Add shared composite actions"
git push origin main
```

### Step 4: Tag Release (Optional)

```bash
git tag v1.0.0
git push origin v1.0.0
```

### Step 5: Use in Other Repositories

In your `docker` repository:

```yaml
# Using main branch (latest)
- uses: charan3844/github-actions/.github/actions/acr-login@main

# OR using specific version tag
- uses: charan3844/github-actions/.github/actions/acr-login@v1.0.0
```

---

## 🔄 Reference Methods

### Local Reference (Same Repo)
```yaml
- uses: ./.github/actions/my-action
```

### External Reference (Different Repo)
```yaml
# Using main branch
- uses: owner/repo/.github/actions/my-action@main

# Using version tag
- uses: owner/repo/.github/actions/my-action@v1.0.0

# Using commit SHA
- uses: owner/repo/.github/actions/my-action@abc1234
```

---

## ✅ Example: Complete Workflow Using Shared Actions

```yaml
name: 'Build and Push'

on:
  push:
    branches: [main]

env:
  ACR_SERVER: tlcaimcpacr.azurecr.io
  IMAGE_NAME: mcp

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      # Use shared action 1: ACR Login
      - name: ACR Login
        uses: charan3844/github-actions/.github/actions/acr-login@main
        with:
          acr-login-server: ${{ env.ACR_SERVER }}
      
      # Use shared action 2: Build Image
      - name: Build Docker Image
        uses: charan3844/github-actions/.github/actions/build-docker-image@main
        with:
          dockerfile-path: MCPAgent/dockerfile
          image-name: ${{ env.IMAGE_NAME }}
          image-tag: ${{ github.sha }}
      
      # Use shared action 3: Push Image
      - name: Push to ACR
        uses: charan3844/github-actions/.github/actions/push-docker-image@main
        with:
          acr-login-server: ${{ env.ACR_SERVER }}
          image-name: ${{ env.IMAGE_NAME }}
          image-tag: ${{ github.sha }}
      
      # Use shared action 4: Backup Tags
      - name: Backup Tags
        uses: charan3844/github-actions/.github/actions/backup-tag@main
        with:
          acr-login-server: ${{ env.ACR_SERVER }}
          repo: ${{ env.IMAGE_NAME }}
      
      # Use shared action 5: Cleanup Old Images
      - name: Cleanup Old Images
        uses: charan3844/github-actions/.github/actions/cleanup-old-images@main
        with:
          acr-login-server: ${{ env.ACR_SERVER }}
          repo: ${{ env.IMAGE_NAME }}
          keep-count: 10
          older-than-days: 30
```

---

## ✨ Benefits

✅ **DRY Principle**: Write once, use everywhere
✅ **Consistency**: Same logic across all repos
✅ **Easy Updates**: Fix issues in one place
✅ **Centralized**: All teams reference same actions
✅ **Versioning**: Tag releases for stability
✅ **Reusability**: Share across organization

---

## 🚀 Complete Repository Setup Guide

### Step 1: Create Shared Actions Repository

```bash
# Create new repository on GitHub
# Name: github-actions (or any name you prefer)
# Description: Shared composite actions for all projects
# Visibility: Public or Private (your choice)
```

### Step 2: Clone and Initialize

```bash
# Clone the repository
git clone https://github.com/charan3844/github-actions.git
cd github-actions

# Create folder structure
mkdir -p .github/actions

# Create README
cat > README.md << 'EOF'
# Shared GitHub Actions

This repository contains shared composite actions used across all our projects.

## Available Actions
- `acr-login` - Azure Container Registry authentication
- `build-docker-image` - Build Docker images
- `push-docker-image` - Push images to ACR
- `backup-tag` - Backup ACR image tags
- `cleanup-old-images` - Remove old images from ACR

## Usage
See individual action folders for detailed documentation.
EOF
```

### Step 3: Create Action Structure

```bash
# Create all action folders
mkdir -p .github/actions/acr-login
mkdir -p .github/actions/build-docker-image
mkdir -p .github/actions/push-docker-image
mkdir -p .github/actions/backup-tag
mkdir -p .github/actions/cleanup-old-images
```

### Step 4: Add Action Files

Create `action.yml` in each folder (see examples in main content above)

### Step 5: Add Documentation

Create `README.md` in each action folder:

```markdown
# Action Name

## Description
Brief description

## Inputs
| Name | Description | Required | Default |
|------|-------------|----------|---------|

## Outputs
| Name | Description |
|------|-------------|

## Usage Example
```yaml
- uses: charan3844/github-actions/.github/actions/action-name@v1.0.0
  with:
    input1: value
```
```

### Step 6: Initial Commit

```bash
git add .
git commit -m "Initial commit: Add shared composite actions"
git push origin main
```

### Step 7: Create First Release

```bash
# Create and push tag
git tag -a v1.0.0 -m "Release v1.0.0: Initial release"
git push origin v1.0.0

# Create major version tag (will be updated)
git tag -a v1 -m "Release v1"
git push origin v1
```

---

## 🏷️ Versioning & Tagging Best Practices

### Semantic Versioning

Follow [semver.org](https://semver.org) format: `MAJOR.MINOR.PATCH`

**MAJOR**: Breaking changes
```bash
# Example: Change required inputs, remove outputs
git tag v2.0.0
```

**MINOR**: New features (backward compatible)
```bash
# Example: Add new optional input
git tag v1.1.0
```

**PATCH**: Bug fixes
```bash
# Example: Fix a bug in existing functionality
git tag v1.0.1
```

### Tagging Strategy

```bash
# 1. Create detailed tag
git tag -a v1.2.3 -m "Release v1.2.3

- Added: New input parameter 'timeout'
- Fixed: Error handling for network failures
- Updated: Documentation with examples"

# 2. Push the tag
git push origin v1.2.3

# 3. Update major version pointer (optional)
git tag -f v1
git push -f origin v1
```

### Release Notes Template

```markdown
## v1.2.3 - 2025-12-25

### Added
- New `timeout` input parameter for build action
- Support for custom Docker build args

### Changed
- Improved error messages in ACR login
- Updated dependencies to latest versions

### Fixed
- Fixed race condition in cleanup action
- Resolved issue with tag backup on Windows runners

### Breaking Changes
None

### Migration Guide
No changes required for existing users.

### Upgrade Path
```yaml
# Old (v1.2.2)
- uses: charan3844/github-actions/.github/actions/build@v1.2.2

# New (v1.2.3)
- uses: charan3844/github-actions/.github/actions/build@v1.2.3
  with:
    timeout: 600  # Optional new parameter
```
```

### Version Matrix Support

Document which versions are supported:

```markdown
## Supported Versions

| Version | Supported | End of Life |
|---------|-----------|-------------|
| 2.x     | ✅ Yes    | N/A         |
| 1.x     | ✅ Yes    | 2026-12-31  |
| 0.x     | ❌ No     | 2025-01-01  |
```

---

## 📚 Documentation Standards

### Action README Template

```markdown
# Action Name

[![Version](https://img.shields.io/github/v/tag/charan3844/github-actions)](https://github.com/charan3844/github-actions/tags)
[![License](https://img.shields.io/github/license/charan3844/github-actions)](LICENSE)

## Description
Clear, concise description of what this action does.

## Inputs

| Name | Description | Required | Default | Type |
|------|-------------|----------|---------|------|
| `input-1` | Description of input 1 | Yes | - | string |
| `input-2` | Description of input 2 | No | `default` | boolean |

## Outputs

| Name | Description | Type |
|------|-------------|------|
| `output-1` | Description of output | string |

## Usage

### Basic Example
```yaml
- uses: charan3844/github-actions/.github/actions/action-name@v1.0.0
  with:
    input-1: value1
```

### Advanced Example
```yaml
- uses: charan3844/github-actions/.github/actions/action-name@v1.0.0
  id: my-step
  with:
    input-1: value1
    input-2: true

- name: Use output
  run: echo "${{ steps.my-step.outputs.output-1 }}"
```

## Error Handling
Description of common errors and how to resolve them.

## Permissions Required
List any specific permissions needed (if applicable).

## Platform Support
- ✅ Linux (ubuntu-latest)
- ✅ macOS (macos-latest)
- ✅ Windows (windows-latest)

## Changelog
See [CHANGELOG.md](CHANGELOG.md) for version history.

## Contributing
See [CONTRIBUTING.md](../../../CONTRIBUTING.md).

## License
[MIT](../../../LICENSE)
```

### Main Repository README

```markdown
# Shared GitHub Actions

Central repository for reusable composite actions.

## Quick Start

```yaml
- uses: charan3844/github-actions/.github/actions/action-name@v1
  with:
    param: value
```

## Available Actions

### Azure Container Registry
- **[acr-login](./github/actions/acr-login)** - Authenticate with Azure Container Registry
- **[push-docker-image](./github/actions/push-docker-image)** - Push Docker images to ACR

### Docker
- **[build-docker-image](./github/actions/build-docker-image)** - Build Docker images with best practices

### Maintenance
- **[backup-tag](./github/actions/backup-tag)** - Backup ACR image tags
- **[cleanup-old-images](./github/actions/cleanup-old-images)** - Clean up old Docker images

## Versioning

We use [Semantic Versioning](https://semver.org/).

### Recommended Usage
```yaml
# Use major version (recommended)
uses: charan3844/github-actions/.github/actions/build@v1

# Use exact version (most stable)
uses: charan3844/github-actions/.github/actions/build@v1.2.3

# Use commit SHA (most secure)
uses: charan3844/github-actions/.github/actions/build@abc123
```

## Support

- **Issues**: [GitHub Issues](https://github.com/charan3844/github-actions/issues)
- **Discussions**: [GitHub Discussions](https://github.com/charan3844/github-actions/discussions)
- **Docs**: [Wiki](https://github.com/charan3844/github-actions/wiki)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

[MIT](LICENSE)
```

### CHANGELOG.md Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Feature X in development

## [1.2.0] - 2025-12-25

### Added
- New action: `deploy-to-aca`
- Timeout support in build action

### Changed
- Improved error messages
- Updated documentation

### Deprecated
- Old parameter `image-path` (use `dockerfile-path` instead)

### Fixed
- Bug in cleanup action
- Race condition in ACR login

## [1.1.0] - 2025-11-20

### Added
- Initial release of 5 core actions

[Unreleased]: https://github.com/charan3844/github-actions/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/charan3844/github-actions/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/charan3844/github-actions/releases/tag/v1.1.0
```

---

## 🔒 Security & Secrets Management

### Repository-Level Security

**1. Enable Security Features:**
- Repository → Settings → Security
- Enable Dependabot alerts
- Enable code scanning
- Enable secret scanning

**2. Branch Protection:**
```yaml
# Settings → Branches → Add rule
Branch name pattern: main
✅ Require pull request reviews
✅ Require status checks
✅ Require conversation resolution
✅ Include administrators
```

**3. Required Secrets Documentation:**

Create `SECURITY.md`:
```markdown
# Security Policy

## Secrets Required

Actions in this repository may require the following secrets:

### Azure Authentication
- `AZURE_CLIENT_ID` - Azure Service Principal Client ID
- `AZURE_TENANT_ID` - Azure AD Tenant ID
- `AZURE_SUBSCRIPTION_ID` - Azure Subscription ID

### Container Registry
- `ACR_USERNAME` - Azure Container Registry username (optional)
- `ACR_PASSWORD` - Azure Container Registry password (optional)

## Setting Up Secrets

### In Calling Repository
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add required secrets based on which actions you use

### Example Usage
```yaml
jobs:
  build:
    steps:
      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - uses: charan3844/github-actions/.github/actions/acr-login@v1
        with:
          acr-login-server: myacr.azurecr.io
```

## Reporting Vulnerabilities

Please report security vulnerabilities to security@example.com
```

### Secrets in Actions

```yaml
# ✅ CORRECT: Document that secrets must be set up in calling workflow
name: 'ACR Login'
description: 'Login to Azure Container Registry. Requires Azure CLI to be authenticated.'

# Note in README.md:
# Prerequisites:
# - Azure CLI must be authenticated (use azure/login@v1 before this action)
```

### Security Scanning

Add `.github/workflows/security.yml`:
```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

---

## 🔄 Breaking Changes Management

### Communication Strategy

**1. Announce in Advance:**
```markdown
## ⚠️ Breaking Change Coming in v2.0.0

We will be removing the deprecated `image-path` input in v2.0.0 (release date: 2026-01-01).

### What's Changing
The `image-path` input will be removed. Use `dockerfile-path` instead.

### Migration
```yaml
# Old (deprecated)
- uses: charan3844/github-actions/.github/actions/build@v1
  with:
    image-path: Dockerfile

# New (required in v2.0.0)
- uses: charan3844/github-actions/.github/actions/build@v2
  with:
    dockerfile-path: Dockerfile
```

### Timeline
- Now: v1.x supports both (with deprecation warning)
- 2026-01-01: v2.0.0 released, `image-path` removed
- 2026-06-30: v1.x end of life
```

**2. Add Deprecation Warnings:**
```yaml
runs:
  using: 'composite'
  steps:
    - name: Check for deprecated inputs
      shell: bash
      run: |
        if [ -n "${{ inputs.image-path }}" ]; then
          echo "::warning::Input 'image-path' is deprecated and will be removed in v2.0.0"
          echo "::warning::Please use 'dockerfile-path' instead"
          echo "::warning::See: https://github.com/charan3844/github-actions/releases/v2.0.0"
        fi
```

**3. Create Migration Guide:**
```markdown
# Migration Guide: v1.x to v2.0.0

## Breaking Changes

### 1. Renamed Input: `image-path` → `dockerfile-path`

**Before (v1.x):**
```yaml
- uses: charan3844/github-actions/.github/actions/build@v1
  with:
    image-path: Dockerfile
```

**After (v2.0.0):**
```yaml
- uses: charan3844/github-actions/.github/actions/build@v2
  with:
    dockerfile-path: Dockerfile
```

### 2. Removed Output: `image-name`

Use `image-full-name` instead, which includes the tag.

### 3. Changed Default: `image-tag`

Default changed from `latest` to `${{ github.sha }}`

## Upgrade Steps

1. Update all workflows to use v2
2. Replace deprecated inputs
3. Test in non-production environment
4. Deploy to production

## Support

- v1.x: Supported until 2026-06-30
- v2.x: Current stable version
```

---

## 📊 Monitoring Usage

### Add Analytics

```yaml
# In each action, add optional telemetry
runs:
  using: 'composite'
  steps:
    - name: Track usage (optional)
      if: inputs.enable-telemetry == 'true'
      shell: bash
      run: |
        curl -s -X POST https://analytics.example.com/track \
          -H "Content-Type: application/json" \
          -d '{
            "action": "${{ github.action }}",
            "repository": "${{ github.repository }}",
            "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
          }' || true
```

### Usage Statistics Dashboard

Create `.github/workflows/stats.yml`:
```yaml
name: Usage Statistics

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  stats:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Get action usage
        id: stats
        run: |
          # Use GitHub API to find workflows using your actions
          gh api graphql -f query='
          {
            search(query: "uses: charan3844/github-actions", type: CODE, first: 100) {
              repositoryCount
              edges {
                node {
                  ... on Code {
                    repository {
                      nameWithOwner
                    }
                  }
                }
              }
            }
          }' > usage.json
          
          echo "Total repositories using actions: $(jq '.data.search.repositoryCount' usage.json)"
        env:
          GH_TOKEN: ${{ github.token }}
      
      - name: Create report
        run: |
          cat > USAGE_REPORT.md << 'EOF'
          # Usage Report
          
          Generated: $(date)
          
          ## Statistics
          - Total repositories: $(jq '.data.search.repositoryCount' usage.json)
          - Most used action: acr-login
          - Version distribution:
            - v1.x: 45%
            - v2.x: 55%
          EOF
```

### Feedback Collection

Create issue templates:
```yaml
# .github/ISSUE_TEMPLATE/action-feedback.yml
name: Action Feedback
description: Provide feedback on a shared action
labels: [feedback]
body:
  - type: dropdown
    id: action
    attributes:
      label: Which action?
      options:
        - acr-login
        - build-docker-image
        - push-docker-image
        - backup-tag
        - cleanup-old-images
    validations:
      required: true
  
  - type: textarea
    id: feedback
    attributes:
      label: Your feedback
      description: What worked well? What could be improved?
    validations:
      required: true
```

---

## 🎯 Summary

Shared composite actions provide:
- **Centralized repository** of reusable actions
- **Multiple teams** using same actions
- **Easy maintenance** - update once
- **Version control** via Git tags
- **Consistency** across organization
- **DRY principle** in action
- **Comprehensive documentation** for easy adoption
- **Security best practices** built-in
- **Breaking changes management** for smooth migrations
- **Usage monitoring** for continuous improvement

Perfect for organizations with multiple teams doing similar tasks!

---

## 📚 Your Other 3 Setups

### 1. Composite Actions
**Location:** `Composite Actions/.github/workflows/compositeactions.yml`

This workflow demonstrates **using local composite actions** to build and deploy your MCP Docker image:

```yaml
name: Build & Deploy Docker Image to ACR and ACA

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    environment: dev
    permissions:
      contents: read
      id-token: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - name: Login to ACR
        uses: ./.github/actions/acr-login
      
      - name: Backup existing tag
        uses: ./.github/actions/backup-tag
      
      - name: Build Docker image
        uses: ./.github/actions/build-docker-image
      
      - name: Push Docker image
        uses: ./.github/actions/push-docker-image
      
      - name: Cleanup old build tags
        uses: ./.github/actions/cleanup-old-tags
      
      - name: Update Azure Container App
        uses: ./.github/actions/update-aca
```

**Key Feature:** All 6 actions are local (`./.github/actions/`), building your **MCPAgent/dockerfile** and deploying to **tlcaimcpacr.azurecr.io**.

---

### 2. Parent & Child Workflows
**Location:** `Parent&Child/.github/workflows/`

This setup demonstrates **parent-child orchestration**:

**Parent:** `main.yml`
```yaml
name: Docker Build & Deploy - Parent Workflow

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  call-build-workflow:
    uses: ./.github/workflows/build.yml
    secrets: inherit
    permissions:
      contents: read
      id-token: write
  
  call-deploy-workflow:
    needs: call-build-workflow
    uses: ./.github/workflows/deploy.yml
    secrets: inherit
    permissions:
      contents: read
      id-token: write
```

**Child:** `build.yml` - Builds your MCP Docker image  
**Child:** `deploy.yml` - Deploys to ACR and ACA

**Key Feature:** Parent calls `build.yml` → waits → calls `deploy.yml`

---

### 3. Reusable Workflows
**Location:** `Reusable/.github/workflows/`

This setup demonstrates **reusable workflows** (like calling functions):

**Caller:** `reusable_docker.yml`
```yaml
name: Reusable Workflow Build & Deploy Docker Image to ACR and ACA

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  id-token: write

jobs:
  build-and-deploy:
    uses: ./.github/workflows/reusable.yml
    secrets: inherit
```

**Reusable:** `reusable.yml` - Contains the actual build and deploy logic with `on: workflow_call:`

**Key Feature:** `reusable_docker.yml` calls `reusable.yml` as a function, building your **MCPAgent** application.

---

## 🔗 All Work With Your MCP Application

All setups build and deploy your **MCP Agent**:
- **Base Image:** Python 3.10.19-slim
- **Application:** mcp.py (MCP server)
- **Port:** 8000
- **Target:** tlcaimcpacr.azurecr.io/mcp
- **Container App:** tlc-ai-mcp-container-app-dev
- **Resource Group:** rg-tlc-ai-dev-eus

Each folder has its own MCPAgent copy for testing!
