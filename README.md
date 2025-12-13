# Playwright-Enterprise-Framework

Production-ready Python + Playwright + Pytest automation framework showcasing Page Object Model (POM), API-based authentication bypass, and parallel execution at scale.

## Highlights
- **API login bypass**: Session-wide authenticated `storageState` generated via API. Parallel-safe per worker.
- **Page Object Model**: Clean separation of test logic from UI interactions.
- **Parallel execution**: Scales with `pytest-xdist` using unique storage files per worker.
- **Config via env vars**: No secrets in code. Easily switch environments.
- **Actionable fixtures**: `auth_page`, `auth_context`, `session_browser` for fast, stable tests.

## Directory Structure
```text
Playwright-Enterprise-Framework/
├─ conftest.py                  # Core fixtures: browser lifecycle, API login bypass, pre-auth context/page
├─ pytest.ini                   # Pytest config: markers, defaults, discovery
├─ requirements.txt             # Python dependencies
├─ pages/
│  └─ home_page.py              # Sample POM for authenticated area
├─ tests/
│  └─ test_login_bypass.py      # Example test starting already authenticated
├─ utils/
│  └─ auth.py                   # Utilities to build storageState via API or token
├─ config/
│  └─ settings.py               # Base URLs, API path, cookie settings, env keys
└─ README.md

# Created at runtime (not committed):
.auth/                          # Per-worker storageState files (e.g., storageState-gw0.json)
```

## Requirements
- Python 3.10–3.12
- macOS/Linux/Windows
- Browsers installed for Playwright

## Setup
```bash
# 1) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2) Install Python dependencies
pip install -r requirements.txt

# 3) Install Playwright browsers
python -m playwright install       # Linux CI may also need: python -m playwright install-deps
```

## Configuration (Environment Variables)
Set the following to target the demo app/API and authenticate without UI:
- `DEMO_BASE_URL` (default: `https://practice.expandtesting.com`)
- `DEMO_APP_URL` (default: `${DEMO_BASE_URL}/notes/app`)
- `DEMO_LOGIN_API_PATH` (default: `/notes/api/auth/login`)
- `DEMO_AUTH_COOKIE_NAME` (default: `token`)
- `DEMO_COOKIE_DOMAIN` (default: `practice.expandtesting.com`)

Authentication options (pick one):
- `DEMO_EMAIL` and `DEMO_PASSWORD` for API login
- or `DEMO_JWT` to synthesize the cookie directly

Example (macOS/Linux):
```bash
export DEMO_EMAIL="your_email@example.com"
export DEMO_PASSWORD="your_password"
# Optional overrides:
# export DEMO_BASE_URL="https://practice.expandtesting.com"
```

## How It Works: API Login Bypass
1. On first use per worker, `conftest.py` calls the demo API login endpoint.
2. If a Set-Cookie is returned, it is captured and persisted to `.auth/storageState-<worker>.json`.
3. If the API returns a token (no cookie), we synthesize a valid `storageState` with the configured cookie name/domain.
4. Tests use a new `BrowserContext` seeded with that `storageState`, starting already logged in.

Fixtures of interest:
- `session_browser` (scope=session): Launches the browser once for the run.
- `auth_storage_path` (scope=session): Builds/returns per-worker storage state path.
- `auth_context`: `new_context(storage_state=...)` for pre-authenticated context.
- `auth_page`: Convenience wrapper returning a pre-authenticated page.

## Running Tests
Basic run (uses pytest.ini defaults):
```bash
pytest
```

Target a specific test or marker:
```bash
pytest -k login_bypass
pytest -m smoke
```

Choose browser and headed mode (via pytest-playwright):
```bash
pytest --browser chromium         # chromium|firefox|webkit
pytest --browser webkit --headed
```

Parallel execution with per-worker sessions:
```bash
pytest -n auto                    # or -n 4
```

HTML report (pytest-html):
```bash
mkdir -p reports
pytest --html=reports/report.html --self-contained-html
```

Run everything together:
```bash
pytest -n auto --browser chromium --html=reports/report.html --self-contained-html
```

## Example Test Flow
- `tests/test_login_bypass.py` opens the app using `auth_page` and asserts the authenticated UI via the `HomePage` POM.
- `pages/home_page.py` encapsulates locators and interactions for the authenticated area.

