import json
import pytest
from config.settings import BASE_URL, API_USERNAME, API_PASSWORD

pytestmark = pytest.mark.regressionTest


def _login_and_ctx(playwright):
    req = playwright.request.new_context(base_url=BASE_URL)
    resp = req.post(
        "/login",
        data=json.dumps({"username": API_USERNAME, "password": API_PASSWORD}),
        headers={"Content-Type": "application/json"},
    )
    assert resp.ok, f"Login failed: {resp.status} {resp.text()}"
    token = resp.json().get("token")
    assert token, "No token in login response"
    api = playwright.request.new_context(base_url=BASE_URL, extra_http_headers={"Authorization": f"Bearer {token}"})
    return token, req, api


class TestTokenManagement:
    def test_token_status_and_invalidate_flow(self, playwright):
        token, login_ctx, api = _login_and_ctx(playwright)
        try:
            # Status should be reachable and 'Valid' after a use
            s = api.get("/tokens/status")
            assert s.ok, f"/tokens/status failed: {s.status} {s.text()}"
            data = s.json()
            assert data.get("status") in {"Active", "Valid"}, data
            assert "lastUsedAt" in data

            # Invalidate
            inv = api.post("/tokens/invalidate")
            assert inv.ok, f"/tokens/invalidate failed: {inv.status} {inv.text()}"

            # Subsequent auth calls should fail with 401
            r = api.get("/clients")
            assert r.status == 401, f"Expected 401 after invalidation, got {r.status}"
        finally:
            # Best-effort cleanup of request contexts
            try:
                api.dispose()
            except Exception:
                pass
            try:
                login_ctx.dispose()
            except Exception:
                pass

    def test_invalid_jwt_rejected(self, playwright):
        bad_api = playwright.request.new_context(base_url=BASE_URL, extra_http_headers={"Authorization": "Bearer not_a_real_token"})
        try:
            resp = bad_api.get("/clients")
            assert resp.status in (401, 403), f"Expected 401/403 for invalid JWT, got {resp.status}"
        finally:
            bad_api.dispose()

    def test_missing_token_rejected(self, playwright):
        anon = playwright.request.new_context(base_url=BASE_URL)
        try:
            resp = anon.get("/clients")
            assert resp.status == 401, f"Expected 401 for missing token, got {resp.status}"
        finally:
            anon.dispose()
