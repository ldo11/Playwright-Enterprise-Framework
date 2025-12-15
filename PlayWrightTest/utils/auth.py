from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from playwright.sync_api import APIRequestContext, Playwright

from config.settings import AUTH_COOKIE_NAME, API_USERNAME as CFG_USER, API_PASSWORD as CFG_PASS


def _env_creds() -> tuple[Optional[str], Optional[str]]:
    """Fetch demo credentials from environment variables."""
    # Try explicit TESTPRODUCT_*, then DEMO_*, then fall back to config defaults
    user = os.getenv("TESTPRODUCT_USERNAME") or os.getenv("DEMO_EMAIL") or CFG_USER
    pwd = os.getenv("TESTPRODUCT_PASSWORD") or os.getenv("DEMO_PASSWORD") or CFG_PASS
    return user, pwd


def _env_token() -> Optional[str]:
    """Fetch a pre-generated JWT token from the environment if provided."""
    return os.getenv("DEMO_JWT")


def _write_storage_state_localstorage(storage_path: Path, key: str, value: str, origin: str) -> None:
    """Persist a storageState JSON that contains a localStorage token for the target origin."""
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
    """Compatibility helper: send JSON body even when playwright version lacks 'json=' kwarg."""
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
    """
    Attempt to perform an API login and persist the authenticated storage state to disk.

    Strategy (robust across demo APIs):
    1) Try to login via API using provided DEMO_EMAIL/DEMO_PASSWORD.
       - If the server returns a Set-Cookie header, Playwright's request context will capture it.
         We then call storage_state(path=...) to persist it.
       - If the server only returns a token in JSON (no Set-Cookie), we synthesize a cookie using
         AUTH_COOKIE_NAME and COOKIE_DOMAIN, writing a valid storageState JSON manually.
    2) If no creds are configured, fall back to DEMO_JWT and synthesize the cookie-based storageState.

    Returns True if a storageState file was successfully written; else False.
    """
    username, password = _env_creds()
    jwt_token = _env_token()

    # If no creds but a token was provided, synthesize storageState directly.
    if (not username or not password) and jwt_token:
        _write_storage_state_localstorage(Path(storage_path), auth_cookie_name, jwt_token, cookie_domain)
        return True

    # If we lack both creds and token, cannot proceed.
    if not (username and password):
        return False

    request_context: APIRequestContext = playwright.request.new_context(base_url=base_url, ignore_https_errors=True)
    try:
        # Prefer JSON (server expects JSON); try username first, then email as fallback
        resp = _post_json(request_context, login_api_path, {"username": username, "password": password})
        if not resp.ok:
            resp = _post_json(request_context, login_api_path, {"email": username, "password": password})

        if not resp.ok:
            # If server responded with error but returned a token payload, still try to use it.
            try:
                payload = resp.json()
            except Exception:
                payload = None
            token = None
            if isinstance(payload, dict):
                token = (
                    payload.get("data", {}).get("token")
                    or payload.get("token")
                    or payload.get("access_token")
                )
            if token:
                _write_storage_state_localstorage(Path(storage_path), auth_cookie_name, token, cookie_domain)
                return True
            return False

        # Happy path: 2xx response
        payload = None
        try:
            payload = resp.json()
        except Exception:
            pass

        # Synthesize storageState with localStorage token for the UI origin
        if isinstance(payload, dict):
            token = (
                payload.get("data", {}).get("token")
                or payload.get("token")
                or payload.get("access_token")
            )
        else:
            token = None
        if token:
            _write_storage_state_localstorage(Path(storage_path), auth_cookie_name, token, cookie_domain)
        else:
            # As a last resort, persist whatever cookies exist (if server set any)
            request_context.storage_state(path=str(storage_path))

        return True
    finally:
        request_context.dispose()
