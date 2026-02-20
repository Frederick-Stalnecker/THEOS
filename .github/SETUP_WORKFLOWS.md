# Setting Up GitHub Actions Workflows for THEOS

This guide explains how to enable GitHub Actions workflows for THEOS. Due to GitHub's security policies, workflow files need to be created through the GitHub UI or with proper permissions.

## Quick Setup (Recommended)

### Option 1: Using GitHub Web UI (Easiest)

1. **Go to GitHub Repository**
   - Navigate to https://github.com/Frederick-Stalnecker/THEOS
   - Click "Actions" tab

2. **Create New Workflow**
   - Click "New workflow"
   - Click "set up a workflow yourself"
   - Name it `tests.yml`

3. **Copy Workflow Content**
   - Copy the content from `workflow-templates/tests.yml` (provided below)
   - Paste into the editor
   - Click "Commit changes"

4. **Repeat for Other Workflows**
   - Create `code-quality.yml`
   - Create `release.yml`

### Option 2: Using GitHub CLI

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com

# Authenticate
gh auth login

# Create workflows
gh workflow enable tests.yml
gh workflow enable code-quality.yml
gh workflow enable release.yml
```

## Workflow Files

### 1. tests.yml - Main Test Suite

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 2 * * *'

jobs:
  test:
    name: Test Suite (Python ${{ matrix.python-version }})
    runs-on: ${{ matrix.os }}
    
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
        exclude:
          - os: macos-latest
            python-version: '3.8'
          - os: macos-latest
            python-version: '3.9'
          - os: windows-latest
            python-version: '3.8'
          - os: windows-latest
            python-version: '3.9'
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest pytest-cov pytest-timeout
          pip install -r requirements.txt
      
      - name: Run unit tests
        run: pytest tests/test_governor.py -v --tb=short --timeout=10
      
      - name: Run all tests with coverage
        run: pytest tests/ -v --tb=short --timeout=10 --cov=code --cov-report=xml
      
      - name: Test examples
        run: |
          python examples/medical_ethics.py > /dev/null 2>&1 && echo "✓ medical_ethics.py"
          python examples/ai_safety.py > /dev/null 2>&1 && echo "✓ ai_safety.py"
          python examples/financial_decision.py > /dev/null 2>&1 && echo "✓ financial_decision.py"
      
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: false
```

### 2. code-quality.yml - Code Quality Checks

```yaml
name: Code Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  linting:
    name: Code Linting
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install tools
        run: |
          python -m pip install --upgrade pip
          pip install flake8 pylint black isort
      
      - name: Check formatting
        run: black --check code/ tests/ examples/
      
      - name: Check imports
        run: isort --check-only code/ tests/ examples/
      
      - name: Lint
        run: flake8 code/ --max-line-length=120 --exit-zero
```

### 3. release.yml - Release Management

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  validate:
    name: Validate Release
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest
          pip install -r requirements.txt
      
      - name: Run tests
        run: pytest tests/ -v --tb=short
      
      - name: Test examples
        run: |
          python examples/medical_ethics.py > /dev/null 2>&1
          python examples/ai_safety.py > /dev/null 2>&1
          python examples/financial_decision.py > /dev/null 2>&1
  
  create-release:
    name: Create Release
    runs-on: ubuntu-latest
    needs: validate
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body: |
            # THEOS Release ${{ github.ref }}
            
            See [GETTING_STARTED.md](GETTING_STARTED.md) for installation and usage.
          draft: false
          prerelease: false
```

## Enabling Workflows in GitHub UI

### Step-by-Step Instructions

1. **Go to Repository**
   - Visit https://github.com/Frederick-Stalnecker/THEOS

2. **Click "Actions" Tab**
   - Top navigation bar

3. **Click "New workflow"**
   - Right side of page

4. **Click "set up a workflow yourself"**
   - Creates a blank workflow file

5. **Name the File**
   - Replace "main.yml" with "tests.yml"

6. **Paste Workflow Content**
   - Copy from above and paste into editor

7. **Review and Commit**
   - Click "Commit changes"
   - Add commit message
   - Commit to main branch

8. **Repeat for Other Workflows**
   - Create `code-quality.yml`
   - Create `release.yml`

## Verifying Workflows

### Check Workflow Status

1. Go to "Actions" tab
2. View workflow runs
3. Click on specific run for details

### Add Status Badges

Add to README.md:

```markdown
[![Tests](https://github.com/Frederick-Stalnecker/THEOS/workflows/Tests/badge.svg)](https://github.com/Frederick-Stalnecker/THEOS/actions/workflows/tests.yml)
[![Code Quality](https://github.com/Frederick-Stalnecker/THEOS/workflows/Code%20Quality/badge.svg)](https://github.com/Frederick-Stalnecker/THEOS/actions/workflows/code-quality.yml)
```

## Troubleshooting

### Workflows Not Running

1. Check branch name (must be main or develop)
2. Check file syntax (YAML)
3. Check trigger conditions
4. Manually trigger workflow

### Permission Errors

If you see "refusing to allow a GitHub App to create or update workflow":

1. Go to Settings → Actions → General
2. Ensure "Allow GitHub Actions to create and approve pull requests" is enabled
3. Ensure "Workflow permissions" includes "Read and write permissions"

### Test Failures

1. Check workflow logs
2. Run tests locally
3. Fix issues
4. Push changes
5. Workflow re-runs automatically

## Next Steps

1. **Enable Workflows** - Follow instructions above
2. **Configure Codecov** (optional)
   - Sign up at https://codecov.io
   - Add repository
   - Workflows will automatically upload coverage
3. **Monitor Workflows**
   - Check "Actions" tab regularly
   - Review logs for issues
4. **Update Documentation**
   - Add status badges to README
   - Document any custom configurations

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Codecov Documentation](https://docs.codecov.io/)

## Support

For issues with workflows:

1. Check this guide
2. Review GitHub Actions documentation
3. Check workflow logs in "Actions" tab
4. Open issue with error details

---

**Status:** Ready for manual setup ✅  
**Last Updated:** February 19, 2026
