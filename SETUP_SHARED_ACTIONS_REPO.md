# How to Create a Shared Composite Actions Repository

This guide shows how to create a SEPARATE repository for shared composite actions.

## Step 1: Create New Repository on GitHub

```
Repository Name: github-actions
Visibility: Internal or Public
Description: Shared GitHub Actions and Composite Actions
```

## Step 2: Clone and Setup

```bash
git clone https://github.com/charan3844/github-actions.git
cd github-actions
```

## Step 3: Create Folder Structure

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
└── LICENSE
```

## Step 4: Copy Composite Actions

Copy all `action.yml` files from this repo:
```
docker/.github/actions/* → github-actions/.github/actions/*
```

## Step 5: Usage from Other Repos

In any repo (docker, api-service, ml-model, etc.):

```yaml
# .github/workflows/build.yml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: charan3844/github-actions/.github/actions/acr-login@main
      - uses: charan3844/github-actions/.github/actions/backup-tag@main
      - uses: charan3844/github-actions/.github/actions/build-docker-image@main
      - uses: charan3844/github-actions/.github/actions/push-docker-image@main
      - uses: charan3844/github-actions/.github/actions/cleanup-old-tags@main
      - uses: charan3844/github-actions/.github/actions/update-aca@main
```

## Step 6: Versioning

Tag releases in github-actions repo:
```bash
git tag v1.0.0
git push origin v1.0.0
```

Then reference specific versions:
```yaml
- uses: charan3844/github-actions/.github/actions/acr-login@v1.0.0
```

Or use `main` branch (latest):
```yaml
- uses: charan3844/github-actions/.github/actions/acr-login@main
```

## Reference Architecture

```
charan3844/github-actions (shared repo)
├── .github/actions/
│   └── [All composite actions here]

charan3844/docker (this repo)
├── Uses: charan3844/github-actions@main

charan3844/api-service
├── Uses: charan3844/github-actions@main

charan3844/ml-model
├── Uses: charan3844/github-actions@main
```

---

## Current Status

✅ **docker repo** - Has local composite actions (working now)
⏳ **github-actions repo** - Create when you need it

## When to Create Shared Repo

- When 2+ repos need same actions
- When multiple teams use GitHub Actions
- For organization standardization
- For easy maintenance and versioning

## Setup Instructions

1. Create `github-actions` repo on GitHub
2. Copy structure from above
3. Copy all `.github/actions/` from docker repo
4. Push to github-actions repo
5. Reference from docker and other repos
