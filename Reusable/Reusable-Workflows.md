# Reusable Workflows

## 📋 What Are Reusable Workflows?

**Reusable workflows** are GitHub Actions workflows that can be called from other workflows. They are essentially the **workflow equivalent of composite actions** but operate at the job level instead of the step level.

### Key Characteristics
- ✅ Defined in `.github/workflows/`
- ✅ Called using `uses: owner/repo/.github/workflows/workflow-name.yml@ref`
- ✅ Can accept inputs and secrets
- ✅ Can return outputs
- ✅ Useful for multi-job workflows

---

## 📂 Folder Structure

```
your-repo/
├── .github/
│   └── workflows/
│       ├── main-workflow.yml           (Caller workflow)
│       ├── reusable-build.yml          (Reusable workflow)
│       ├── reusable-test.yml           (Reusable workflow)
│       ├── reusable-deploy.yml         (Reusable workflow)
│       └── [other workflows]
│
└── ... (other repo files)
```

**OR with organization:**

```
your-repo/
├── .github/
│   └── workflows/
│       ├── main.yml
│       ├── reusable/
│       │   ├── build.yml
│       │   ├── test.yml
│       │   └── deploy.yml
│       └── [other workflows]
```

---

## 🔧 Reusable Workflow Syntax

### Basic Structure

```yaml
name: 'Reusable Workflow Name'
description: 'What this workflow does'

on:
  workflow_call:
    # Inputs from the calling workflow
    inputs:
      input-name-1:
        description: 'Description'
        required: true
        type: string
      input-name-2:
        description: 'Another input'
        required: false
        type: string
        default: 'default-value'
    
    # Secrets from the calling workflow
    secrets:
      secret-name-1:
        description: 'Secret description'
        required: true
      secret-name-2:
        required: false
    
    # Outputs from this workflow
    outputs:
      output-name-1:
        description: 'What this output contains'
        value: ${{ jobs.job-id.outputs.output-name-1 }}

# Job definitions
jobs:
  job-name:
    runs-on: ubuntu-latest
    outputs:
      output-name-1: ${{ steps.step-id.outputs.output-name-1 }}
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Step Name
        id: step-id
        run: |
          echo "output-name-1=value" >> $GITHUB_OUTPUT
          echo "Using input: ${{ inputs.input-name-1 }}"
          echo "Using secret: ${{ secrets.secret-name-1 }}"
```

---

## 🔧 Calling a Reusable Workflow

### From Local Repository

```yaml
name: 'Main Workflow'
on: [push]

jobs:
  call-reusable:
    uses: ./.github/workflows/reusable-build.yml
    with:
      input-name-1: 'value1'
      input-name-2: 'value2'
    secrets:
      secret-name-1: ${{ secrets.MY_SECRET }}
```

### From External Repository

```yaml
name: 'Main Workflow'
on: [push]

jobs:
  call-reusable:
    uses: owner/repo/.github/workflows/reusable-build.yml@main
    with:
      input-name-1: 'value1'
    secrets:
      secret-name-1: ${{ secrets.MY_SECRET }}
```

---

## 📝 How It Works (Step by Step)

### Step 1: Create Reusable Workflow

**File:** `.github/workflows/reusable-build.yml`

```yaml
name: 'Reusable Build'

on:
  workflow_call:
    inputs:
      node-version:
        description: 'Node.js version'
        required: true
        type: string
      build-command:
        description: 'Build command'
        required: false
        type: string
        default: 'npm run build'
    
    outputs:
      build-artifact:
        description: 'Build artifact path'
        value: ${{ jobs.build.outputs.artifact }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      artifact: ${{ steps.result.outputs.artifact }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: ${{ inputs.node-version }}
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        id: result
        run: |
          ${{ inputs.build-command }}
          echo "artifact=./dist" >> $GITHUB_OUTPUT
          echo "✅ Build completed"
```

### Step 2: Create Caller Workflow

**File:** `.github/workflows/main.yml`

```yaml
name: 'Main Pipeline'

on:
  push:
    branches: [main]

jobs:
  build-job:
    name: 'Build Step'
    uses: ./.github/workflows/reusable-build.yml
    with:
      node-version: '18'
      build-command: 'npm run build'

  deploy-job:
    name: 'Deploy Step'
    needs: build-job
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: |
          echo "Deploying artifact: ${{ needs.build-job.outputs.build-artifact }}"
```

---

