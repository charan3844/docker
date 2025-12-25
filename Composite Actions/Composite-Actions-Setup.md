# Composite Actions Setup

## 📋 What Are Composite Actions?

Composite actions are reusable building blocks for GitHub Actions workflows. They bundle multiple steps into a single, reusable action that can be used across different workflows.

### Key Characteristics
- ✅ Store in `.github/actions/` folder
- ✅ Each action has its own folder with `action.yml`
- ✅ Can be used locally or referenced externally
- ✅ Reduce code duplication

---

## 📂 Folder Structure

```
your-repo/
├── .github/
│   └── actions/
│       ├── action-name-1/
│       │   ├── action.yml
│       │   └── [optional: shell scripts, README]
│       ├── action-name-2/
│       │   ├── action.yml
│       │   └── [optional files]
│       └── action-name-3/
│           └── action.yml
└── ... (other repo files)
```

---

## 🔧 Basic Composite Action Syntax

### action.yml File Structure

```yaml
name: 'Action Name'
description: 'What this action does'

# Define inputs (parameters your action accepts)
inputs:
  input-name-1:
    description: 'Description of input'
    required: true
    default: 'default-value'
  input-name-2:
    description: 'Another input'
    required: false

# Define outputs (values your action returns)
outputs:
  output-name:
    description: 'What this output contains'
    value: ${{ steps.step-id.outputs.variable-name }}

# Define the action steps
runs:
  using: 'composite'
  steps:
    - name: Step 1 Name
      shell: bash
      run: |
        echo "Doing something"
        echo "output=$value" >> $GITHUB_OUTPUT
    
    - name: Step 2 Name
      id: step-id
      shell: bash
      run: |
        echo "variable-name=result-value" >> $GITHUB_OUTPUT
```

---

## 📝 How It Works

### Step 1: Create Action Folder
```bash
mkdir -p .github/actions/my-custom-action
cd .github/actions/my-custom-action
touch action.yml
```

### Step 2: Define action.yml
```yaml
name: 'My Custom Action'
description: 'This action does something useful'

inputs:
  name:
    description: 'Name to use'
    required: true

outputs:
  result:
    description: 'Result of the action'
    value: ${{ steps.run.outputs.result }}

runs:
  using: 'composite'
  steps:
    - name: Run custom logic
      id: run
      shell: bash
      run: |
        echo "Hello ${{ inputs.name }}"
        echo "result=Success" >> $GITHUB_OUTPUT
```

### Step 3: Use in Workflow
```yaml
# .github/workflows/example.yml
name: Example Workflow

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Use local composite action
      - uses: ./.github/actions/my-custom-action
        with:
          name: "World"
```

---

## ✅ Your Docker Example

For your Docker setup, you could create:

```
docker/
└── .github/
    └── actions/
        ├── docker-build/
        │   └── action.yml
        ├── acr-login/
        │   └── action.yml
        └── docker-push/
            └── action.yml
```

### docker-build/action.yml
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
    - name: Build Image
      id: build
      shell: bash
      run: |
        IMAGE_FULL_NAME="${{ inputs.image-name }}:${{ inputs.image-tag }}"
        docker build -f ${{ inputs.dockerfile-path }} -t $IMAGE_FULL_NAME .
        echo "image-full-name=$IMAGE_FULL_NAME" >> $GITHUB_OUTPUT
        echo "✅ Built: $IMAGE_FULL_NAME"
```

### Usage in Workflow
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: ./.github/actions/docker-build
        with:
          dockerfile-path: MCPAgent/dockerfile
          image-name: mcp
          image-tag: ${{ github.sha }}
```

---

## 🎯 Best Practices

✅ **Do:**
- Keep each action focused on one task
- Document inputs and outputs clearly
- Use meaningful step IDs for output references
- Test actions locally before using in workflows

❌ **Don't:**
- Make actions too complex (break them up)
- Use hardcoded values (use inputs instead)
- Forget to provide descriptions

---

## 🔗 Local vs External Reference

### Local (In Same Repo)
```yaml
- uses: ./.github/actions/my-action
  with:
    input: value
```

### External (Different Repo)
```yaml
- uses: owner/repo/.github/actions/my-action@main
  with:
    input: value
```

---

## 📊 Example: Complete Composite Action

