import pytest
import requests
from utils.step import step
from config.settings import BASE_URL, API_USERNAME, API_PASSWORD


@pytest.mark.api
class TestTestProductAPI:
    def _login(self) -> str:
        """Helper to obtain a JWT token from the TestProduct API."""
        with step("Helper: Login to API to get token"):
            resp = requests.post(f"{BASE_URL}/login", json={"username": API_USERNAME, "password": API_PASSWORD})
            resp.raise_for_status()
            data = resp.json() if resp.content else {}
            token = (data.get("data", {}) or {}).get("token") or data.get("token") or data.get("access_token")
            assert token, "Expected token in login response"
            return token

    def test_health_endpoint(self):
        with step("Check Health Endpoint"):
            resp = requests.get(f"{BASE_URL}/health")
            resp.raise_for_status()
            payload = resp.json()
            assert payload.get("status") == "ok"

    def test_login_and_get_clients(self):
        token = self._login()
        
        with step("Get Clients List"):
            headers = {"Authorization": f"Bearer {token}"}
            # GET /clients should return a JSON array (may be empty on first run)
            resp = requests.get(f"{BASE_URL}/clients", headers=headers)
            resp.raise_for_status()
            data = resp.json()
            assert isinstance(data, list)