## ✅ Your Docker Example

### Reusable Workflow: Build

**File:** `.github/workflows/reusable/build-docker.yml`

```yaml
name: 'Build Docker Image'

on:
  workflow_call:
    inputs:
      dockerfile:
        description: 'Path to Dockerfile'
        required: true
        type: string
      image-name:
        description: 'Docker image name'
        required: true
        type: string
    
    outputs:
      image-tag:
        description: 'Built image tag'
        value: ${{ jobs.build.outputs.tag }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.build.outputs.tag }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set image tag
        id: build
        run: |
          TAG=${{ github.sha }}
          docker build -f ${{ inputs.dockerfile }} -t ${{ inputs.image-name }}:$TAG .
          echo "tag=$TAG" >> $GITHUB_OUTPUT
          echo "✅ Built: ${{ inputs.image-name }}:$TAG"
```

### Reusable Workflow: Push

**File:** `.github/workflows/reusable/push-docker.yml`

```yaml
name: 'Push Docker Image'

on:
  workflow_call:
    inputs:
      image-name:
        required: true
        type: string
      image-tag:
        required: true
        type: string
      registry:
        required: true
        type: string
    
    secrets:
      registry-username:
        required: true
      registry-password:
        required: true

jobs:
  push:
    runs-on: ubuntu-latest
    
    steps:
      - name: Login to registry
        run: |
          echo "${{ secrets.registry-password }}" | \
          docker login -u "${{ secrets.registry-username }}" \
          --password-stdin "${{ inputs.registry }}"
      
      - name: Push image
        run: |
          docker tag ${{ inputs.image-name }}:${{ inputs.image-tag }} \
          ${{ inputs.registry }}/${{ inputs.image-name }}:${{ inputs.image-tag }}
          docker push ${{ inputs.registry }}/${{ inputs.image-name }}:${{ inputs.image-tag }}
          echo "✅ Pushed: ${{ inputs.registry }}/${{ inputs.image-name }}:${{ inputs.image-tag }}"
```

### Main Caller Workflow

**File:** `.github/workflows/main.yml`

```yaml
name: 'Build and Push'

on:
  push:
    branches: [main]

jobs:
  build:
    name: 'Build Docker Image'
    uses: ./.github/workflows/reusable/build-docker.yml
    with:
      dockerfile: MCPAgent/dockerfile
      image-name: mcp

  push:
    name: 'Push to Registry'
    needs: build
    uses: ./.github/workflows/reusable/push-docker.yml
    with:
      image-name: mcp
      image-tag: ${{ needs.build.outputs.image-tag }}
      registry: tlcaimcpacr.azurecr.io
    secrets:
      registry-username: ${{ secrets.ACR_USERNAME }}
      registry-password: ${{ secrets.ACR_PASSWORD }}
```

---

## 🔄 Reusable Workflow Execution Flow

```
main.yml (calls)
    ↓
    ├─→ reusable/build-docker.yml
    │   (builds image, outputs tag)
    │   ↓
    │   (completes, returns output)
    │
    └─→ reusable/push-docker.yml (waits for build)
        (pushes image using tag from build)
        ↓
        (completes)
```

---

## 📊 Comparison: Composite vs Reusable Workflows

| Feature | Composite Actions | Reusable Workflows |
|---------|-------------------|-------------------|
| **Location** | `.github/actions/` | `.github/workflows/` |
| **Scope** | Steps | Jobs |
| **Input Type** | Simple values | string, boolean, number |
| **Complexity** | Simple tasks | Complex multi-job pipelines |
| **Reuse** | Within repo | Within or across repos |
| **Definition** | `action.yml` | `on: workflow_call:` |
| **Best For** | Single-step reuse | Multi-step, multi-job reuse |

---

## ✨ Best Practices

✅ **Do:**
- Keep reusable workflows focused on one responsibility
- Use descriptive input/output names
- Document all inputs and outputs
- Use `workflow_call` for reusable workflows
- Version your reusable workflows with tags
- Use required secrets and inputs when needed

❌ **Don't:**
- Make reusable workflows too complex
- Hardcode environment-specific values
- Store secrets in workflow files
- Create deeply nested workflow calls
- Forget to handle errors

---

## � Key Differences: Composite vs Reusable

Understanding when to use each:

### Composite Actions
```yaml
# Location: .github/actions/my-action/action.yml
name: 'My Action'
runs:
  using: 'composite'
  steps:
    - run: echo "Step-level reuse"
      shell: bash
```

