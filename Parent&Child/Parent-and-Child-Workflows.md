# Parent and Child Workflows

## 📋 What Are Parent-Child Workflows?

A **parent workflow** calls (reuses) one or more **child workflows**. This allows you to organize complex CI/CD pipelines into smaller, manageable, reusable workflows.

### Key Concepts
- ✅ Parent = Main workflow that orchestrates
- ✅ Child = Reusable workflow that performs specific tasks
- ✅ Parent calls child using `uses:` keyword
- ✅ Child receives inputs from parent, returns outputs

---

## 📂 Folder Structure

```
your-repo/
├── .github/
│   └── workflows/
│       ├── parent-workflow.yml      (Main orchestrator)
│       ├── child-build.yml          (Child workflow)
│       ├── child-test.yml           (Child workflow)
│       ├── child-deploy.yml         (Child workflow)
│       └── [other workflows]
└── ... (other repo files)
```

**OR organize in subfolders:**

```
your-repo/
├── .github/
│   └── workflows/
│       ├── parent.yml
│       ├── reusable/
│       │   ├── build.yml
│       │   ├── test.yml
│       │   └── deploy.yml
│       └── [other workflows]
```

---

## 🔧 Child Workflow Syntax

A **reusable workflow** (child) is defined with `on.workflow_call`:

```yaml
name: 'Child Workflow Name'
description: 'What this workflow does'

on:
  workflow_call:
    # Define inputs from parent
    inputs:
      input-name-1:
        description: 'Input description'
        required: true
        type: string
      input-name-2:
        description: 'Another input'
        required: false
        type: string
        default: 'default-value'
    
    # Define secrets from parent
    secrets:
      secret-name-1:
        description: 'Secret description'
        required: true
      secret-name-2:
        required: false
    
    # Define outputs to parent
    outputs:
      output-name:
        description: 'What this output contains'
        value: ${{ jobs.job-id.outputs.output-name }}

jobs:
  job-name:
    runs-on: ubuntu-latest
    outputs:
      output-name: ${{ steps.step-id.outputs.output-name }}
    
    steps:
      - name: Step 1
        id: step-id
        run: |
          echo "output-name=value" >> $GITHUB_OUTPUT
      
      - name: Step 2
        run: |
          echo "Using input: ${{ inputs.input-name-1 }}"
          echo "Using secret: ${{ secrets.secret-name-1 }}"
```

---

## 🔧 Parent Workflow Syntax

A **parent workflow** calls child workflows:

```yaml
name: 'Parent Workflow'

on:
  push:
    branches: [main]

jobs:
  call-child-workflow:
    uses: ./.github/workflows/child-workflow.yml
    with:
      input-name-1: 'value1'
      input-name-2: 'value2'
    secrets:
      secret-name-1: ${{ secrets.MY_SECRET }}
      secret-name-2: ${{ secrets.ANOTHER_SECRET }}

  use-child-output:
    needs: call-child-workflow
    runs-on: ubuntu-latest
    steps:
      - name: Use output from child
        run: |
          echo "Result: ${{ needs.call-child-workflow.outputs.output-name }}"
```

---

## 📝 How It Works (Step by Step)

### Step 1: Create Child Workflow

**File:** `.github/workflows/child-build.yml`

```yaml
name: 'Build Application'

on:
  workflow_call:
    inputs:
      node-version:
        description: 'Node version to use'
        required: true
        type: string
    outputs:
      build-status:
        description: 'Build result'
        value: ${{ jobs.build.outputs.status }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      status: ${{ steps.check.outputs.result }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: ${{ inputs.node-version }}
      
      - name: Install dependencies
        run: npm install
      
      - name: Build
        id: check
        run: |
          npm run build
          echo "result=success" >> $GITHUB_OUTPUT
```

### Step 2: Create Parent Workflow

**File:** `.github/workflows/parent.yml`

```yaml
name: 'Main Pipeline'

on:
  push:
    branches: [main]

jobs:
  build-step:
    name: Build
    uses: ./.github/workflows/child-build.yml
    with:
      node-version: '18'

  test-step:
    name: Test
    needs: build-step
    uses: ./.github/workflows/child-test.yml
    with:
      node-version: '18'

  deploy-step:
    name: Deploy
    needs: test-step
    uses: ./.github/workflows/child-deploy.yml
    if: success()
```

