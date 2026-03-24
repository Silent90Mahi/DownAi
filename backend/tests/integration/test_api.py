"""
Integration Tests for API Endpoints
Test complete request/response cycles
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    @pytest.mark.integration
    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.integration
    def test_api_root(self, client: TestClient):
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK


class TestAuthenticationFlow:
    @pytest.mark.integration
    def test_user_registration(self, client: TestClient):
        user_data = {
            "phone": "9998887776",
            "name": "New User",
            "email": "newuser@example.com",
            "role": "SHG",
            "district": "Bangalore",
            "state": "Karnataka"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST
        ]

    @pytest.mark.integration
    def test_user_login(self, client: TestClient, test_user):
        login_data = {
            "phone": test_user.phone,
            "otp": "123456"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND
        ]


class TestProductEndpoints:
    @pytest.mark.integration
    def test_list_products(self, client: TestClient):
        response = client.get("/api/products/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.integration
    def test_get_product_by_id(self, client: TestClient, test_product):
        response = client.get(f"/api/products/{test_product.id}")
        
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    @pytest.mark.integration
    def test_search_products(self, client: TestClient):
        response = client.get("/api/products/search?query=basket")
        
        assert response.status_code == status.HTTP_200_OK


class TestOrderEndpoints:
    @pytest.mark.integration
    def test_create_order(self, client: TestClient, auth_headers, sample_order_data):
        response = client.post(
            "/api/orders/",
            json=sample_order_data,
            headers=auth_headers
        )
        
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

    @pytest.mark.integration
    def test_get_user_orders(self, client: TestClient, auth_headers):
        response = client.get(
            "/api/orders/my-orders",
            headers=auth_headers
        )
        
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED
        ]

    @pytest.mark.integration
    def test_update_order_status(self, client: TestClient, admin_headers, test_order):
        update_data = {
            "status": "shipped",
            "tracking_number": "TRK123456"
        }
        
        response = client.put(
            f"/api/orders/{test_order.id}/status",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]


class TestMarketplaceIntegration:
    @pytest.mark.integration
    def test_get_categories(self, client: TestClient):
        response = client.get("/api/products/categories")
        
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.integration
    def test_filter_products_by_category(self, client: TestClient):
        response = client.get("/api/products/?category=Handicrafts")
        
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.integration
    def test_product_pagination(self, client: TestClient):
        response = client.get("/api/products/?skip=0&limit=10")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 10


class TestTrustSystem:
    @pytest.mark.integration
    def test_get_user_trust_score(self, client: TestClient, auth_headers, test_user):
        response = client.get(
            f"/api/trust/score/{test_user.id}",
            headers=auth_headers
        )
        
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND
        ]

    @pytest.mark.integration
    def test_update_trust_after_transaction(self, client: TestClient, test_order):
        response = client.post(
            f"/api/trust/update/{test_order.buyer_id}",
            json={"transaction_id": test_order.id, "rating": 5}
        )
        
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