## Extending the Framework
- Add new POMs under `pages/` and import them in tests.
- Group tests by feature under `tests/` and apply `@pytest.mark.<marker>`.
- Add your own fixtures in `conftest.py` or per-package `conftest.py` files.
- Configure additional CLI defaults or markers in `pytest.ini`.

## CI/CD Notes
- Install browsers in CI: `python -m playwright install` (Linux may need `install-deps`).
- Provide `DEMO_EMAIL`/`DEMO_PASSWORD` (or `DEMO_JWT`) as secure CI secrets.
- Enable parallelism: `pytest -n auto`.
- Cache `.venv` and `~/.cache/ms-playwright` for speed when possible.

## Troubleshooting
- "API login bypass failed": Ensure credentials (or JWT) are set and the API is reachable.
- "No cookies in storageState": Your API may return a token only; the framework synthesizes the cookie automatically if token fields are present.
- Certificate/network issues: The request context ignores HTTPS errors; ensure your network/Proxy allows the call.
- Playwright not found: Re-run `pip install -r requirements.txt` and `python -m playwright install`.

## Why This Is Production-Ready
- Stable, fast tests by avoiding UI login.
- Parallel-safe session management via worker-specific storage files.
- Clear layering (tests → POM → fixtures/utils → config).
- Minimal global state and easily configurable environments.

---
Maintained for demonstration and portfolio purposes. Replace the demo app endpoints with your target system by adjusting `config/settings.py` and environment variables.

## Frontend (Angular) - Local Development

This repo also includes a sample Angular 17+ frontend scaffold for a Client Management System under `Testproduct/UI` using standalone components, Angular Material, and an HTTP interceptor.

### Prerequisites
- Node.js 18+ (recommended LTS)
- npm 9+
- Angular CLI (optional but recommended): `npm i -g @angular/cli`
- Backend API running at `http://localhost:8000` with endpoints:
  - `POST /login` -> returns `{ token }` or `{ access_token }`
  - `GET /clients` -> all clients (admin), or own clients when `?mine=true`
  - `POST /clients` -> create client

### Install dependencies
```bash
cd Testproduct/UI
npm install
```

If Angular CLI is not installed globally, you can still use the `ng` binary from `node_modules/.bin` via npm scripts (e.g., `npm start`).

### Start the dev server
```bash
# From Testproduct/UI
npm start
# Opens http://localhost:4200
```

The app provides:
- `/login` page to authenticate and store the JWT token in `localStorage`.
- `/dashboard` client list ("Client List" toolbar) with role-based filtering (Admin sees all; User sees only their own).
- "Add Client" dialog to create a new client.
- Ability to click a client's first name to open a detail dialog where you can view and edit client info.

### Configuration notes
- API base URL is set in `src/app/services/client.service.ts` as `http://localhost:8000`.
  - Adjust this if your API runs elsewhere.
- Auth header is attached by `src/app/interceptors/auth.interceptor.ts` as `Authorization: Bearer <token>`.
- JWT role detection is parsed from the token payload (`role` or `roles[0]`). Adjust if your token differs.

### Angular Material & icons
- Material theme is imported in `src/styles.css`.
- To enable icons, add this to `<head>` in `src/index.html` if not present:
```html
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet" />
```

### Common issues
- CORS errors: Enable CORS on the backend for origin `http://localhost:4200`. Alternatively, configure a proxy:
  - Create `proxy.conf.json` in `Testproduct/UI` with:
    ```json
    { 
      "/api": { "target": "http://localhost:8000", "secure": false, "changeOrigin": true, "pathRewrite": { "^/api": "" } }
    }
    ```
  - Update API calls to use `/api` base path, and start with: `ng serve --proxy-config proxy.conf.json`
- 401/403 responses: Ensure `localStorage.token` is set after login and the interceptor is wired (see `main.ts`).
- Missing packages: Run `npm install` inside `Testproduct/UI`.

### Useful scripts
- `npm start` -> `ng serve` dev server
- `npm run build` -> Production build in `dist/`


## Backend API (Node.js/Express) - Local Development

A REST API is provided under `TestProduct/API` using Express, JWT auth, CORS for the Angular UI, and **JSON-file storage** (no external database).

### Prerequisites
- Node.js 18+ and npm 9+

### Data storage
- The API stores users and clients in `TestProduct/API/data.json`.
- On first start, if the file does not exist, it is created automatically with:
  - One default user: `user1` / `123456` (role: `Admin`).
  - An empty `clients` array.