### Step 3: View Workflow Execution

When parent runs:
1. Parent starts
2. Calls child-build → waits for completion
3. Gets output from child-build
4. Calls child-test (only if child-build succeeded)
5. Calls child-deploy (only if child-test succeeded)

---

## ✅ Your Docker Example

### Child Workflow: Build

**File:** `.github/workflows/reusable-build.yml`

```yaml
name: 'Build Docker Image'

on:
  workflow_call:
    inputs:
      dockerfile-path:
        required: true
        type: string
      image-name:
        required: true
        type: string
    outputs:
      image-tag:
        value: ${{ jobs.build.outputs.tag }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.build.outputs.tag }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Image
        id: build
        run: |
          TAG=${{ github.sha }}
          docker build -f ${{ inputs.dockerfile-path }} -t ${{ inputs.image-name }}:$TAG .
          echo "tag=$TAG" >> $GITHUB_OUTPUT
          echo "✅ Built: ${{ inputs.image-name }}:$TAG"
```

### Parent Workflow

**File:** `.github/workflows/main.yml`

```yaml
name: 'Main Pipeline'

on:
  push:
    branches: [main]

jobs:
  build:
    name: Build Stage
    uses: ./.github/workflows/reusable-build.yml
    with:
      dockerfile-path: MCPAgent/dockerfile
      image-name: mcp

  deploy:
    name: Deploy Stage
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy Image
        run: |
          echo "Deploying: mcp:${{ needs.build.outputs.image-tag }}"
```

---

## 🔗 Key Differences

| Aspect | Composite Actions | Parent-Child Workflows |
|--------|-------------------|------------------------|
| **Use Case** | Reuse simple steps | Orchestrate complex jobs |
| **Location** | `.github/actions/` | `.github/workflows/` |
| **Definition** | `action.yml` | `on: workflow_call:` |
| **Reference** | `uses: ./.github/actions/...` | `uses: ./.github/workflows/...` |
| **Job Control** | Single job | Multiple jobs |
| **Complexity** | Simple | Complex |

---

## ✨ Best Practices

✅ **Do:**
- Use meaningful names for workflows
- Document inputs and outputs clearly
- Use `needs:` to control job order
- Pass secrets securely
- Keep child workflows focused

❌ **Don't:**
- Make child workflows too complex
- Hardcode values (use inputs)
- Pass sensitive data in logs
- Create deeply nested parent-child chains

---

## 📊 Complete Example: Build → Test → Deploy

### Child 1: Build (`.github/workflows/build.yml`)
```yaml
name: 'Build'
on:
  workflow_call:
    outputs:
      version:
        value: ${{ jobs.build.outputs.version }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: v1.0.0
    steps:
      - run: echo "Building..."
```

### Child 2: Test (`.github/workflows/test.yml`)
```yaml
name: 'Test'
on:
  workflow_call:
    inputs:
      version:
        type: string
        required: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Testing version ${{ inputs.version }}"
```

### Child 3: Deploy (`.github/workflows/deploy.yml`)
```yaml
name: 'Deploy'
on:
  workflow_call:
    inputs:
      version:
        type: string
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying version ${{ inputs.version }}"
```

### Parent Workflow (`.github/workflows/main.yml`)
```yaml
name: 'Pipeline'
on: [push]

jobs:
  build:
    uses: ./.github/workflows/build.yml
  
  test:
    needs: build
    uses: ./.github/workflows/test.yml
    with:
      version: ${{ needs.build.outputs.version }}
  
  deploy:
    needs: test
    uses: ./.github/workflows/deploy.yml
    with:
      version: ${{ needs.build.outputs.version }}
```

---

## � Workflow Call Basics (For Beginners)

### What is `workflow_call`?

`workflow_call` is a special trigger that allows one workflow to be called by another workflow, similar to calling a function in programming.

### Key Differences from Regular Workflows

| Regular Workflow | Reusable Workflow |
|-----------------|-------------------|
| `on: push:` or `on: pull_request:` | `on: workflow_call:` |
| Triggered by GitHub events | Triggered by other workflows |
| Standalone execution | Called as a dependency |
| Cannot accept inputs from caller | Can accept inputs and secrets |
| Cannot return outputs | Can return outputs to caller |

### Basic Example

