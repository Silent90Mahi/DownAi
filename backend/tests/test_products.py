"""
Product Tests
Tests for product CRUD operations and management
"""
import pytest
from fastapi import status


@pytest.mark.unit
class TestProductCreation:
    """Test product creation endpoints"""

    def test_create_product_success(self, client: TestClient, auth_headers: dict, sample_product_data: dict):
        """Test successful product creation"""
        response = client.post(
            "/api/products/",
            headers=auth_headers,
            json=sample_product_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == sample_product_data["name"]
        assert data["category"] == sample_product_data["category"]
        assert data["price"] == sample_product_data["price"]
        assert data["status"] == "Draft"

    def test_create_product_unauthorized(self, client: TestClient, sample_product_data: dict):
        """Test product creation without authentication"""
        response = client.post(
            "/api/products/",
            json=sample_product_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_product_missing_fields(self, client: TestClient, auth_headers: dict):
        """Test product creation with missing required fields"""
        response = client.post(
            "/api/products/",
            headers=auth_headers,
            json={
                "name": "Test Product"
                # Missing category, price, etc.
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_product_invalid_price(self, client: TestClient, auth_headers: dict):
        """Test product creation with invalid price"""
        response = client.post(
            "/api/products/",
            headers=auth_headers,
            json={
                "name": "Test Product",
                "category": "Handicrafts",
                "price": -100.00,  # Invalid negative price
                "stock": 10
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.unit
class TestProductRetrieval:
    """Test product retrieval endpoints"""

    def test_get_all_products(self, client: TestClient, test_product: models.Product):
        """Test getting all products"""
        response = client.get("/api/products/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0
        assert "total" in data
        assert "page" in data

    def test_get_product_by_id(self, client: TestClient, test_product: models.Product):
        """Test getting specific product"""
        response = client.get(f"/api/products/{test_product.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_product.id
        assert data["name"] == test_product.name

    def test_get_product_not_found(self, client: TestClient):
        """Test getting non-existent product"""
        response = client.get("/api/products/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_products_with_pagination(self, client: TestClient, db: Session, test_seller: models.User):
        """Test product pagination"""
        # Create multiple products
        for i in range(25):
            product = models.Product(
                seller_id=test_seller.id,
                name=f"Product {i}",
                category="Handicrafts",
                price=100.00 + i,
                stock=10,
                status=models.ProductStatus.ACTIVE
            )
            db.add(product)
        db.commit()

        # Get first page
        response = client.get("/api/products/?page=1&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["total_pages"] > 1

    def test_get_products_with_filters(self, client: TestClient, test_product: models.Product):
        """Test product filtering by category"""
        response = client.get(f"/api/products/?category=Handicrafts")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for product in data["items"]:
            assert product["category"] == "Handicrafts"


@pytest.mark.unit
class TestProductUpdate:
    """Test product update endpoints"""

    def test_update_product_success(self, client: TestClient, auth_headers: dict, test_product: models.Product):
        """Test successful product update"""
        response = client.put(
            f"/api/products/{test_product.id}",
            headers=auth_headers,
            json={
                "name": "Updated Product Name",
                "price": 750.00
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Product Name"
        assert data["price"] == 750.00

    def test_update_product_unauthorized(self, client: TestClient, test_product: models.Product):
        """Test product update without authentication"""
        response = client.put(
            f"/api/products/{test_product.id}",
            json={"name": "Updated"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_product_not_owner(self, client: TestClient, auth_headers: dict, db: Session):
        """Test updating product owned by another user"""
        other_user = models.User(
            phone="6666666666",
            name="Other User",
            role=models.UserRole.SHG
        )
        db.add(other_user)
        db.commit()

        other_product = models.Product(
            seller_id=other_user.id,
            name="Other Product",
            category="Handicrafts",
            price=100.00,
            stock=10
        )
        db.add(other_product)
        db.commit()

        response = client.put(
            f"/api/products/{other_product.id}",
            headers=auth_headers,
            json={"name": "Hacked"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.unit
class TestProductDeletion:
    """Test product deletion endpoints"""

    def test_delete_product_success(self, client: TestClient, auth_headers: dict, test_product: models.Product):
        """Test successful product deletion"""
        response = client.delete(
            f"/api/products/{test_product.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify product is deleted
        get_response = client.get(f"/api/products/{test_product.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_product_unauthorized(self, client: TestClient, test_product: models.Product):
        """Test product deletion without authentication"""
        response = client.delete(f"/api/products/{test_product.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
class TestProductStatus:
    """Test product status management"""

    def test_activate_product(self, client: TestClient, auth_headers: dict, db: Session, test_seller: models.User):
        """Test activating a product"""
        product = models.Product(
            seller_id=test_seller.id,
            name="Draft Product",
            category="Handicrafts",
            price=100.00,
            stock=10,
            status=models.ProductStatus.DRAFT
        )
        db.add(product)
        db.commit()

        response = client.patch(
            f"/api/products/{product.id}/status",
            headers=auth_headers,
            json={"status": "Active"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "Active"


@pytest.mark.integration
class TestProductIntegration:
    """Integration tests for product workflows"""

    def test_full_product_lifecycle(self, client: TestClient, auth_headers: dict, db: Session, test_seller: models.User):
        """Test complete product lifecycle: create -> activate -> update -> delete"""
        # Create
        create_response = client.post(
            "/api/products/",
            headers=auth_headers,
            json={
                "name": "Lifecycle Test Product",
                "category": "Handicrafts",
                "price": 500.00,
                "stock": 100
            }
        )
        assert create_response.status_code == status.HTTP_200_OK
        product_id = create_response.json()["id"]

        # Activate
        activate_response = client.patch(
            f"/api/products/{product_id}/status",
            headers=auth_headers,
            json={"status": "Active"}
        )
        assert activate_response.status_code == status.HTTP_200_OK

        # Update
        update_response = client.put(
            f"/api/products/{product_id}",
            headers=auth_headers,
            json={"price": 600.00}
        )
        assert update_response.status_code == status.HTTP_200_OK

        # Delete
        delete_response = client.delete(
            f"/api/products/{product_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == status.HTTP_200_OK