```yaml
name: 'Login to Registry'
description: 'Login to Docker/Container Registry'

inputs:
  registry:
    description: 'Registry URL'
    required: true
  username:
    description: 'Registry username'
    required: true
  password:
    description: 'Registry password'
    required: true

runs:
  using: 'composite'
  steps:
    - name: Login to Registry
      shell: bash
      run: |
        echo "${{ inputs.password }}" | docker login -u "${{ inputs.username }}" --password-stdin "${{ inputs.registry }}"
        echo "✅ Logged in to ${{ inputs.registry }}"
    
    - name: Verify Login
      shell: bash
      run: |
        docker ps
        echo "✅ Login successful"
```

---

## 🔍 Input Types (Advanced)

GitHub Actions supports different input types for composite actions:

```yaml
inputs:
  string-input:
    description: 'A string value'
    required: true
    type: string
  
  boolean-input:
    description: 'A boolean flag'
    required: false
    type: boolean
    default: 'false'
  
  number-input:
    description: 'A numeric value'
    required: false
    type: number
    default: '10'
```

**Using Boolean Inputs:**
```yaml
steps:
  - name: Conditional step
    shell: bash
    if: ${{ inputs.boolean-input == 'true' }}
    run: echo "Boolean is true"
```

---

## 🧪 Testing Composite Actions

### Method 1: Local Testing

```yaml
# .github/workflows/test-action.yml
name: Test My Action

on: [push, workflow_dispatch]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Test action
        uses: ./.github/actions/my-action
        with:
          input1: test-value
          input2: another-value
      
      - name: Verify output
        run: |
          echo "Output: ${{ steps.test.outputs.result }}"
```

### Method 2: Act (Local Runner)

```bash
# Install act (https://github.com/nektos/act)
# Run workflows locally
act -j test-action
```

### Method 3: Matrix Testing

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/my-action
```

---

## 🐛 Error Handling & Debugging

### Setting Exit Codes

```yaml
runs:
  using: 'composite'
  steps:
    - name: Check something
      shell: bash
      run: |
        if [ ! -f "required-file.txt" ]; then
          echo "::error::Required file not found"
          exit 1
        fi
```

### Annotations

```yaml
steps:
  - name: Validate input
    shell: bash
    run: |
      if [ -z "${{ inputs.required-input }}" ]; then
        echo "::error::Input is required"
        exit 1
      fi
      
      echo "::notice::Processing started"
      echo "::warning::This is a warning message"
      echo "::debug::Debug information here"
```

### Continue on Error

```yaml
steps:
  - name: Risky operation
    shell: bash
    continue-on-error: true
    run: |
      echo "This might fail"
      exit 1
  
  - name: Always runs
    shell: bash
    run: echo "Continuing after error"
```

---

## 🎨 Advanced Patterns

### Pattern 1: Multi-Shell Support

```yaml
name: 'Cross-Platform Action'
description: 'Works on Linux, Windows, and macOS'

runs:
  using: 'composite'
  steps:
    - name: Linux/macOS Step
      if: runner.os != 'Windows'
      shell: bash
      run: echo "Running on Unix-like system"
    
    - name: Windows Step
      if: runner.os == 'Windows'
      shell: pwsh
      run: Write-Host "Running on Windows"
```

### Pattern 2: Environment Variables

```yaml
runs:
  using: 'composite'
  steps:
    - name: Set environment
      shell: bash
      run: |
        echo "CUSTOM_VAR=my-value" >> $GITHUB_ENV
        echo "PATH=/custom/path:$PATH" >> $GITHUB_ENV
    
    - name: Use environment
      shell: bash
      run: echo "Using: $CUSTOM_VAR"
```

### Pattern 3: File Processing

```yaml
runs:
  using: 'composite'
  steps:
    - name: Process files
      shell: bash
      run: |
        for file in ${{ inputs.file-pattern }}; do
          echo "Processing: $file"
          # Process each file
        done
```

### Pattern 4: Caching

```yaml
runs:
  using: 'composite'
  steps:
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache
        key: ${{ runner.os }}-cache-${{ hashFiles('**/package-lock.json') }}
    
    - name: Install dependencies
      shell: bash
      run: npm install
```

---

## 🔒 Security Best Practices

✅ **Do:**
- Validate all inputs
- Use `secrets` for sensitive data
- Pin action versions with SHA
- Avoid logging secrets
- Use least privilege

```yaml
steps:
  - name: Use secret safely
    shell: bash
    env:
      SECRET_VALUE: ${{ inputs.secret-input }}
    run: |
      # Use $SECRET_VALUE instead of ${{ inputs.secret-input }}
      # This prevents secrets from appearing in logs
      echo "Processing with secret..."