**Child (Reusable):**
```yaml
name: Reusable Workflow
on:
  workflow_call:  # This makes it reusable
    inputs:
      message:
        required: true
        type: string

jobs:
  greet:
    runs-on: ubuntu-latest
    steps:
      - run: echo "${{ inputs.message }}"
```

**Parent (Caller):**
```yaml
name: Parent Workflow
on: [push]

jobs:
  call-child:
    uses: ./.github/workflows/child.yml
    with:
      message: "Hello from parent!"
```

---

## 🎯 Matrix Strategies

### Basic Matrix

Run child workflow with different parameters:

```yaml
# Parent workflow
jobs:
  test-matrix:
    strategy:
      matrix:
        node-version: [14, 16, 18]
        os: [ubuntu-latest, windows-latest]
    uses: ./.github/workflows/test.yml
    with:
      node-version: ${{ matrix.node-version }}
      os-type: ${{ matrix.os }}
```

### Matrix with Exclude

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    node: [14, 16, 18]
    exclude:
      - os: macos-latest
        node: 14  # Don't test Node 14 on macOS
```

### Matrix with Include

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node: [16, 18]
    include:
      - os: ubuntu-latest
        node: 20  # Add Node 20 only for Ubuntu
        experimental: true
```

### Dynamic Matrix

```yaml
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - id: set-matrix
        run: |
          # Generate matrix dynamically
          echo 'matrix={"node":[14,16,18],"os":["ubuntu-latest","windows-latest"]}' >> $GITHUB_OUTPUT

  test:
    needs: setup
    strategy:
      matrix: ${{ fromJson(needs.setup.outputs.matrix) }}
    uses: ./.github/workflows/test.yml
    with:
      node-version: ${{ matrix.node }}
```

---

## 🔀 Conditional Execution

### Conditional Job Execution

```yaml
jobs:
  build:
    uses: ./.github/workflows/build.yml
  
  test:
    needs: build
    if: success()  # Only if build succeeds
    uses: ./.github/workflows/test.yml
  
  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/develop'  # Only on develop branch
    uses: ./.github/workflows/deploy.yml
    with:
      environment: staging
  
  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'  # Only on main branch
    uses: ./.github/workflows/deploy.yml
    with:
      environment: production
```

### Conditional with Inputs

```yaml
jobs:
  deploy:
    uses: ./.github/workflows/deploy.yml
    with:
      skip-tests: ${{ github.event.inputs.skip-tests || 'false' }}
    
  notify:
    needs: deploy
    if: always()  # Run even if deploy fails
    runs-on: ubuntu-latest
    steps:
      - name: Send notification
        run: |
          if [ "${{ needs.deploy.result }}" == "success" ]; then
            echo "✅ Deployment successful"
          else
            echo "❌ Deployment failed"
          fi
```

### Conditional Based on Files

```yaml
jobs:
  check-changes:
    runs-on: ubuntu-latest
    outputs:
      backend-changed: ${{ steps.filter.outputs.backend }}
      frontend-changed: ${{ steps.filter.outputs.frontend }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: filter
        with:
          filters: |
            backend:
              - 'backend/**'
            frontend:
              - 'frontend/**'
  
  build-backend:
    needs: check-changes
    if: needs.check-changes.outputs.backend-changed == 'true'
    uses: ./.github/workflows/build-backend.yml
  
  build-frontend:
    needs: check-changes
    if: needs.check-changes.outputs.frontend-changed == 'true'
    uses: ./.github/workflows/build-frontend.yml
```

---

## ⚠️ Error Handling

### Continue on Error

```yaml
jobs:
  build:
    uses: ./.github/workflows/build.yml
  
  test:
    needs: build
    uses: ./.github/workflows/test.yml
    continue-on-error: true  # Don't fail entire workflow
  
  deploy:
    needs: [build, test]
    if: always()  # Run even if test fails
    uses: ./.github/workflows/deploy.yml
```

### Fail Fast vs Fail Slow

```yaml
jobs:
  test:
    strategy:
      fail-fast: false  # Continue other matrix jobs if one fails
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    uses: ./.github/workflows/test.yml
    with:
      os: ${{ matrix.os }}
```

### Error Handling in Child Workflow

