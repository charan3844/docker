# Setup Guide: Composite Actions, Reusable Workflows & Parent-Child Architecture

## 📚 Table of Contents
1. [Composite Actions Setup](#composite-actions-setup)
2. [Reusable Workflows Setup](#reusable-workflows-setup)
3. [Parent-Child Workflow Patterns](#parent-child-workflow-patterns)
4. [Integration Patterns](#integration-patterns)
5. [Real-World Examples](#real-world-examples)
6. [Best Practices](#best-practices)

---

## 🏗️ Part 1: Composite Actions Setup

### What is a Composite Action?

A **composite action** is a reusable bundle of steps packaged in a single action file. It allows you to group multiple shell commands, other GitHub Actions, or environment setup into a single, reusable unit.

**When to Use:**
- ✅ Reusing step sequences within a job
- ✅ Creating modular, testable components
- ✅ DRY (Don't Repeat Yourself) principles
- ✅ Single job, same runner context
- ❌ Not for multi-job orchestration
- ❌ Not for environment-specific approvals
- ❌ Not for cross-repo standardization

---

### Step 1: Create Composite Action Directory Structure

```bash
# Navigate to your repo
cd your-repo

# Create composite action directory
mkdir -p .github/actions/my-action-name

# Create action metadata file
touch .github/actions/my-action-name/action.yml
```

**Expected Structure:**
```
.github/
└── actions/
    └── my-action-name/
        ├── action.yml              # Metadata & steps definition
        └── optional-scripts/       # Optional helper scripts
            ├── script.sh
            └── setup.py
```

---

### Step 2: Define Composite Action Metadata

**Basic Template (action.yml):**
```yaml
name: My Composite Action
description: A brief description of what this action does
author: Your Name

# INPUTS - Parameters the action accepts (optional)
inputs:
  my-parameter:
    description: Description of the input
    required: true
    default: 'default-value'
  
  optional-param:
    description: Optional parameter
    required: false
    default: 'some-value'

# OUTPUTS - Values the action returns (optional)
outputs:
  my-output:
    description: Description of what this output contains
    value: ${{ steps.step-id.outputs.output-name }}

# RUNS - How the action executes
runs:
  using: composite
  steps:
    - name: Step 1 - Setup
      shell: bash
      run: |
        echo "Setting up..."
        # Your commands here
    
    - name: Step 2 - Do Work
      id: work-step          # id allows other steps to reference this
      shell: bash
      run: |
        echo "Doing work..."
        echo "result=success" >> $GITHUB_OUTPUT
    
    - name: Step 3 - Cleanup
      shell: bash
      if: always()           # Run even if previous steps fail
      run: |
        echo "Cleaning up..."
```

---

### Step 3: Real Example - ACR Login Composite Action

**Create: `.github/actions/acr-login/action.yml`**
```yaml
name: Login to Azure Container Registry
description: Authenticates with Azure Container Registry and retrieves login server

inputs:
  acr-name:
    description: Name of the Azure Container Registry
    required: false
    default: ${{ env.ACR_NAME }}

outputs:
  login-server:
    description: The ACR login server URL
    value: ${{ steps.get-login-server.outputs.server }}

runs:
  using: composite
  steps:
    - name: Login to ACR
      shell: bash
      run: |
        ACR_NAME="${{ inputs.acr-name }}"
        if [ -z "$ACR_NAME" ]; then
          echo "Error: ACR_NAME not provided"
          exit 1
        fi
        az acr login --name "$ACR_NAME"
        echo "ACR login successful"
    
    - name: Get Login Server
      id: get-login-server
      shell: bash
      run: |
        LOGIN_SERVER=$(az acr show \
          --name ${{ inputs.acr-name }} \
          --query "loginServer" \
          -o tsv)
        echo "server=$LOGIN_SERVER" >> $GITHUB_OUTPUT
        echo "ACR_LOGIN_SERVER=$LOGIN_SERVER" >> $GITHUB_ENV
```

**Usage in Workflow:**
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      # Use composite action
      - name: Login to ACR
        uses: ./.github/actions/acr-login
        with:
          acr-name: myregistry
      
      # Use output from composite action
      - name: Use ACR Output
        run: |
          echo "Login server: ${{ steps.acr-login.outputs.login-server }}"
```

---

### Step 4: Composite Action with Environment Variables

**Create: `.github/actions/build-docker-image/action.yml`**
```yaml
name: Build Docker Image
description: Builds Docker image with metadata labels

inputs:
  dockerfile-path:
    description: Path to Dockerfile
    required: false
    default: 'Dockerfile'
  
  context:
    description: Docker build context directory
    required: false
    default: '.'
  
  image-name:
    description: Full image name (registry/repo)
    required: true
  
  build-tag:
    description: Tag for the image
    required: false
    default: 'latest'

outputs:
  image-digest:
    description: SHA256 digest of built image
    value: ${{ steps.build.outputs.digest }}

runs:
  using: composite
  steps:
    - name: Build Docker Image
      id: build
      shell: bash
      run: |
        BUILD_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        GIT_SHA="${{ github.sha }}"
        IMAGE_NAME="${{ inputs.image-name }}"
        BUILD_TAG="${{ inputs.build-tag }}"
        
        docker build \
          -f ${{ inputs.dockerfile-path }} \
          --label build_time=$BUILD_TIME \
          --label git_sha=$GIT_SHA \
          --label version=$BUILD_TAG \
          -t $IMAGE_NAME:$BUILD_TAG \
          ${{ inputs.context }}
        
        DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' $IMAGE_NAME:$BUILD_TAG | cut -d'@' -f2)
        echo "digest=$DIGEST" >> $GITHUB_OUTPUT
        echo "Built image: $IMAGE_NAME:$BUILD_TAG"
    
    - name: List Built Images
      shell: bash
      run: docker images | grep "${{ inputs.image-name }}"
```

**Usage:**
```yaml
- name: Build Docker Image
  uses: ./.github/actions/build-docker-image
  with:
    dockerfile-path: MCPAgent/dockerfile
    context: MCPAgent
    image-name: myregistry.azurecr.io/mcp
    build-tag: latest
```

---

### Step 5: Composite Action Best Practices

**✅ DO:**
```yaml
name: Good Composite Action
description: Clear, concise description

inputs:
  param:
    description: Clearly describe what this does
    required: true

runs:
  using: composite
  steps:
    # Use meaningful step names
    - name: Validate inputs
      shell: bash
      run: |
        # Check inputs
        if [ -z "${{ inputs.param }}" ]; then
          echo "Error: param is required" >&2
          exit 1
        fi
    
    # Use step IDs for outputs
    - name: Do work
      id: work
      shell: bash
      run: |
        result=$(some_command)
        echo "result=$result" >> $GITHUB_OUTPUT
    
    # Use if conditions
    - name: Conditional cleanup
      if: always()  # Run even on failure
      shell: bash
      run: cleanup_command
```

**❌ DON'T:**
```yaml
# Bad: No error checking
- name: Just run commands
  shell: bash
  run: |
    command1
    command2
    command3

# Bad: No meaningful step names
- name: Step 1
  shell: bash
  run: echo "doing something"

# Bad: Silent failures
- name: Run script
  shell: bash
  run: script.sh  # If script fails, workflow continues
```

---

## 🔄 Part 2: Reusable Workflows Setup

### What is a Reusable Workflow?

A **reusable workflow** is an entire workflow file that can be called from another workflow. It supports multiple jobs, complex logic, and environment-specific governance.

**When to Use:**
- ✅ Multi-job pipelines
- ✅ Cross-repo standardization
- ✅ Environment approval gates
- ✅ Complex orchestration
- ❌ Not for simple step reuse (use composite actions instead)
- ❌ Not when you need shared runner state

---

### Step 1: Create Reusable Workflow File

**Directory Structure:**
```
.github/
└── workflows/
    ├── main.yml                    # Parent workflow (entry point)
    ├── build.yml                   # Child reusable workflow
    ├── deploy.yml                  # Child reusable workflow
    └── test.yml                    # Child reusable workflow
```

---

### Step 2: Create Child Reusable Workflow

**Create: `.github/workflows/build.yml`**
```yaml
name: Build Docker Image - Reusable

# TRIGGER TYPE - workflow_call means this is reusable
on:
  workflow_call:
    # INPUTS - Parameters passed from parent
    inputs:
      dockerfile-path:
        description: Path to Dockerfile
        type: string
        required: false
        default: 'Dockerfile'
      
      image-name:
        description: Full image name (registry/repo)
        type: string
        required: true
      
      build-context:
        description: Docker build context
        type: string
        required: false
        default: '.'
    
    # SECRETS - Credentials needed
    secrets:
      REGISTRY_USERNAME:
        description: Container registry username
        required: true
      
      REGISTRY_PASSWORD:
        description: Container registry password
        required: true
    
    # OUTPUTS - Values returned to parent workflow
    outputs:
      image-digest:
        description: SHA256 digest of built image
        value: ${{ jobs.build.outputs.digest }}
      
      image-tag:
        description: Tag of built image
        value: ${{ jobs.build.outputs.tag }}

jobs:
  build:
    name: Build Image
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    # Define outputs at job level
    outputs:
      digest: ${{ steps.build.outputs.digest }}
      tag: latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Registry
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
      
      - name: Build and push
        id: build
        uses: docker/build-push-action@v4
        with:
          context: ${{ inputs.build-context }}
          file: ${{ inputs.dockerfile-path }}
          push: true
          tags: ${{ inputs.image-name }}:latest
          labels: |
            git.sha=${{ github.sha }}
            git.ref=${{ github.ref }}
      
      - name: Export image digest
        id: build
        shell: bash
        run: |
          echo "digest=${{ steps.build.outputs.digest }}" >> $GITHUB_OUTPUT
          echo "Built: ${{ inputs.image-name }}"
```

---

### Step 3: Create Parent Workflow

**Create: `.github/workflows/main.yml`**
```yaml
name: CI/CD Pipeline - Parent Workflow

on:
  push:
    branches:
      - main
  workflow_dispatch:

env:
  REGISTRY: myregistry.azurecr.io
  IMAGE_NAME: myapp

jobs:
  # Call build reusable workflow
  build-image:
    name: Build
    uses: ./.github/workflows/build.yml
    with:
      dockerfile-path: Dockerfile
      image-name: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
      build-context: .
    secrets:
      REGISTRY_USERNAME: ${{ secrets.REGISTRY_USERNAME }}
      REGISTRY_PASSWORD: ${{ secrets.REGISTRY_PASSWORD }}
  
  # Call deploy reusable workflow after build completes
  deploy-image:
    name: Deploy
    needs: build-image              # Wait for build to complete
    uses: ./.github/workflows/deploy.yml
    with:
      image-name: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
      image-digest: ${{ needs.build-image.outputs.image-digest }}
      environment: production
    secrets:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

---

### Step 4: Create Deploy Reusable Workflow

**Create: `.github/workflows/deploy.yml`**
```yaml
name: Deploy Docker Image - Reusable

on:
  workflow_call:
    inputs:
      image-name:
        description: Full image name
        type: string
        required: true
      
      image-digest:
        description: Image digest from build
        type: string
        required: true
      
      environment:
        description: Deployment environment
        type: string
        required: true
        default: production
    
    secrets:
      DEPLOY_TOKEN:
        description: Token for deployment
        required: true

jobs:
  deploy:
    name: Deploy to ${{ inputs.environment }}
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}  # Environment protection rules apply
    permissions:
      contents: read
      id-token: write
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Deploy notification
        run: |
          echo "Deploying ${{ inputs.image-name }}@${{ inputs.image-digest }}"
          echo "Environment: ${{ inputs.environment }}"
      
      - name: Deploy application
        run: |
          # Your deployment commands
          echo "Deploying to ${{ inputs.environment }}"
      
      - name: Verify deployment
        run: |
          echo "Verifying deployment..."
          # Health checks, smoke tests, etc.
```

---

## 👨‍👧‍👦 Part 3: Parent-Child Workflow Patterns

### Pattern 1: Sequential Execution

**Use Case:** Build must complete before deploy starts

```yaml
# main.yml
jobs:
  build:
    uses: ./.github/workflows/build.yml
    with:
      image-name: myapp:latest
    secrets: inherit
  
  deploy:
    needs: build                    # Wait for build job
    uses: ./.github/workflows/deploy.yml
    with:
      image-digest: ${{ needs.build.outputs.image-digest }}
    secrets: inherit
  
  test:
    needs: deploy                   # Wait for deploy job
    uses: ./.github/workflows/test.yml
    secrets: inherit
```

**Execution Flow:**
```
build (start)
  ↓ (wait)
deploy (start after build completes)
  ↓ (wait)
test (start after deploy completes)
```

---

### Pattern 2: Fan-Out Execution

**Use Case:** Build multiple variants in parallel

```yaml
# main.yml
jobs:
  build-linux:
    uses: ./.github/workflows/build.yml
    with:
      platform: linux
      image-name: myapp:linux
    secrets: inherit
  
  build-windows:
    uses: ./.github/workflows/build.yml
    with:
      platform: windows
      image-name: myapp:windows
    secrets: inherit
  
  build-macos:
    uses: ./.github/workflows/build.yml
    with:
      platform: macos
      image-name: myapp:macos
    secrets: inherit
  
  # All builds complete, then deploy
  deploy:
    needs: [build-linux, build-windows, build-macos]
    uses: ./.github/workflows/deploy.yml
    secrets: inherit
```

**Execution Flow:**
```
build-linux   build-windows   build-macos  (all run in parallel)
       ↓               ↓              ↓
       └───────────────┼──────────────┘
                       ↓
                    deploy (after all builds complete)
```

---

### Pattern 3: Conditional Execution

**Use Case:** Deploy only if tests pass

```yaml
# main.yml
jobs:
  build:
    uses: ./.github/workflows/build.yml
    secrets: inherit
  
  test:
    needs: build
    uses: ./.github/workflows/test.yml
    secrets: inherit
  
  deploy:
    needs: test
    if: success()              # Only run if test passed
    uses: ./.github/workflows/deploy.yml
    secrets: inherit
  
  notify-failure:
    needs: test
    if: failure()              # Only run if test failed
    uses: ./.github/workflows/notify.yml
    secrets: inherit
```

---

### Pattern 4: Environment-Specific Workflows

**Use Case:** Different deployment for different environments

```yaml
# main.yml
jobs:
  build:
    uses: ./.github/workflows/build.yml
    secrets: inherit
  
  deploy-dev:
    needs: build
    uses: ./.github/workflows/deploy.yml
    with:
      environment: dev
    secrets: inherit
  
  deploy-staging:
    needs: deploy-dev
    uses: ./.github/workflows/deploy.yml
    with:
      environment: staging
    secrets: inherit
  
  deploy-prod:
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    uses: ./.github/workflows/deploy.yml
    with:
      environment: production
    secrets: inherit
```

---

## 🔗 Part 4: Integration Patterns - Composite Actions + Reusable Workflows

### Architecture Overview

```
Parent Workflow (main.yml)
└── Reusable Workflow (build.yml)
    └── Job (build-docker)
        └── Composite Actions
            ├── acr-login
            ├── build-docker-image
            └── push-docker-image
```

---

### Pattern: Composite Actions Inside Reusable Workflows

**Create: `.github/workflows/build.yml` (uses composite actions)**
```yaml
name: Build with Composite Actions - Reusable

on:
  workflow_call:
    inputs:
      registry:
        type: string
        required: true
      image-name:
        type: string
        required: true
    
    secrets:
      REGISTRY_TOKEN:
        required: true
    
    outputs:
      image-url:
        value: ${{ jobs.build.outputs.url }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.image.outputs.url }}
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      # Composite Action 1: Registry Login
      - name: Login to Registry
        uses: ./.github/actions/registry-login
        with:
          registry: ${{ inputs.registry }}
          token: ${{ secrets.REGISTRY_TOKEN }}
      
      # Composite Action 2: Build Image
      - name: Build Image
        id: build
        uses: ./.github/actions/build-docker-image
        with:
          image-name: ${{ inputs.image-name }}
          dockerfile: Dockerfile
          context: .
      
      # Composite Action 3: Push Image
      - name: Push Image
        id: push
        uses: ./.github/actions/push-docker-image
        with:
          image-name: ${{ inputs.image-name }}
          registry: ${{ inputs.registry }}
      
      # Composite Action 4: Generate Report
      - name: Generate Build Report
        uses: ./.github/actions/generate-report
        with:
          image-digest: ${{ steps.build.outputs.digest }}
      
      # Set output for parent workflow
      - name: Set Output
        id: image
        run: |
          echo "url=${{ inputs.registry }}/${{ inputs.image-name }}:latest" >> $GITHUB_OUTPUT
```

**Parent calls this with composite actions inside:**
```yaml
# main.yml
jobs:
  build-prod:
    uses: ./.github/workflows/build.yml
    with:
      registry: myregistry.azurecr.io
      image-name: production/app
    secrets:
      REGISTRY_TOKEN: ${{ secrets.REGISTRY_TOKEN }}
```

---

## 🌟 Real-World Examples

### Example 1: Complete CI/CD Pipeline (Your Docker Project)

**Directory Structure:**
```
.github/
├── workflows/
│   ├── main.yml
│   ├── build.yml
│   └── deploy.yml
│
└── actions/
    ├── acr-login/action.yml
    ├── backup-tag/action.yml
    ├── build-docker-image/action.yml
    ├── push-docker-image/action.yml
    ├── cleanup-old-tags/action.yml
    └── update-aca/action.yml
```

**`main.yml` (Parent):**
```yaml
name: Docker Build & Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  call-build:
    uses: ./.github/workflows/build.yml
    secrets: inherit

  call-deploy:
    needs: call-build
    uses: ./.github/workflows/deploy.yml
    secrets: inherit
```

**`build.yml` (Child with Composite Actions):**
```yaml
name: Build Docker Image

on:
  workflow_call:
    secrets:
      AZURE_CLIENT_ID:
        required: true
      AZURE_TENANT_ID:
        required: true
      AZURE_SUBSCRIPTION_ID:
        required: true
      ACR_NAME:
        required: true

jobs:
  build-docker:
    runs-on: ubuntu-latest
    environment: dev
    env:
      ACR_NAME: ${{ secrets.ACR_NAME }}
      REPO: mcp

    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      # Composite Actions sequence
      - uses: ./.github/actions/acr-login
      - uses: ./.github/actions/backup-tag
      - uses: ./.github/actions/build-docker-image
      - uses: ./.github/actions/push-docker-image
      - uses: ./.github/actions/cleanup-old-tags
```

**`deploy.yml` (Child with Composite Actions):**
```yaml
name: Deploy to Azure Container App

on:
  workflow_call:
    secrets:
      AZURE_CLIENT_ID:
        required: true
      AZURE_TENANT_ID:
        required: true
      AZURE_SUBSCRIPTION_ID:
        required: true

jobs:
  deploy-aca:
    runs-on: ubuntu-latest
    environment: dev
    env:
      ACA_NAME: ${{ secrets.ACA_NAME }}
      ACA_RG: ${{ secrets.ACA_RG }}

    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - uses: ./.github/actions/update-aca
```

---

### Example 2: Multi-Platform Build Pipeline

```yaml
# main.yml
name: Multi-Platform Build

on:
  push:
    branches: [main]

jobs:
  # Build for multiple platforms in parallel
  build-linux:
    uses: ./.github/workflows/build-platform.yml
    with:
      platform: linux
      arch: amd64

  build-windows:
    uses: ./.github/workflows/build-platform.yml
    with:
      platform: windows
      arch: amd64

  build-macos:
    uses: ./.github/workflows/build-platform.yml
    with:
      platform: macos
      arch: arm64

  # Consolidate and deploy
  consolidate:
    needs: [build-linux, build-windows, build-macos]
    uses: ./.github/workflows/consolidate.yml
```

---

## 📋 Best Practices

### ✅ Composite Actions Best Practices

1. **Clear Naming:**
   ```yaml
   # Good
   name: Login to Azure Container Registry
   
   # Bad
   name: ACR login
   ```

2. **Input Validation:**
   ```yaml
   steps:
     - name: Validate inputs
       shell: bash
       run: |
         if [ -z "${{ inputs.registry }}" ]; then
           echo "Error: registry input required" >&2
           exit 1
         fi
   ```

3. **Error Handling:**
   ```yaml
   steps:
     - name: Do work with error handling
       shell: bash
       run: |
         set -e  # Exit on error
         command1 || { echo "Command 1 failed"; exit 1; }
         command2
   ```

4. **Document Inputs/Outputs:**
   ```yaml
   inputs:
     image-name:
       description: |
         Full image name including registry
         Example: myregistry.azurecr.io/myapp
       required: true
   ```

---

### ✅ Reusable Workflows Best Practices

1. **Version Control with Tags:**
   ```yaml
   # Use specific version
   jobs:
     build:
       uses: org/repo/.github/workflows/build.yml@v1.0.0
   
   # Or use commit SHA
   jobs:
     build:
       uses: org/repo/.github/workflows/build.yml@abc123
   ```

2. **Explicit Secrets Mapping:**
   ```yaml
   # Good
   jobs:
     deploy:
       uses: ./.github/workflows/deploy.yml
       secrets:
         TOKEN: ${{ secrets.TOKEN }}
         API_KEY: ${{ secrets.API_KEY }}
   
   # Avoid (all secrets inherited)
   jobs:
     deploy:
       uses: ./.github/workflows/deploy.yml
       secrets: inherit
   ```

3. **Clear Inputs Definition:**
   ```yaml
   on:
     workflow_call:
       inputs:
         environment:
           description: Target deployment environment (dev, staging, prod)
           type: string
           required: true
       
       secrets:
         DEPLOY_TOKEN:
           description: Token with deploy permissions
           required: true
   ```

4. **Output Documentation:**
   ```yaml
   outputs:
     image-digest:
       description: SHA256 digest of the built image
       value: ${{ jobs.build.outputs.digest }}
     
     deployment-url:
       description: URL of deployed application
       value: ${{ jobs.deploy.outputs.app-url }}
   ```

---

### ✅ Parent-Child Best Practices

1. **Use `needs` for Dependencies:**
   ```yaml
   jobs:
     build:
       uses: ./.github/workflows/build.yml
     
     test:
       needs: build      # Must complete before test starts
       uses: ./.github/workflows/test.yml
     
     deploy:
       needs: [build, test]  # Multiple dependencies
       uses: ./.github/workflows/deploy.yml
   ```

2. **Pass Data via Inputs:**
   ```yaml
   # Parent
   jobs:
     build:
       uses: ./.github/workflows/build.yml
       with:
         image-name: myapp:${{ github.sha }}
   
   # Child uses input
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - run: echo "Building ${{ inputs.image-name }}"
   ```

3. **Return Data via Outputs:**
   ```yaml
   # Child workflow
   outputs:
     image-digest:
       value: ${{ jobs.build.outputs.digest }}
   
   # Parent uses output
   - name: Deploy
     run: echo "Image: ${{ needs.build.outputs.image-digest }}"
   ```

4. **Conditional Execution:**
   ```yaml
   jobs:
     test:
       uses: ./.github/workflows/test.yml
     
     deploy:
       needs: test
       if: success()            # Only if test passed
       uses: ./.github/workflows/deploy.yml
     
     notify:
       needs: deploy
       if: always()             # Run regardless of outcome
       uses: ./.github/workflows/notify.yml
   ```

---

## 🔍 Troubleshooting

### Composite Actions

**Issue:** Composite action not found
```
Error: Can't find 'action.yml' file in './.github/actions/my-action'
```
**Solution:** Ensure `action.yml` exists in the action directory

**Issue:** Outputs not working
```
Error: ${{ steps.step-id.outputs.output-name }} is empty
```
**Solution:** Ensure step has `id:` and output is set via `$GITHUB_OUTPUT`

---

### Reusable Workflows

**Issue:** Secrets not passed to child
```
Error: ${{ secrets.TOKEN }} is empty in reusable workflow
```
**Solution:** Pass secrets explicitly or use `secrets: inherit`

**Issue:** Circular dependency
```
Error: Job 'deploy' depends on 'test' which depends on 'build' which depends on 'deploy'
```
**Solution:** Check `needs:` declarations for circular references

---

## 📞 Quick Reference

### Composite Action Template
```yaml
name: My Action
description: Does something useful

inputs:
  param:
    required: true

outputs:
  result:
    value: ${{ steps.work.outputs.result }}

runs:
  using: composite
  steps:
    - id: work
      shell: bash
      run: echo "result=value" >> $GITHUB_OUTPUT
```

### Reusable Workflow Template
```yaml
name: My Workflow

on:
  workflow_call:
    inputs:
      param:
        type: string
        required: true
    secrets:
      TOKEN:
        required: true
    outputs:
      result:
        value: ${{ jobs.work.outputs.result }}

jobs:
  work:
    runs-on: ubuntu-latest
    outputs:
      result: ${{ steps.step.outputs.result }}
    steps:
      - id: step
        run: echo "result=value" >> $GITHUB_OUTPUT
```

### Parent Workflow Template
```yaml
name: Parent

on:
  push:
    branches: [main]

jobs:
  call-child:
    uses: ./.github/workflows/child.yml
    with:
      param: value
    secrets:
      TOKEN: ${{ secrets.TOKEN }}
  
  next-job:
    needs: call-child
    uses: ./.github/workflows/next.yml
    with:
      prev-result: ${{ needs.call-child.outputs.result }}
```

---

## 📚 Further Learning

- [GitHub Composite Actions Docs](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [GitHub Reusable Workflows Docs](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

**Document Version:** 1.0  
**Last Updated:** December 23, 2025  
**Status:** Complete & Production Ready
