from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from playwright.sync_api import APIRequestContext, Playwright

from config.settings import AUTH_COOKIE_NAME


def _env_creds() -> tuple[Optional[str], Optional[str]]:
    """Fetch demo credentials from environment variables."""
    return os.getenv("DEMO_EMAIL"), os.getenv("DEMO_PASSWORD")


def _env_token() -> Optional[str]:
    """Fetch a pre-generated JWT token from the environment if provided."""
    return os.getenv("DEMO_JWT")


def _write_storage_state_cookie(storage_path: Path, cookie_name: str, cookie_value: str, domain: str) -> None:
    """Persist a minimal storageState JSON that contains the given cookie for the target domain."""
    storage = {
        "cookies": [
            {
                "name": cookie_name,
                "value": cookie_value,
                "domain": domain,
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "Lax",
            }
        ],
        "origins": [],
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
    email, password = _env_creds()
    jwt_token = _env_token()

    # If no creds but a token was provided, synthesize storageState directly.
    if (not email or not password) and jwt_token:
        _write_storage_state_cookie(Path(storage_path), auth_cookie_name, jwt_token, cookie_domain)
        return True

    # If we lack both creds and token, cannot proceed.
    if not (email and password):
        return False

    request_context: APIRequestContext = playwright.request.new_context(base_url=base_url, ignore_https_errors=True)
    try:
        # Most login endpoints accept either JSON or form data; we try JSON first then fallback.
        resp = request_context.post(login_api_path, data=None, json={"email": email, "password": password})
        if resp.status == 415:  # Unsupported Media Type, try form data
            resp = request_context.post(login_api_path, data={"email": email, "password": password})

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
                _write_storage_state_cookie(Path(storage_path), auth_cookie_name, token, cookie_domain)
                return True
            return False

        # Happy path: 2xx response
        payload = None
        try:
            payload = resp.json()
        except Exception:
            pass

        # Persist any cookies captured by the request context
        request_context.storage_state(path=str(storage_path))

        # If no cookies were set but a token is present, synthesize cookie-based storageState.
        # This guards APIs that return tokens without Set-Cookie.
        try:
            with open(storage_path, "r", encoding="utf-8") as f:
                current_state = json.load(f)
        except Exception:
            current_state = {"cookies": [], "origins": []}

        if (not current_state.get("cookies")) and isinstance(payload, dict):
            token = (
                payload.get("data", {}).get("token")
                or payload.get("token")
                or payload.get("access_token")
            )
            if token:
                _write_storage_state_cookie(Path(storage_path), auth_cookie_name, token, cookie_domain)

        return True
    finally:
        request_context.dispose()
