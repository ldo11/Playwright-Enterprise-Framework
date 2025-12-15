import json
import pytest
from config.settings import BASE_URL, API_USERNAME, API_PASSWORD

pytestmark = pytest.mark.regressionTest


def _post(api, path, payload):
    return api.post(path, data=json.dumps(payload), headers={"Content-Type": "application/json"})


def test_login_success(playwright):
    api = playwright.request.new_context(base_url=BASE_URL)
    resp = _post(api, "/login", {"username": API_USERNAME, "password": API_PASSWORD})
    assert resp.ok, f"Login failed: {resp.status} {resp.text()}"
    body = resp.json()
    assert body.get("token")
    assert body.get("user", {}).get("username") == API_USERNAME
    api.dispose()


def test_login_missing_fields(playwright):
    api = playwright.request.new_context(base_url=BASE_URL)
    resp = _post(api, "/login", {"username": API_USERNAME})
    assert resp.status == 400
    api.dispose()


def test_login_invalid_credentials(playwright):
    api = playwright.request.new_context(base_url=BASE_URL)
    resp = _post(api, "/login", {"username": API_USERNAME, "password": "wrong"})
    assert resp.status == 401
    api.dispose()