```

❌ **Don't:**
```yaml
# DON'T: This logs the secret!
run: echo "Secret is ${{ inputs.secret-input }}"

# DON'T: Hardcode sensitive values
run: |
  PASSWORD="hardcoded-password"
```

---

## 🛠️ Troubleshooting

### Common Issues

**Issue 1: Action not found**
```
Error: Unable to resolve action ./.github/actions/my-action
```
**Solution:** Ensure checkout action runs first
```yaml
steps:
  - uses: actions/checkout@v4  # Required first!
  - uses: ./.github/actions/my-action
```

**Issue 2: Output not available**
```yaml
# Wrong: Missing step ID
- name: Generate output
  shell: bash
  run: echo "result=value" >> $GITHUB_OUTPUT

# Correct: Use step ID
- name: Generate output
  id: generate
  shell: bash
  run: echo "result=value" >> $GITHUB_OUTPUT

# Reference it correctly
outputs:
  result:
    value: ${{ steps.generate.outputs.result }}
```

**Issue 3: Shell not available**
```
Error: Required shell 'bash' is not available
```
**Solution:** Use appropriate shell for OS
```yaml
- name: Cross-platform command
  shell: bash
  run: |
    if [[ "$RUNNER_OS" == "Windows" ]]; then
      # Windows-specific code
    else
      # Unix-specific code
    fi
```

---

## 📊 Performance Optimization

### Minimize Checkout Operations

```yaml
# Bad: Multiple checkouts
- uses: actions/checkout@v4
- uses: ./.github/actions/action1
- uses: actions/checkout@v4
- uses: ./.github/actions/action2

# Good: Single checkout
- uses: actions/checkout@v4
- uses: ./.github/actions/action1
- uses: ./.github/actions/action2
```

### Use Caching

```yaml
runs:
  using: 'composite'
  steps:
    - name: Cache build
      uses: actions/cache@v3
      with:
        path: build/
        key: build-${{ hashFiles('src/**') }}
    
    - name: Build (cached)
      shell: bash
      run: |
        if [ -d "build" ]; then
          echo "Using cached build"
        else
          npm run build
        fi
```

### Parallel Execution (Within Limits)

```yaml
runs:
  using: 'composite'
  steps:
    - name: Run parallel tasks
      shell: bash
      run: |
        task1 &
        task2 &
        task3 &
        wait
        echo "All tasks completed"
```

---

## 📚 Documentation Template

Create a README.md for each action:

````markdown
# Action Name

## Description
Brief description of what this action does.

## Inputs
| Name | Description | Required | Default |
|------|-------------|----------|---------|
| input-1 | Description | Yes | - |
| input-2 | Description | No | `default` |

## Outputs
| Name | Description |
|------|-------------|
| output-1 | Description |

## Usage

```yaml
- uses: ./.github/actions/my-action
  with:
    input-1: value
    input-2: value
```

## Examples

### Example 1: Basic Usage
```yaml
steps:
  - uses: ./.github/actions/my-action
    with:
      input-1: test
```

### Example 2: With Outputs
```yaml
steps:
  - uses: ./.github/actions/my-action
    id: my-step
  - run: echo "${{ steps.my-step.outputs.output-1 }}"
```

## Development
...
````

---

## 🎓 Learning Path

### Beginner Level
1. Create simple action with 1-2 steps
2. Use basic inputs (no outputs)
3. Test in local workflow
4. Add error messages

### Intermediate Level
1. Add outputs
2. Use multiple shell types
3. Implement error handling
4. Add validation logic

### Advanced Level
1. Multi-platform support
2. Complex input/output handling
3. Performance optimization
4. Security hardening
5. Comprehensive documentation

---

## ✨ Summary

Composite actions are simple but powerful:
- **Create** a folder in `.github/actions/`
- **Define** inputs, outputs, and steps in `action.yml`
- **Use** them in your workflows with `uses:` keyword
- **Reuse** across multiple workflows in your repo
- **Test** thoroughly with different inputs
- **Document** clearly for maintainability
- **Secure** by validating inputs and protecting secrets
- **Optimize** for performance and reliability

Keep them small, focused, and well-documented!