```yaml
# Child workflow
name: Build with Error Handling
on:
  workflow_call:
    outputs:
      status:
        value: ${{ jobs.build.outputs.status }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      status: ${{ steps.build.outcome }}
    steps:
      - name: Build
        id: build
        continue-on-error: true
        run: |
          # Build logic here
          npm run build
      
      - name: Handle failure
        if: steps.build.outcome == 'failure'
        run: |
          echo "::error::Build failed, but continuing for cleanup"
          # Cleanup or notification logic
      
      - name: Report status
        if: always()
        run: |
          echo "Build status: ${{ steps.build.outcome }}"
```

### Retry Logic

```yaml
# Parent workflow
jobs:
  deploy-with-retry:
    runs-on: ubuntu-latest
    steps:
      - name: Try deploy (attempt 1)
        id: deploy1
        continue-on-error: true
        uses: ./.github/workflows/deploy.yml
      
      - name: Wait before retry
        if: steps.deploy1.outcome == 'failure'
        run: sleep 60
      
      - name: Try deploy (attempt 2)
        if: steps.deploy1.outcome == 'failure'
        id: deploy2
        continue-on-error: true
        uses: ./.github/workflows/deploy.yml
      
      - name: Try deploy (attempt 3)
        if: steps.deploy2.outcome == 'failure'
        uses: ./.github/workflows/deploy.yml
```

---

## 🔗 Dependency Management

### Linear Dependencies

```yaml
jobs:
  step1:
    uses: ./.github/workflows/build.yml
  
  step2:
    needs: step1
    uses: ./.github/workflows/test.yml
  
  step3:
    needs: step2
    uses: ./.github/workflows/deploy.yml
```

### Parallel with Final Step

```yaml
jobs:
  build-frontend:
    uses: ./.github/workflows/build-frontend.yml
  
  build-backend:
    uses: ./.github/workflows/build-backend.yml
  
  build-mobile:
    uses: ./.github/workflows/build-mobile.yml
  
  integration-test:
    needs: [build-frontend, build-backend, build-mobile]
    uses: ./.github/workflows/integration-test.yml
```

### Complex Dependencies

```yaml
jobs:
  # Stage 1: Parallel builds
  build-api:
    uses: ./.github/workflows/build-api.yml
  
  build-web:
    uses: ./.github/workflows/build-web.yml
  
  # Stage 2: Tests (depend on builds)
  test-api:
    needs: build-api
    uses: ./.github/workflows/test-api.yml
  
  test-web:
    needs: build-web
    uses: ./.github/workflows/test-web.yml
  
  # Stage 3: Integration (depends on all tests)
  integration:
    needs: [test-api, test-web]
    uses: ./.github/workflows/integration.yml
  
  # Stage 4: Deploy (depends on integration)
  deploy-staging:
    needs: integration
    if: github.ref == 'refs/heads/develop'
    uses: ./.github/workflows/deploy.yml
    with:
      environment: staging
  
  deploy-prod:
    needs: integration
    if: github.ref == 'refs/heads/main'
    uses: ./.github/workflows/deploy.yml
    with:
      environment: production
```

### Dependency Visualization

```
       build-api ──→ test-api ──┐
                                 ├──→ integration ──→ deploy
       build-web ──→ test-web ──┘
```

---

## ⚡ Performance Optimization

### Parallel Execution

```yaml
jobs:
  # These run in parallel (no dependencies)
  lint:
    uses: ./.github/workflows/lint.yml
  
  type-check:
    uses: ./.github/workflows/type-check.yml
  
  unit-test:
    uses: ./.github/workflows/unit-test.yml
  
  # This waits for all above
  build:
    needs: [lint, type-check, unit-test]
    uses: ./.github/workflows/build.yml
```

### Caching Across Workflows

```yaml
# Child workflow with caching
name: Build with Cache
on:
  workflow_call:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.npm
            node_modules
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            ${{ runner.os }}-node-
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
```

### Artifact Sharing

```yaml
# Child 1: Build and save artifact
name: Build
on:
  workflow_call:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run build
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: build-output
          path: dist/
          retention-days: 1

# Child 2: Use artifact from build
name: Deploy
on:
  workflow_call:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Download artifact
        uses: actions/download-artifact@v3
        with:
          name: build-output
          path: dist/
      
      - name: Deploy
        run: ./deploy.sh dist/
```

### Concurrency Control

