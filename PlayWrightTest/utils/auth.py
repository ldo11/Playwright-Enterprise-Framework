from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from playwright.sync_api import APIRequestContext, Playwright

from config.settings import AUTH_COOKIE_NAME, COOKIE_DOMAIN, API_USERNAME, API_PASSWORD


def _env_creds() -> tuple[Optional[str], Optional[str]]:
    """Fetch TestProduct API credentials from settings/env variables."""
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
    """Persist a minimal storageState JSON that seeds localStorage for the Angular app."""
    storage = {
        "cookies": [],
        "origins": [
            {
                "origin": origin.rstrip("/"),
                "localStorage": [
                    {"name": key, "value": value},
                ],
            }
        ],
    }
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    storage_path.write_text(json.dumps(storage, indent=2))


def _post_json(request_context: APIRequestContext, path: str, payload: dict):
    """Send JSON request body explicitly (compatible across playwright versions)."""
    return request_context.post(path, data=json.dumps(payload), headers={"Content-Type": "application/json"})


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

    Returns True if a storageState file was successfully written; else False.
    """
    username, password = _env_creds()
    jwt_token = _env_token()

    # If no creds but a token was provided, synthesize storageState directly.
    if (not username or not password) and jwt_token:
        _write_storage_state_local_storage(Path(storage_path), cookie_domain, auth_cookie_name, jwt_token)
        return True

    # If we lack both creds and token, cannot proceed.
    if not (username and password):
        return False

    request_context: APIRequestContext = playwright.request.new_context(
        base_url=base_url,
        ignore_https_errors=True,
    )
    try:
        # TestProduct expects JSON with username/password
        resp = _post_json(request_context, login_api_path, {"username": username, "password": password})
        if not resp.ok and resp.status == 415:  # Fallback: form data
            resp = request_context.post(login_api_path, form={"username": username, "password": password})

        payload = None
        try:
            payload = resp.json()
        except Exception:
            payload = None

        if not isinstance(payload, dict):
            return False

        token: Optional[str] = (
            payload.get("data", {}).get("token")
            or payload.get("token")
            or payload.get("access_token")
        )

        if not token:
            return False

        # Synthesize storageState with localStorage token for the UI origin
        _write_storage_state_local_storage(Path(storage_path), cookie_domain, auth_cookie_name, token)
        return True
    finally:
        request_context.dispose()
