import json
import pytest
from config.settings import API_USERNAME

pytestmark = pytest.mark.regressionTest


def _post_json(api_context, path, payload):
    return api_context.post(path, data=json.dumps(payload), headers={"Content-Type": "application/json"})


def _put_json(api_context, path, payload):
    return api_context.put(path, data=json.dumps(payload), headers={"Content-Type": "application/json"})


class TestApiClientsCRUD:
    def test_crud_client_happy_path(self, api_context):
        # Create
        payload = {"firstName": "ApiHappy", "lastName": "User", "dob": "1990-01-01", "sex": "Male"}
        resp = _post_json(api_context, "/clients", payload)
        assert resp.status == 201, resp.text()
        created = resp.json()
        cid = created["id"]
        try:
            # List mine
            lst = api_context.get("/clients?mine=true")
            assert lst.ok
            items = lst.json()
            assert any(c.get("id") == cid for c in items)

            # Get by id
            got = api_context.get(f"/clients/{cid}")
            assert got.ok
            assert got.json()["firstName"] == payload["firstName"]

            # Update
            upd = _put_json(api_context, f"/clients/{cid}", {**payload, "lastName": "Updated"})
            assert upd.ok
            assert upd.json()["lastName"] == "Updated"
        finally:
            # Delete
            delr = api_context.delete(f"/clients/{cid}")
            assert delr.ok

    def test_create_unhappy_validation(self, api_context):
        # invalid sex
        resp = _post_json(api_context, "/clients", {"firstName": "John", "lastName": "Doe", "dob": "1990-01-01", "sex": "N/A"})
        assert resp.status == 400
        # invalid name pattern
        resp = _post_json(api_context, "/clients", {"firstName": "J0hn", "lastName": "Doe", "dob": "1990-01-01", "sex": "Male"})
        assert resp.status == 400

    def test_update_unhappy_validation(self, api_context, new_client):
        cid = new_client["id"]
        resp = _put_json(api_context, f"/clients/{cid}", {"firstName": "John", "lastName": "X" * 21, "dob": "1990-01-01", "sex": "Male"})
        assert resp.status == 400
