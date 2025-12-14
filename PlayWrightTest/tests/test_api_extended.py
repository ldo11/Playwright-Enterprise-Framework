import pytest
from playwright.sync_api import APIRequestContext

@pytest.mark.api
class TestAPIExtended:
    
    def test_create_client_missing_fields(self, api_context: APIRequestContext):
        """Test creating a client with missing required fields."""
        # Missing lastName
        client_data = {
            "firstName": "Incomplete",
            "dob": "1990-01-01",
            "sex": "Male"
        }
        response = api_context.post("/clients", data=client_data)
        assert response.status == 400
        error_msg = response.json().get("message", "")
        assert "required" in error_msg

    def test_create_client_invalid_sex(self, api_context: APIRequestContext):
        """Test creating a client with invalid sex value."""
        client_data = {
            "firstName": "Invalid",
            "lastName": "Sex",
            "dob": "1990-01-01",
            "sex": "Alien"
        }
        response = api_context.post("/clients", data=client_data)
        assert response.status == 400
        error_msg = response.json().get("message", "")
        assert "sex must be" in error_msg

    def test_create_client_invalid_dob(self, api_context: APIRequestContext):
        """Test creating a client with invalid DOB format."""
        client_data = {
            "firstName": "Invalid",
            "lastName": "Date",
            "dob": "not-a-date",
            "sex": "Male"
        }
        response = api_context.post("/clients", data=client_data)
        assert response.status == 400
        error_msg = response.json().get("message", "")
        assert "dob must be a valid date" in error_msg

    def test_get_non_existent_client(self, api_context: APIRequestContext):
        """Test retrieving a client ID that does not exist."""
        response = api_context.get("/clients/99999999")
        assert response.status == 404
        error_msg = response.json().get("message", "")
        assert "Client not found" in error_msg

    def test_delete_non_existent_client(self, api_context: APIRequestContext):
        """Test deleting a client ID that does not exist."""
        response = api_context.delete("/clients/99999999")
        assert response.status == 404
        error_msg = response.json().get("message", "")
        assert "Client not found" in error_msg

    def test_unauthorized_access(self, playwright):
        """Test accessing protected endpoint without token."""
        # Create a context without auth headers (default api_context fixture usually has them)
        api_request = playwright.request.new_context(base_url="http://127.0.0.1:3001")
        response = api_request.get("/clients")
        assert response.status == 401
        error_msg = response.json().get("message", "")
        assert "Missing token" in error_msg