### Reusable Workflows
```yaml
# Location: .github/workflows/my-workflow.yml
name: 'My Workflow'
on:
  workflow_call:

jobs:
  my-job:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Job-level reuse"
```

### Comparison Table

| Feature | Composite Actions | Reusable Workflows |
|---------|-------------------|-------------------|
| **Scope** | Steps within a job | Entire jobs |
| **Can use actions** | ✅ Yes | ✅ Yes |
| **Can have multiple jobs** | ❌ No | ✅ Yes |
| **Can use secrets** | ✅ (as inputs) | ✅ (dedicated section) |
| **Can use `needs:`** | ❌ No | ✅ Yes |
| **Can use matrix** | ❌ No | ✅ Yes |
| **Can use environments** | ❌ No | ✅ Yes |
| **Best for** | Simple reusable steps | Complex multi-job workflows |
| **Visibility** | Local or external | Local or external |
| **Trigger** | Within a job step | As a complete job |

### When to Use What?

**Use Composite Actions when:**
- Reusing a few simple steps
- Need to run within a single job
- No need for multiple jobs or runners
- Simple input/output handling

**Use Reusable Workflows when:**
- Need multiple jobs
- Require different runners
- Need matrix strategies
- Complex workflows with dependencies
- Need environment protection rules

---

## 🔄 Calling Strategies

### Strategy 1: Local Reference

```yaml
jobs:
  call-local:
    uses: ./.github/workflows/reusable.yml
    with:
      param1: value1
```

### Strategy 2: External Reference (Same Org)

```yaml
jobs:
  call-external:
    uses: myorg/shared-workflows/.github/workflows/build.yml@main
    with:
      param1: value1
```

### Strategy 3: Version Pinning

```yaml
jobs:
  # Use specific version tag
  call-v1:
    uses: myorg/shared-workflows/.github/workflows/build.yml@v1.0.0
  
  # Use commit SHA (most secure)
  call-sha:
    uses: myorg/shared-workflows/.github/workflows/build.yml@abc123def456
  
  # Use branch (less stable)
  call-main:
    uses: myorg/shared-workflows/.github/workflows/build.yml@main
```

### Strategy 4: Dynamic Selection

```yaml
jobs:
  determine-workflow:
    runs-on: ubuntu-latest
    outputs:
      workflow-ref: ${{ steps.select.outputs.ref }}
    steps:
      - id: select
        run: |
          if [ "${{ github.event_name }}" == "push" ]; then
            echo "ref=v2.0.0" >> $GITHUB_OUTPUT
          else
            echo "ref=v1.0.0" >> $GITHUB_OUTPUT
          fi
  
  call-workflow:
    needs: determine-workflow
    uses: myorg/workflows/.github/workflows/build.yml@${{ needs.determine-workflow.outputs.workflow-ref }}
```

---

## 📦 Passing Complex Data

### Pass JSON Objects

```yaml
# Caller
jobs:
  call-with-json:
    uses: ./.github/workflows/process.yml
    with:
      config: '{"env":"prod","region":"us-east","replicas":3}'

# Reusable workflow
on:
  workflow_call:
    inputs:
      config:
        type: string
        required: true

jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - name: Parse JSON
        id: parse
        run: |
          ENV=$(echo '${{ inputs.config }}' | jq -r '.env')
          REGION=$(echo '${{ inputs.config }}' | jq -r '.region')
          REPLICAS=$(echo '${{ inputs.config }}' | jq -r '.replicas')
          echo "env=$ENV" >> $GITHUB_OUTPUT
          echo "region=$REGION" >> $GITHUB_OUTPUT
          echo "replicas=$REPLICAS" >> $GITHUB_OUTPUT
```

### Pass Arrays

```yaml
# Caller
jobs:
  call-with-array:
    uses: ./.github/workflows/process.yml
    with:
      environments: '["dev","staging","prod"]'

# Reusable workflow
jobs:
  process:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: ${{ fromJson(inputs.environments) }}
    steps:
      - run: echo "Deploying to ${{ matrix.environment }}"
```

### Pass Multiple Outputs

