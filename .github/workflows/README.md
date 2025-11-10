# GitHub Actions Workflows

This directory contains CI/CD workflows for the Xseller.ai automation platform.

## Workflows

### 1. Full Stack CI (`ci.yml`)
**Triggers:** Push or Pull Request to main/master/terminal branches

This is the main workflow that runs comprehensive checks on both backend and frontend:
- **Backend Job:**
  - Sets up Python 3.11
  - Installs dependencies
  - Runs flake8 linting
  - Checks code formatting with black
  - Runs pytest with coverage
  - Validates FastAPI app structure

- **Frontend Job:**
  - Sets up Node.js 18
  - Installs npm dependencies
  - Runs ESLint
  - Performs TypeScript type checking
  - Builds the Next.js application
  - Runs tests if available

- **Integration Job:**
  - Runs after both backend and frontend jobs complete
  - Validates overall integration

### 2. Backend CI (`backend-ci.yml`)
**Triggers:** Push or Pull Request to main/master/terminal branches (only when backend files change)

Focused workflow that runs only when backend code changes:
- Python linting and formatting checks
- Pytest with coverage reporting
- FastAPI app validation

### 3. Frontend CI (`frontend-ci.yml`)
**Triggers:** Push or Pull Request to main/master/terminal branches (only when frontend files change)

Focused workflow that runs only when frontend code changes:
- ESLint checks
- TypeScript type checking
- Next.js build validation
- Test execution if available

## Features

- **Caching:** Uses pip cache for Python and npm cache for Node.js to speed up builds
- **Path Filtering:** Backend and frontend workflows only run when relevant files change
- **Continue on Error:** Some steps continue even if they fail (tests, type checking) to provide full feedback
- **Multiple Python/Node Versions:** Currently set to Python 3.11 and Node.js 18

## Usage

These workflows run automatically on:
- Push to main, master, or terminal branches
- Pull requests targeting main, master, or terminal branches

You can also manually trigger workflows from the Actions tab in GitHub.

## Local Development

To run checks locally before pushing:

### Backend
```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black
flake8 .
black --check .
pytest --cov=app
```

### Frontend
```bash
cd frontend
npm ci
npm run lint
npx tsc --noEmit
npm run build
```
