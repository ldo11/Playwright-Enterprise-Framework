from __future__ import annotations

# Core Pytest and typing
import os
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
)
from utils.auth import create_authenticated_storage_state


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
    browser_name = pytestconfig.getoption("--browser") or "chromium"
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
def auth_page(auth_context: BrowserContext) -> Generator[Page, None, None]:
    """
    Convenience fixture returning a pre-authenticated Page.
    """
    page = auth_context.new_page()
    try:
        yield page
    finally:
        page.close()