```yaml
# Reusable workflow (returns multiple values)
on:
  workflow_call:
    outputs:
      build-version:
        value: ${{ jobs.build.outputs.version }}
      build-time:
        value: ${{ jobs.build.outputs.time }}
      artifact-url:
        value: ${{ jobs.build.outputs.url }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.value }}
      time: ${{ steps.time.outputs.value }}
      url: ${{ steps.artifact.outputs.url }}
    steps:
      - id: version
        run: echo "value=1.0.0" >> $GITHUB_OUTPUT
      - id: time
        run: echo "value=$(date -u)" >> $GITHUB_OUTPUT
      - id: artifact
        run: echo "url=https://example.com/artifact" >> $GITHUB_OUTPUT

# Caller uses multiple outputs
jobs:
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "Version: ${{ needs.build.outputs.build-version }}"
          echo "Built at: ${{ needs.build.outputs.build-time }}"
          echo "Download: ${{ needs.build.outputs.artifact-url }}"
```

### Share Files via Artifacts

```yaml
# Reusable workflow 1: Generate files
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - run: echo "data" > output.txt
      - uses: actions/upload-artifact@v3
        with:
          name: shared-data
          path: output.txt

# Reusable workflow 2: Use files
jobs:
  consume:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v3
        with:
          name: shared-data
      - run: cat output.txt
```

---

## 🏷️ Versioning Strategies

### Semantic Versioning

```bash
# Create version tags
git tag v1.0.0
git push origin v1.0.0

# Major version tag (update as needed)
git tag -f v1
git push -f origin v1
```

**Usage:**
```yaml
# Pin to exact version (recommended for production)
uses: myorg/workflows/.github/workflows/build.yml@v1.0.0

# Use major version (gets latest v1.x.x)
uses: myorg/workflows/.github/workflows/build.yml@v1

# Use branch (development only)
uses: myorg/workflows/.github/workflows/build.yml@main
```

### Version Matrix Testing

```yaml
name: Test Workflow Versions

on: [push]

jobs:
  test-v1:
    uses: myorg/workflows/.github/workflows/test.yml@v1.0.0
  
  test-v2:
    uses: myorg/workflows/.github/workflows/test.yml@v2.0.0
  
  test-main:
    uses: myorg/workflows/.github/workflows/test.yml@main
  
  compare-results:
    needs: [test-v1, test-v2, test-main]
    runs-on: ubuntu-latest
    steps:
      - run: echo "All versions tested successfully"
```

### Breaking Change Management

```yaml
# v1.0.0 (old interface)
on:
  workflow_call:
    inputs:
      image-name:
        type: string
        required: true

# v2.0.0 (new interface - breaking change)
on:
  workflow_call:
    inputs:
      registry:
        type: string
        required: true
      repository:
        type: string
        required: true
      tag:
        type: string
        required: false
        default: latest

# Migration guide in README.md
```

### Deprecation Warnings

```yaml
# v1.x.x (to be deprecated)
jobs:
  warn:
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "::warning::This workflow version is deprecated."
          echo "::warning::Please migrate to v2.0.0 by 2025-12-31"
          echo "::warning::See: https://github.com/myorg/workflows/releases/v2.0.0"
  
  actual-work:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Doing work..."
```

---

## 🔒 Security Considerations

### Secret Handling

```yaml
# ❌ DON'T: Pass secrets as inputs
on:
  workflow_call:
    inputs:
      api-key:  # WRONG!
        type: string
        required: true

# ✅ DO: Use secrets section
on:
  workflow_call:
    secrets:
      api-key:  # CORRECT!
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Use secret
        env:
          API_KEY: ${{ secrets.api-key }}
        run: |
          # Use $API_KEY (not visible in logs)
          echo "Deploying with API key..."
```

### GITHUB_TOKEN Permissions

```yaml
# Reusable workflow
name: Secure Workflow
on:
  workflow_call:

permissions:
  contents: read      # Minimum required permissions
  pull-requests: write

jobs:
  job1:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
```

### Input Validation

```yaml
jobs:
  validate-and-process:
    runs-on: ubuntu-latest
    steps:
      - name: Validate inputs
        run: |
          # Validate environment
          if [[ ! "${{ inputs.environment }}" =~ ^(dev|staging|prod)$ ]]; then
            echo "::error::Invalid environment: ${{ inputs.environment }}"
            exit 1
          fi
          
          # Validate version format
          if [[ ! "${{ inputs.version }}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo "::error::Invalid version format: ${{ inputs.version }}"
            exit 1
          fi
```

### Prevent Code Injection