```yaml
# Parent workflow
name: Deploy Pipeline
on: [push]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # Cancel old runs

jobs:
  deploy:
    uses: ./.github/workflows/deploy.yml
```

---

## 🔒 Security Best Practices

### Inherit Secrets Safely

```yaml
jobs:
  deploy:
    uses: ./.github/workflows/deploy.yml
    secrets: inherit  # Pass all secrets
    # OR pass specific secrets:
    secrets:
      API_KEY: ${{ secrets.API_KEY }}
      DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

### Environment Protection

```yaml
jobs:
  deploy-prod:
    uses: ./.github/workflows/deploy.yml
    with:
      environment: production
    secrets: inherit
    # Requires approval rules in Settings → Environments
```

### Permissions

```yaml
jobs:
  build:
    uses: ./.github/workflows/build.yml
    permissions:
      contents: read
      packages: write
```

---

## 🐛 Debugging Tips

### Enable Debug Logging

1. Repository → Settings → Secrets
2. Add secret: `ACTIONS_STEP_DEBUG` = `true`
3. Add secret: `ACTIONS_RUNNER_DEBUG` = `true`

### Add Debug Outputs

```yaml
# Child workflow
jobs:
  debug:
    runs-on: ubuntu-latest
    steps:
      - name: Debug context
        run: |
          echo "Event: ${{ github.event_name }}"
          echo "Ref: ${{ github.ref }}"
          echo "Actor: ${{ github.actor }}"
          echo "Inputs: ${{ toJson(inputs) }}"
```

### Workflow Summary

```yaml
steps:
  - name: Create summary
    run: |
      echo "## Workflow Summary" >> $GITHUB_STEP_SUMMARY
      echo "- Status: ${{ job.status }}" >> $GITHUB_STEP_SUMMARY
      echo "- Duration: ${{ steps.timer.outputs.duration }}s" >> $GITHUB_STEP_SUMMARY
```

---

## 📊 Advanced Patterns

### Pattern 1: Fan-Out / Fan-In

```yaml
jobs:
  # Fan-out: Split work
  shard-1:
    uses: ./.github/workflows/test.yml
    with:
      shard: 1
      total-shards: 4
  
  shard-2:
    uses: ./.github/workflows/test.yml
    with:
      shard: 2
      total-shards: 4
  
  shard-3:
    uses: ./.github/workflows/test.yml
    with:
      shard: 3
      total-shards: 4
  
  shard-4:
    uses: ./.github/workflows/test.yml
    with:
      shard: 4
      total-shards: 4
  
  # Fan-in: Collect results
  report:
    needs: [shard-1, shard-2, shard-3, shard-4]
    runs-on: ubuntu-latest
    steps:
      - name: Aggregate results
        run: echo "All shards completed"
```

### Pattern 2: Progressive Deployment

```yaml
jobs:
  deploy-canary:
    uses: ./.github/workflows/deploy.yml
    with:
      environment: canary
      traffic-percentage: 10
  
  monitor-canary:
    needs: deploy-canary
    runs-on: ubuntu-latest
    steps:
      - name: Monitor for 10 minutes
        run: sleep 600
      - name: Check metrics
        run: ./check-metrics.sh
  
  deploy-full:
    needs: monitor-canary
    if: success()
    uses: ./.github/workflows/deploy.yml
    with:
      environment: production
      traffic-percentage: 100
```

### Pattern 3: Approval Gates

```yaml
jobs:
  build-and-test:
    uses: ./.github/workflows/build.yml
  
  request-approval:
    needs: build-and-test
    runs-on: ubuntu-latest
    environment: production  # Requires manual approval
    steps:
      - run: echo "Awaiting approval..."
  
  deploy:
    needs: request-approval
    uses: ./.github/workflows/deploy.yml
```

---

## 🎯 Summary

Parent-Child workflows let you:
- **Organize** complex CI/CD into manageable pieces
- **Reuse** workflows across multiple parent workflows
- **Control** execution order with `needs:`
- **Pass data** between workflows with inputs/outputs
- **Share secrets** securely
- **Handle errors** gracefully
- **Optimize performance** with parallelization
- **Implement complex patterns** like fan-out/fan-in
- **Add approval gates** for production deployments
- **Debug effectively** with proper logging

Use them when you have multi-stage pipelines!
