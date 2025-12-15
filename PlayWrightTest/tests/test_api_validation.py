import json
import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.regressionTest


def _post_json(api_context, path, payload):
    return api_context.post(
        path,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )


class TestApiValidation:
    def test_create_rejects_firstname_special_chars(self, api_context):
        payload = {"firstName": "John$", "lastName": "Doe", "dob": "1990-01-01", "sex": "Male"}
        resp = _post_json(api_context, "/clients", payload)
        assert resp.status == 400

    def test_create_rejects_firstname_numbers(self, api_context):
        payload = {"firstName": "John2", "lastName": "Doe", "dob": "1990-01-01", "sex": "Male"}
        resp = _post_json(api_context, "/clients", payload)
        assert resp.status == 400

    def test_create_rejects_lastname_special_chars(self, api_context):
        payload = {"firstName": "John", "lastName": "Doe@", "dob": "1990-01-01", "sex": "Male"}
        resp = _post_json(api_context, "/clients", payload)
        assert resp.status == 400

    def test_create_rejects_firstname_too_long(self, api_context):
        payload = {"firstName": "A" * 26, "lastName": "Doe", "dob": "1990-01-01", "sex": "Male"}
        resp = _post_json(api_context, "/clients", payload)
        assert resp.status == 400

    def test_create_rejects_lastname_too_long(self, api_context):
        payload = {"firstName": "John", "lastName": "B" * 21, "dob": "1990-01-01", "sex": "Male"}
        resp = _post_json(api_context, "/clients", payload)
        assert resp.status == 400

    def test_create_rejects_invalid_sex_na(self, api_context):
        payload = {"firstName": "John", "lastName": "Doe", "dob": "1990-01-01", "sex": "N/A"}
        resp = _post_json(api_context, "/clients", payload)
        assert resp.status == 400

    def test_create_rejects_underage(self, api_context):
        payload = {"firstName": "John", "lastName": "Doe", "dob": "2015-01-01", "sex": "Male"}
        resp = _post_json(api_context, "/clients", payload)
        assert resp.status == 400

    def test_update_rejects_invalid_fields(self, api_context, new_client):
        cid = new_client["id"]
        # Special char in firstName
        resp = api_context.put(
            f"/clients/{cid}",
            data=json.dumps({"firstName": "Jo@hn", "lastName": "Doe", "dob": "1990-01-01", "sex": "Male"}),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 400
        # Too long lastName
        resp = api_context.put(
            f"/clients/{cid}",
            data=json.dumps({"firstName": "John", "lastName": "B" * 21, "dob": "1990-01-01", "sex": "Male"}),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 400
        # Underage DOB
        resp = api_context.put(
            f"/clients/{cid}",
            data=json.dumps({"firstName": "John", "lastName": "Doe", "dob": "2015-01-01", "sex": "Male"}),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 400