```yaml
# ❌ DANGEROUS: Direct interpolation
steps:
  - run: echo "${{ inputs.user-input }}"  # Can be exploited!

# ✅ SAFE: Use environment variable
steps:
  - env:
      USER_INPUT: ${{ inputs.user-input }}
    run: echo "$USER_INPUT"
```

### Audit Logging

```yaml
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - name: Log workflow call
        run: |
          echo "Workflow called by: ${{ github.actor }}"
          echo "Trigger: ${{ github.event_name }}"
          echo "Inputs: ${{ toJson(inputs) }}"
          echo "Timestamp: $(date -u)"
          
          # Send to audit system
          curl -X POST https://audit.example.com/log \
            -d '{"actor":"${{ github.actor }}","workflow":"${{ github.workflow }}"}'
```

---

## 🚀 Migration Guide

### From Duplicate Workflows to Reusable

**Before (Duplicate Code):**
```yaml
# workflow1.yml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install
      - run: npm run build

# workflow2.yml (same code!)
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install
      - run: npm run build
```

**After (Reusable):**
```yaml
# reusable-build.yml
name: Reusable Build
on:
  workflow_call:
    inputs:
      node-version:
        type: string
        default: '18'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v3
        with:
          node-version: ${{ inputs.node-version }}
      - run: npm install
      - run: npm run build

# workflow1.yml (now calls reusable)
jobs:
  build:
    uses: ./.github/workflows/reusable-build.yml
    with:
      node-version: '18'

# workflow2.yml (also calls reusable)
jobs:
  build:
    uses: ./.github/workflows/reusable-build.yml
    with:
      node-version: '16'
```

### From Composite Actions to Reusable Workflows

**When to migrate:**
- Need multiple jobs
- Need different runners
- Need matrix strategies
- Need environment protection

**Migration steps:**
1. Create new workflow with `on: workflow_call:`
2. Move jobs from composite action
3. Convert inputs to workflow inputs
4. Update callers to use `uses:` at job level
5. Test thoroughly
6. Update documentation

---

## 📊 Advanced Patterns

### Pattern 1: Workflow Chaining

```yaml
# Stage 1
jobs:
  build:
    uses: ./.github/workflows/build.yml
    
# Stage 2 (uses output from stage 1)
  test:
    needs: build
    uses: ./.github/workflows/test.yml
    with:
      build-id: ${{ needs.build.outputs.build-id }}

# Stage 3 (uses outputs from both)
  deploy:
    needs: [build, test]
    uses: ./.github/workflows/deploy.yml
    with:
      build-id: ${{ needs.build.outputs.build-id }}
      test-result: ${{ needs.test.outputs.result }}
```

### Pattern 2: Conditional Workflows

```yaml
jobs:
  determine-path:
    runs-on: ubuntu-latest
    outputs:
      should-deploy: ${{ steps.check.outputs.deploy }}
    steps:
      - id: check
        run: |
          if [ "${{ github.ref }}" == "refs/heads/main" ]; then
            echo "deploy=true" >> $GITHUB_OUTPUT
          else
            echo "deploy=false" >> $GITHUB_OUTPUT
          fi
  
  deploy-prod:
    needs: determine-path
    if: needs.determine-path.outputs.should-deploy == 'true'
    uses: ./.github/workflows/deploy.yml
    with:
      environment: production
```

### Pattern 3: Error Recovery

```yaml
jobs:
  primary-deploy:
    uses: ./.github/workflows/deploy-primary.yml
    continue-on-error: true
  
  fallback-deploy:
    needs: primary-deploy
    if: needs.primary-deploy.result == 'failure'
    uses: ./.github/workflows/deploy-fallback.yml
  
  notify:
    needs: [primary-deploy, fallback-deploy]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - run: |
          if [ "${{ needs.primary-deploy.result }}" == "success" ]; then
            echo "Primary deployment succeeded"
          else
            echo "Fallback deployment: ${{ needs.fallback-deploy.result }}"
          fi
```

---

## 🎯 Summary

Reusable workflows let you:
- **Encapsulate** complex CI/CD logic at job level
- **Reuse** across multiple workflows
- **Share** within or across organizations
- **Version** for stable releases
- **Organize** by functionality
- **Pass complex data** with inputs/outputs
- **Secure** with proper secret handling
- **Optimize** with parallelization and caching
- **Validate** inputs for security
- **Migrate** from duplicate code

Perfect for standardizing builds, tests, and deployments across your organization!
