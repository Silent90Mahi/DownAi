"""
Authentication Tests
Tests for authentication endpoints and user management
"""
import pytest
from fastapi import status


@pytest.mark.unit
class TestAuthentication:
    """Test authentication endpoints"""

    def test_register_new_user(self, client: TestClient):
        """Test user registration"""
        response = client.post(
            "/api/auth/register",
            json={
                "phone": "9123456789",
                "name": "New User",
                "role": "SHG",
                "district": "Hyderabad",
                "language_preference": "English"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "user" in data
        assert data["user"]["phone"] == "9123456789"
        assert data["user"]["name"] == "New User"

    def test_register_duplicate_phone(self, client: TestClient, test_user: models.User):
        """Test registration with duplicate phone number"""
        response = client.post(
            "/api/auth/register",
            json={
                "phone": test_user.phone,  # Duplicate
                "name": "Duplicate User",
                "role": "SHG"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self, client: TestClient, test_user: models.User):
        """Test successful login"""
        response = client.post(
            "/api/auth/login",
            json={
                "phone": test_user.phone,
                "password": "test123"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data

    def test_login_invalid_phone(self, client: TestClient):
        """Test login with invalid phone"""
        response = client.post(
            "/api/auth/login",
            json={
                "phone": "0000000000",
                "password": "test123"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user(self, client: TestClient, auth_headers: dict):
        """Test getting current user profile"""
        response = client.get(
            "/api/auth/me",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["phone"] == "9999999999"
        assert data["name"] == "Test User"

    def test_update_user_profile(self, client: TestClient, auth_headers: dict):
        """Test updating user profile"""
        response = client.put(
            "/api/auth/profile",
            headers=auth_headers,
            json={
                "name": "Updated Name",
                "district": "Updated District"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["district"] == "Updated District"

    def test_logout(self, client: TestClient, auth_headers: dict):
        """Test logout functionality"""
        response = client.post(
            "/api/auth/logout",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True


@pytest.mark.unit
class TestAuthorization:
    """Test authorization and access control"""

    def test_unauthorized_access(self, client: TestClient):
        """Test access without authentication"""
        response = client.get("/api/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token(self, client: TestClient):
        """Test access with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_only_endpoint(self, client: TestClient, auth_headers: dict):
        """Test admin-only endpoint with regular user"""
        response = client.get(
            "/api/users/all",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_access(self, client: TestClient, admin_headers: dict):
        """Test admin endpoint with admin credentials"""
        response = client.get(
            "/api/users/all",
            headers=admin_headers
        )

        assert response.status_code == status.HTTP_200_OK
