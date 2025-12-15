import pytest
from playwright.sync_api import APIRequestContext
from utils.step import step
from config.settings import BASE_URL

@pytest.mark.api
class TestAPIExtended:
    
    def test_create_client_missing_fields(self, api_context: APIRequestContext):
        """Test creating a client with missing required fields."""
        with step("Attempt create with missing lastName"):
            # Missing lastName
            client_data = {
                "firstName": "Incomplete",
                "dob": "1990-01-01",
                "sex": "Male"
            }
            response = api_context.post("/clients", data=client_data)
        
        with step("Verify 400 Error for Missing Fields"):
            assert response.status == 400
            error_msg = response.json().get("message", "")
            assert "required" in error_msg

    def test_create_client_invalid_sex(self, api_context: APIRequestContext):
        """Test creating a client with invalid sex value."""
        with step("Attempt create with invalid sex"):
            client_data = {
                "firstName": "Invalid",
                "lastName": "Sex",
                "dob": "1990-01-01",
                "sex": "Alien"
            }
            response = api_context.post("/clients", data=client_data)
        
        with step("Verify 400 Error for Invalid Sex"):
            assert response.status == 400
            error_msg = response.json().get("message", "")
            assert "sex must be" in error_msg

    def test_create_client_invalid_dob(self, api_context: APIRequestContext):
        """Test creating a client with invalid DOB format."""
        with step("Attempt create with invalid DOB"):
            client_data = {
                "firstName": "Invalid",
                "lastName": "Date",
                "dob": "not-a-date",
                "sex": "Male"
            }
            response = api_context.post("/clients", data=client_data)
        
        with step("Verify 400 Error for Invalid DOB"):
            assert response.status == 400
            error_msg = response.json().get("message", "")
            assert "dob must be a valid date" in error_msg

    def test_get_non_existent_client(self, api_context: APIRequestContext):
        """Test retrieving a client ID that does not exist."""
        with step("Get non-existent client ID 99999999"):
            response = api_context.get("/clients/99999999")
        
        with step("Verify 404 Not Found"):
            assert response.status == 404
            error_msg = response.json().get("message", "")
            assert "Client not found" in error_msg

    def test_delete_non_existent_client(self, api_context: APIRequestContext):
        """Test deleting a client ID that does not exist."""
        with step("Delete non-existent client ID 99999999"):
            response = api_context.delete("/clients/99999999")
        
        with step("Verify 404 Not Found"):
            assert response.status == 404
            error_msg = response.json().get("message", "")
            assert "Client not found" in error_msg

    def test_unauthorized_access(self, playwright):
        """Test accessing protected endpoint without token."""
        with step("Create unauthenticated context"):
            # Create a context without auth headers (default api_context fixture usually has them)
            api_request = playwright.request.new_context(base_url=BASE_URL)
        
        with step("Attempt to access /clients without token"):
            response = api_request.get("/clients")
        
        with step("Verify 401 Unauthorized"):
            assert response.status == 401
            error_msg = response.json().get("message", "")
            assert "Missing token" in error_msg
