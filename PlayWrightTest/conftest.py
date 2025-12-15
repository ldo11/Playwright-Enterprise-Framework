from __future__ import annotations

# Core Pytest and typing
import os

import json

from pathlib import Path
from typing import Generator, Optional

import pytest

# Playwright sync API (used by pytest-playwright under the hood)
from playwright.sync_api import (
    APIRequestContext,
    Browser,
    BrowserContext,
    Page,
    Playwright,
)

# Local settings and helpers
from config.settings import (
    APP_URL,
    BASE_URL,
    LOGIN_API_PATH,
    AUTH_COOKIE_NAME,
    COOKIE_DOMAIN,
    API_USERNAME,
    API_PASSWORD,

    UI_BASE_URL,

)
from utils.auth import create_authenticated_storage_state
from utils.step import current_steps


# -------------------------------
# Reporting & Step Tracking
# -------------------------------
@pytest.fixture(autouse=True)
def reset_step_history():
    """
    Reset the step history before each test runs.
    This ensures that steps from previous tests do not leak into the current one.
    """
    current_steps.clear()
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to add test steps to the HTML report.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        # Only add steps if we have them and it's the main call phase
        if current_steps:
            # Construct HTML table for steps
            # We use inline styles for simplicity in the report
            html = """
            <div style="margin: 10px 0;">
                <h4 style="margin-bottom: 5px;">Test Execution Steps</h4>
                <table style="width:100%; border-collapse: collapse; font-size: 14px; border: 1px solid #ddd;">
                    <thead>
                        <tr style="background-color: #f2f2f2; text-align: left;">
                            <th style="padding: 8px; border: 1px solid #ddd;">Step Description</th>
                            <th style="padding: 8px; border: 1px solid #ddd; width: 100px;">Status</th>
                            <th style="padding: 8px; border: 1px solid #ddd;">Details / Error</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for step in current_steps:
                status = step["status"]
                name = step["name"]
                error = step["error"]
                
                # Style based on status
                if status == "passed":
                    status_style = "color: green; font-weight: bold;"
                    row_style = ""
                elif status == "failed":
                    status_style = "color: red; font-weight: bold;"
                    row_style = "background-color: #fff0f0;"
                else:
                    status_style = "color: orange;"
                    row_style = ""
                
                error_html = f"<pre style='margin: 0; white-space: pre-wrap; color: red;'>{error}</pre>" if error else "-"
                
                html += f"""
                        <tr style="{row_style}">
                            <td style="padding: 8px; border: 1px solid #ddd;">{name}</td>
                            <td style="padding: 8px; border: 1px solid #ddd; {status_style}">{status.upper()}</td>
                            <td style="padding: 8px; border: 1px solid #ddd;">{error_html}</td>
                        </tr>
                """
            
            html += """
                    </tbody>
                </table>
            </div>
            """
            
            # Add to report extras using pytest-html's extras module
            # We import here to avoid failure if pytest-html is not installed, 
            # although it's required for this feature.
            try:
                from pytest_html import extras
                if not hasattr(report, "extras"):
                    report.extras = []
                report.extras.append(extras.html(html))
            except ImportError:
                pass


# -------------------------------
# API Fixtures
# -------------------------------
@pytest.fixture(scope="session")
def api_token(playwright: Playwright) -> str:
    """
    Get a valid JWT token for API interactions.
    """
    request_context = playwright.request.new_context(base_url=BASE_URL)
    response = request_context.post(
        LOGIN_API_PATH,

        data=json.dumps({"username": API_USERNAME, "password": API_PASSWORD}),
        headers={"Content-Type": "application/json"},

    )
    if not response.ok:
        raise RuntimeError(f"Failed to get API token: {response.status} {response.text()}")
    
    data = response.json()
    token = data.get("token") or data.get("access_token")
    if not token:
        raise RuntimeError("No token found in login response")
    
    return token

@pytest.fixture(scope="session")
def api_context(playwright: Playwright, api_token: str) -> Generator[APIRequestContext, None, None]:
    """
    Session-scoped authenticated APIRequestContext.
    """
    headers = {"Authorization": f"Bearer {api_token}"}
    context = playwright.request.new_context(base_url=BASE_URL, extra_http_headers=headers)
    yield context
    context.dispose()

@pytest.fixture
def new_client(api_context: APIRequestContext) -> Generator[dict, None, None]:
    """
    Create a new client via API before test and return its data.
    """
    import uuid
    # Unique suffix to avoid collisions in parallel execution
    unique_id = str(uuid.uuid4())[:8]

    letters = "".join([c for c in unique_id if c.isalpha()])[:6] or "X"
    client_data = {
        "firstName": f"Auto{letters}",
        "lastName": "Test",
        "dob": "1990-01-01",
        "sex": "Male",
    }
    

    response = api_context.post(
        "/clients",
        data=json.dumps(client_data),
        headers={"Content-Type": "application/json"},
    )

    if not response.ok:
        pytest.fail(f"Failed to create new client fixture: {response.text()}")
        
    client = response.json()
    yield client
    
    # Teardown: Clean up (best effort)
    delete_response = api_context.delete(f"/clients/{client['id']}")
    if not delete_response.ok:
        print(f"Warning: Failed to tear down client {client['id']}: {delete_response.status}")


# -------------------------------
# Browser lifecycle (session-wide)
# -------------------------------
@pytest.fixture(scope="session")
def session_browser(playwright: Playwright, pytestconfig: pytest.Config) -> Generator[Browser, None, None]:
    """
    Launch a single Browser instance for the entire test session.

    Notes
    - We deliberately manage a dedicated session-scoped browser here instead of using the
      default pytest-playwright `browser` fixture to demonstrate explicit lifecycle control.
    - Headless/Browser selection follow pytest-playwright CLI options:
        * --browser [chromium|firefox|webkit]
        * --headed (otherwise runs headless by default)
    """
    browser_opt = pytestconfig.getoption("--browser") or "chromium"
    # Normalize --browser which can be: Enum, string, or a list/tuple (select first)
    def _normalize_browser_name(opt):
        try:
            # If list/tuple provided, take the first value
            if isinstance(opt, (list, tuple)):
                opt = opt[0] if opt else "chromium"
            # Prefer Enum.name, then Enum.value, else string
            if hasattr(opt, "name"):
                name = opt.name
            elif hasattr(opt, "value"):
                name = opt.value
            else:
                name = str(opt)
            return str(name).strip().lower()
        except Exception:
            return "chromium"

    browser_name = _normalize_browser_name(browser_opt)
    headed = pytestconfig.getoption("--headed")
    browser_factory = getattr(playwright, browser_name)
    browser = browser_factory.launch(headless=not headed)
    yield browser
    browser.close()


# -------------------------------------------------------------
# API login bypass -> create storageState per worker (parallel)
# -------------------------------------------------------------
@pytest.fixture(scope="session")
def auth_storage_path(
    playwright: Playwright,
    pytestconfig: pytest.Config,
    worker_id: str,
) -> str:
    """
    Create (or reuse) a per-worker storageState JSON by performing API login and persisting
    authenticated cookies/localStorage to disk.

    Why per-worker? Parallel execution via pytest-xdist launches multiple workers. A unique
    storageState per worker avoids clobbering during concurrent writes and keeps sessions isolated.

    Behavior
    - Tries to login via the demo API using Playwright's request context.
    - If the API returns a Set-Cookie, we persist it via request_context.storage_state().
    - If the API returns only a token (no cookie), we synthesize a cookie with AUTH_COOKIE_NAME
      and persist a valid storageState JSON manually.
    - If login cannot be completed (e.g., missing creds or network issue), we skip tests that
      require pre-auth by raising pytest.Skip from this fixture.
    """
    # Store storageState files under the project-local .auth directory
    auth_dir = Path(pytestconfig.rootpath) / ".auth"
    auth_dir.mkdir(parents=True, exist_ok=True)

    # Normalize worker_id for local/CI: 'master' (no xdist) or 'gw0', 'gw1', ...
    storage_file = auth_dir / f"storageState-{worker_id}.json"

    if storage_file.exists():
        return str(storage_file)

    # Attempt to create the storage state via API login
    try:
        created = create_authenticated_storage_state(
            playwright=playwright,
            storage_path=storage_file,
            base_url=BASE_URL,
            login_api_path=LOGIN_API_PATH,
            auth_cookie_name=AUTH_COOKIE_NAME,
            cookie_domain=COOKIE_DOMAIN,
        )
    except Exception as exc:
        pytest.skip(f"API login bypass failed to create storage state: {exc}")

    if not created or not storage_file.exists():
        pytest.skip(
            "API login bypass could not create a storageState file. "
            "Ensure DEMO_EMAIL/DEMO_PASSWORD (or DEMO_JWT) are set and the demo site is reachable."
        )

    return str(storage_file)


# -------------------------------------------------
# Pre-authenticated Context and Page (test fixtures)
# -------------------------------------------------
@pytest.fixture()
def auth_context(session_browser: Browser, auth_storage_path: str) -> Generator[BrowserContext, None, None]:
    """
    Create a new BrowserContext that loads the previously generated storageState so tests start
    already logged-in (no UI login flow).
    """
    context = session_browser.new_context(storage_state=auth_storage_path, base_url=BASE_URL)
    try:
        yield context
    finally:
        context.close()


@pytest.fixture()

def auth_page(auth_context: BrowserContext, api_token: str) -> Generator[Page, None, None]:
    """
    Convenience fixture returning a pre-authenticated Page.
    """
    # Ensure token is present in localStorage for UI origin before navigating to dashboard
    auth_context.add_init_script("window.localStorage.setItem('token', '" + api_token + "')")
    page = auth_context.new_page()
    # Prime origin so localStorage is set for the correct site before tests navigate
    try:
        page.goto(UI_BASE_URL)
    except Exception:
        pass
    try:
        yield page
    finally:
        page.close()
