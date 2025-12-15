# Playwright-Enterprise-Framework

Production-ready Python + Playwright + Pytest automation framework showcasing Page Object Model (POM), API-based authentication bypass, and parallel execution at scale.

## Highlights
- **API login bypass**: Session-wide authenticated `storageState` generated via API. Parallel-safe per worker.
- **Page Object Model**: Clean separation of test logic from UI interactions.
- **Parallel execution**: Scales with `pytest-xdist` using unique storage files per worker. Defaults to 2 workers.
- **Config via env vars**: No secrets in code. Easily switch environments.
- **Integrated Test Product**: Includes a local Angular UI and Node.js API for full-stack testing.

## Test Design Patterns (Interview Notes)

### Architecture / Patterns
- **Page Object Model (POM)**
  - UI interactions are encapsulated in Page Objects under `PlayWrightTest/pages/`.
  - Tests call higher-level Page methods instead of low-level selectors, improving readability and maintainability.

- **Fixture-driven test composition (Pytest)**
  - Shared setup is centralized in `PlayWrightTest/conftest.py`.
  - Examples: authenticated API context (`api_context`), authenticated UI page (`auth_page`), test data factories (e.g. `new_client`).

- **Arrange / Act / Assert with explicit step logging**
  - Tests follow a clear flow with meaningful checkpoints using the `step(...)` context manager (`PlayWrightTest/utils/step.py`).
  - Step history is attached to the HTML report via `pytest-html` to make failures easier to diagnose.

### Stability & Maintainability Techniques
- **Environment-based configuration**
  - URLs/credentials are read from environment variables (`PlayWrightTest/config/settings.py`) so the same suite can run locally and in CI.
- **Single source of truth for base URLs**
  - Tests reference `BASE_URL`/`UI_BASE_URL` instead of hardcoded endpoints to avoid CI/local drift.

## Performance Techniques (How the suite runs fast)

- **API-based authentication bypass (no UI login)**
  - Authentication is performed via API (`POST /login`) and injected into the browser context.
  - This removes the slowest UI step from most tests and reduces flake.

- **Reusing authenticated storageState per worker**
  - A per-worker `storageState-<worker>.json` is created once and reused across tests.
  - Enables safe parallel execution without session collisions.

- **Session-scoped browser instance**
  - A single Browser is launched per test session, while each test uses a fresh Context/Page.
  - This reduces startup overhead while keeping isolation.

- **Parallel execution with pytest-xdist**
  - Runs with multiple workers (default configured in `pytest.ini`).
  - Combined with per-worker storageState, this improves throughput safely.

- **Lightweight test data creation/cleanup**
  - Tests create their own data (API CRUD) and attempt best-effort cleanup in fixtures.
  - Reduces inter-test coupling and makes reruns predictable.

## Directory Structure
```text
Playwright-Enterprise-Framework/
├─ PlayWrightTest/
│  ├─ config/                  # Configuration settings (URLs, creds)
│  ├─ pages/                   # Page Object Models (POM)
│  ├─ tests/                   # Pytest test suites
│  │  ├─ test_testproduct_api.py   # Basic API tests
│  │  ├─ test_testproduct_ui.py    # UI tests with auth bypass
│  │  └─ test_api_extended.py      # Extended API validation tests
│  ├─ utils/                   # Helper utilities
│  ├─ conftest.py              # Shared fixtures (auth, browser)
│  └─ pytest.ini               # Pytest configuration (markers, defaults)
├─ TestProduct/
│  ├─ API/                     # Node.js/Express Backend API
│  └─ UI/                      # Angular 17+ Frontend
├─ requirements.txt            # Python dependencies
└─ README.md
```

## Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm 9+**
- **Browsers** installed for Playwright

---

## 1. Backend API (TestProduct/API)
A simple REST API using JSON-file storage.

### Setup & Run
```bash
cd TestProduct/API
npm install
npm run dev
# Server starts at http://localhost:8000 (PORT can be overridden)
```
*Note: Data is stored in `data.json`. Delete this file to reset the database.*

Notes
- Dev server is configured not to restart on `data.json`/`token.json` writes to avoid interrupting tests.
- API supports JWT auth at `POST /login` and CRUD at `/clients`.

---

## 2. Frontend UI (TestProduct/UI)
Angular Client Management System.

### Features
- **Client List**: View all clients (Admin) or own clients (User).
- **Actions**: Update client details via iframe; Delete client directly from the list.
- **User Info**: Displays "Hi <username>" next to the Logout button.

### Setup & Run
```bash
cd TestProduct/UI
npm install
npm start
# App opens at http://localhost:4200
```

---

## 3. Playwright Tests (PlayWrightTest)
Automated test suite covering API and UI workflows.

### Setup
```bash
cd PlayWrightTest
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 -m playwright install
```

### Configuration (`pytest.ini`)
The project is configured to run with **2 parallel workers** and **Chromium** by default.
```ini
[pytest]
addopts = -q -s --maxfail=1 -n 2 --browser chromium
```

### Running Tests
Ensure both API and UI are running before starting tests.

**Run All Tests (Default):**
```bash
pytest
```
*Runs with 2 workers in parallel using Chromium.*

**HTML Report:**
```bash
pytest --html=report.html
```

**Run Specific Suites:**
```bash
# UI Tests only
pytest -m ui

# API Tests only
pytest -m api

# Extended API Validation
pytest -k extended
```

**Custom Execution:**
```bash
# Run with header (visible browser)
pytest --headed

# Run with more workers
pytest -n 4
```

## Test Suites Overview

### UI Tests (`test_testproduct_ui.py`)
- **Login Bypass**: Uses API to inject auth state, skipping the login page UI.
- **CRUD Operations**: Verifies creating, updating, and deleting clients.
- **User Interface**: Checks for dashboard visibility and user greeting ("Hi user1").

Global Fixtures
- Session and per-test setup/teardown run automatically (autouse) and log start/finish to the console.

### API Tests (`test_testproduct_api.py`, `test_api_extended.py`)
- **Health Check**: Verifies API status.
- **Auth**: Tests login and token generation.
- **Validation**: Verifies error handling for missing fields, invalid data types, and unauthorized access.

Duplicates
- A legacy CRUD test (`tests/test_api_crud.py`) is marked skipped to avoid duplication with `tests/test_api_clients_crud.py`.

## Continuous Integration (GitHub Actions)
The project includes a pre-configured GitHub Actions workflow located in `.github/workflows/test.yml`. This workflow automatically runs all tests on every Pull Request and push to the `main` or `master` branches.

### Workflow Steps
1. **Setup**: Installs Node.js (for App) and Python (for Tests).
2. **Start Services**:
   - Launches the **API** on port 3001.
   - Launches the **Angular UI** on port 4200.
3. **Install Dependencies**: Installs Python packages and Playwright browsers.
4. **Wait for Readiness**: Polls the API health endpoint and UI URL until they are up.
5. **Run Tests**: Executes `pytest` with HTML reporting enabled.
6. **Artifacts**: Uploads the `report.html` as a workflow artifact for review.

### Viewing Test Results in CI
1. Go to the **Actions** tab in your GitHub repository.
2. Click on the latest workflow run.
3. Scroll down to the **Artifacts** section.
4. Download **playwright-report** to view the detailed HTML test report.
