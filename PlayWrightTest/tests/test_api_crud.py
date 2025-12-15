import pytest
from playwright.sync_api import APIRequestContext, expect
from utils.step import step

@pytest.mark.api
def test_verify_client_crud_operations_when_interacting_via_api_with_valid_data(api_context: APIRequestContext):
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    # Ensure firstName conforms to letters-only validation rules
    letters_only = "".join([c for c in unique_id if c.isalpha()]) or "X"
    client_id = None
    
    with step("Create a new client with valid data"):
        client_data = {
            "firstName": f"CRUD{letters_only}",
            "lastName": "Test",
            "dob": "1990-01-01",
            "sex": "Male"
        }
        response = api_context.post("/clients", data=client_data)
        assert response.ok, f"Create failed: {response.text()}"
        created_client = response.json()
        client_id = created_client["id"]
        assert created_client["firstName"] == f"CRUD{letters_only}"

    with step(f"Retrieve the client by ID: {client_id}"):
        response = api_context.get(f"/clients/{client_id}")
        assert response.ok, f"Get failed: {response.text()}"
        fetched = response.json()
        assert fetched["id"] == client_id

    with step("Update the client details (Change sex to Female)"):
        update_data = {
            "firstName": f"CRUDUpdated{letters_only}",
            "lastName": "Test",
            "dob": "1990-01-01",
            "sex": "Female"
        }
        response = api_context.put(f"/clients/{client_id}", data=update_data)
        assert response.ok, f"Update failed: {response.text()}"
        updated = response.json()
        assert updated["firstName"] == f"CRUDUpdated{letters_only}"
        assert updated["sex"] == "Female"

    with step("Delete the client"):
        response = api_context.delete(f"/clients/{client_id}")
        assert response.ok, f"Delete failed: {response.text()}"

    with step("Verify the client is successfully deleted (404 Expected)"):
        response = api_context.get(f"/clients/{client_id}")
        assert response.status == 404, f"Expected 404 but got {response.status}"
