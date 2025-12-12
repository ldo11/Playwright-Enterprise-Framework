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
- `/dashboard` client list with role-based filtering (Admin sees all; User sees only theirs).
- "Add Client" dialog to create a new client.

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

A REST API is provided under `Testproduct/API` using Express, MSSQL, JWT auth, and CORS for the Angular UI.

### Prerequisites
- Node.js 18+ and npm 9+
- SQL Server running locally with database `ClientManagementDB`
  - Tables: `Users(UserID, Username, PasswordHash, Role)` and `Clients(ClientID, FirstName, LastName, DOB, Sex, CreatedByUserID)`
- If using Windows Authentication, run on Windows with `msnodesqlv8`; otherwise use SQL Login (`tedious`).

### Environment setup
Create `Testproduct/API/.env` and configure one of the following:

Option A: SQL Login (cross-platform)
```ini
PORT=8000
CORS_ORIGIN=http://localhost:4200
JWT_SECRET=change_this_in_production
DB_DRIVER=tedious
DB_HOST=localhost
DB_NAME=ClientManagementDB
DB_USER=your_sql_user
DB_PASSWORD=your_sql_password
DB_PORT=1433
```

Option B: Windows Auth (Windows only)
```ini
PORT=8000
CORS_ORIGIN=http://localhost:4200
JWT_SECRET=change_this_in_production
DB_DRIVER=msnodesqlv8
DB_CONNECTION_STRING=server=localhost;Database=ClientManagementDB;Trusted_Connection=Yes;Driver={SQL Server Native Client 11.0}
```

### Install and run
```bash
cd Testproduct/API
npm install
npm run dev   # nodemon
# or
npm start     # node server.js
```
Server starts at: http://localhost:8000

### Seed a user (generate bcrypt hash)
```bash
node -e "require('bcryptjs').hash('YourPassword123', 10).then(h=>console.log(h))"
# Insert into Users table with the printed hash
```

### Endpoints
- POST `/api/login` (also `/login`)
  - Body: `{ "username": "...", "password": "..." }`
  - Response: `{ token, user: { userId, username, role } }`
- GET `/api/clients` (also `/clients`)
  - Header: `Authorization: Bearer <token>`
  - Admin role -> returns all. User role -> returns only own clients.
  - Optional: `?mine=true` to force own clients
- POST `/api/clients` (also `/clients`)
  - Header: `Authorization: Bearer <token>`
  - Body: `{ firstName, lastName, dob: "yyyy-mm-dd", sex: "Male|Female|N/A" }`
  - Automatically sets `CreatedByUserID` from the JWT.

### Common issues
- Connection errors: validate `.env` DB settings and that SQL Server is reachable on port 1433.
- Login fails: ensure `Users.PasswordHash` contains a bcrypt hash of the provided password.
- CORS errors from UI: ensure `CORS_ORIGIN` matches the Angular dev origin (http://localhost:4200).