- `data.json` is git-ignored and safe to delete between runs if you want a clean state.

### Install and run
```bash
cd TestProduct/API
npm install
npm run dev   # nodemon
# or
npm start     # node server.js
```
Server starts at: http://localhost:8000

### Endpoints
- POST `/login` (also `/api/login`)
  - Body: `{ "username": "user1", "password": "123456" }` (by default)
  - Response: `{ token, user: { userId, username, role } }`
- GET `/clients` (also `/api/clients`)
  - Header: `Authorization: Bearer <token>`
  - Admin role -> returns all clients.
  - User role -> returns only clients where `createdByUserId` matches the current user.
  - Optional: `?mine=true` to force only own clients.
- POST `/clients` (also `/api/clients`)
  - Header: `Authorization: Bearer <token>`
  - Body: `{ firstName, lastName, dob: "yyyy-mm-dd", sex: "Male|Female|N/A" }`
  - Automatically sets `createdByUserId` from the JWT.
- GET `/clients/:id` (also `/api/clients/:id`)
  - Header: `Authorization: Bearer <token>`
  - Returns a single client if the user is Admin or the creator of that client.
- PUT `/clients/:id` (also `/api/clients/:id`)
  - Header: `Authorization: Bearer <token>`
  - Body: `{ firstName, lastName, dob: "yyyy-mm-dd", sex: "Male|Female|N/A" }`
  - Updates an existing client (Admin can edit any client; non-admins can edit only their own).

### Swagger API documentation
- When the backend is running (default `http://localhost:8000`),
  open `http://localhost:8000/api-docs` in your browser to view the
  Swagger UI for the API.

### Common issues
- Port already in use: ensure nothing else is running on `8000`.
- CORS errors from UI: ensure `CORS_ORIGIN` in `server.js` (or `.env`) matches the Angular dev origin (`http://localhost:4200`).

### Backend API tests (Jest)
- Tests live under `TestProduct/API/tests` and currently cover:
  - `POST /login` with username `user1` and password `123456` against the JSON store.
- Run tests:
  ```bash
  cd TestProduct/API
  npm install
  npm test
  ```

## TestProduct Playwright Tests (Python)

Under `PlayWrightTest/` there is a Python + Playwright + Pytest test harness. It has been configured to target the local TestProduct API and Angular UI.

### Configuration for TestProduct
- Config file: `PlayWrightTest/config/settings.py`
  - `BASE_URL`: TestProduct API base URL (default: `http://localhost:8000`).
  - `UI_BASE_URL`: Angular UI base URL (default: `http://localhost:4200`).
  - `APP_URL`: Dashboard URL (default: `http://localhost:4200/dashboard`).
  - `LOGIN_API_PATH`: API login path (default: `/login`).
  - `API_USERNAME` / `API_PASSWORD`: default to `user1` / `123456`.

### API suite
- File: `PlayWrightTest/tests/test_testproduct_api.py`
- Marked with `@pytest.mark.api`.
- Covers:
  - `GET /health` on the API.
  - `POST /login` and `GET /clients` using the JSON store.

### UI suite (pre-authenticated via API)
- File: `PlayWrightTest/tests/test_testproduct_ui.py`
- Marked with `@pytest.mark.ui`.
- Uses the existing fixtures in `PlayWrightTest/conftest.py`:
  - `auth_storage_path` (session-scoped, per worker):
    - Logs in once via the TestProduct API using `API_USERNAME`/`API_PASSWORD`.
    - Writes a Playwright `storageState` JSON that seeds `localStorage['token']` for the Angular origin.
  - `auth_context` / `auth_page`: start each test with a pre-authenticated Playwright context/page.
- POM: `PlayWrightTest/pages/home_page.py` represents the TestProduct dashboard (Client List).
- Tests:
  - Verify the Client List dashboard is visible when using the pre-authenticated storage state.
  - Create a client via the UI and confirm its first name appears as a clickable entry.

### Running the Playwright tests
```bash
cd PlayWrightTest
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Ensure TestProduct API and UI are running locally first:
# - API:    cd TestProduct/API && npm run dev
# - UI:     cd TestProduct/UI  && npm start

# Run only TestProduct API tests
pytest -m api

# Run only TestProduct UI tests with 4 parallel workers (each worker logs in via API once)
pytest -m ui -n 4 --browser chromium

# Run everything (all suites)
pytest -n 4 --browser chromium
```

