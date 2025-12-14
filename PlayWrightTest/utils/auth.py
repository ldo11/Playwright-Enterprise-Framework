from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from playwright.sync_api import APIRequestContext, Playwright

from config.settings import AUTH_COOKIE_NAME, COOKIE_DOMAIN, API_USERNAME, API_PASSWORD


def _env_creds() -> tuple[Optional[str], Optional[str]]:
    """Fetch TestProduct API credentials from settings/env variables."""
    # API_USERNAME/API_PASSWORD already read from TESTPRODUCT_* env vars in settings
    return API_USERNAME, API_PASSWORD


def _env_token() -> Optional[str]:
    """Fetch a pre-generated JWT token for TestProduct if provided."""
    return os.getenv("TESTPRODUCT_JWT")


def _write_storage_state_local_storage(
    storage_path: Path,
    origin: str,
    key: str,
    value: str,
) -> None:
    """Persist a minimal storageState JSON that seeds localStorage for the Angular app.

    The TestProduct UI reads `localStorage['token']` to attach the Authorization header, so we
    store the JWT there rather than relying on cookies.
    """
    storage = {
        "cookies": [],
        "origins": [
            {
                "origin": origin,
                "localStorage": [
                    {"name": key, "value": value},
                ],
            }
        ],
    }
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    storage_path.write_text(json.dumps(storage, indent=2))


def create_authenticated_storage_state(
    *,
    playwright: Playwright,
    storage_path: Path,
    base_url: str,
    login_api_path: str,
    auth_cookie_name: str,
    cookie_domain: str,
) -> bool:
    """Perform an API login against the TestProduct API and persist storageState.

    Strategy for TestProduct:
    1) Prefer TESTPRODUCT_USERNAME/TESTPRODUCT_PASSWORD (via API_USERNAME/API_PASSWORD).
    2) If not provided but TESTPRODUCT_JWT is set, synthesize storageState directly.
    3) The TestProduct API returns a JWT token in JSON (no cookies). We call POST /login,
       extract the token from the response body, and write a storageState JSON that seeds
       localStorage with that token for the Angular app origin.

    Returns True if a storageState file was successfully written; else False.
    """
    username, password = _env_creds()
    jwt_token = _env_token()

    # If no creds but a token was provided, synthesize storageState directly.
    if (not username or not password) and jwt_token:
        _write_storage_state_local_storage(Path(storage_path), cookie_domain, auth_cookie_name, jwt_token)
        return True

    # Force override if it looks like localhost:4200 (legacy default) to ensure tests run against current environment
    if "localhost:4200" in cookie_domain:
        cookie_domain = "http://127.0.0.1:4201"

    # If we lack both creds and token, cannot proceed.
    if not (username and password):
        return False

    request_context: APIRequestContext = playwright.request.new_context(
        base_url=base_url,
        ignore_https_errors=True,
    )
    try:
        # TestProduct expects JSON with username/password.
        # In Playwright Python, passing a dict to 'data' sends it as JSON
        resp = request_context.post(login_api_path, data={"username": username, "password": password})
        
        if not resp.ok and resp.status == 415:  # Unsupported Media Type, try form data
            resp = request_context.post(login_api_path, form={"username": username, "password": password})

        try:
           payload = resp.json()
        except Exception:
           payload = None

        if not resp.ok and not isinstance(payload, dict):
            return False

        token: Optional[str] = None
        if isinstance(payload, dict):
            token = (
                payload.get("data", {}).get("token")
                or payload.get("token")
                or payload.get("access_token")
            )

        if not token:
            return False

        _write_storage_state_local_storage(Path(storage_path), cookie_domain, auth_cookie_name, token)
        return True
    finally:
        request_context.dispose()
