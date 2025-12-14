import pytest
from playwright.sync_api import APIRequestContext, expect

@pytest.mark.api
def test_crud_client(api_context: APIRequestContext):
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # 1. Create
    client_data = {
        "firstName": f"CRUD_{unique_id}",
        "lastName": "Test",
        "dob": "1990-01-01",
        "sex": "Male"
    }
    response = api_context.post("/clients", data=client_data)
    assert response.ok, f"Create failed: {response.text()}"
    created_client = response.json()
    client_id = created_client["id"]
    assert created_client["firstName"] == f"CRUD_{unique_id}"

    # 2. Get
    response = api_context.get(f"/clients/{client_id}")
    assert response.ok
    fetched = response.json()
    assert fetched["id"] == client_id

    # 3. Update (PUT)
    update_data = {
        "firstName": f"CRUD_Updated_{unique_id}",
        "lastName": "Test",
        "dob": "1990-01-01",
        "sex": "Female"
    }
    response = api_context.put(f"/clients/{client_id}", data=update_data)
    assert response.ok, f"Update failed: {response.text()}"
    updated = response.json()
    assert updated["firstName"] == f"CRUD_Updated_{unique_id}"
    assert updated["sex"] == "Female"

    # 4. Delete
    response = api_context.delete(f"/clients/{client_id}")
    assert response.ok, f"Delete failed: {response.text()}"

    # 5. Verify Delete
    response = api_context.get(f"/clients/{client_id}")
    assert response.status == 404
