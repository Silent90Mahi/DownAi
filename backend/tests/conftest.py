"""
Pytest Configuration
Fixtures and test configuration for the test suite
"""
import os
import sys
import pytest
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import get_db
from app.main import app
from app import models

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database for each test"""
    # Create all tables
    models.Base.metadata.create_all(bind=engine)

    # Create session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        models.Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database override"""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> models.User:
    """Create a test user"""
    user = models.User(
        phone="9999999999",
        name="Test User",
        email="test@example.com",
        role=models.UserRole.SHG,
        district="Hyderabad",
        state="Telangana",
        trust_score=75.0,
        trust_coins=100,
        trust_badge="Silver",
        language_preference="English",
        low_bandwidth_mode=False,
        notification_enabled=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_seller(db: Session) -> models.User:
    """Create a test seller user"""
    user = models.User(
        phone="8888888888",
        name="Test Seller",
        email="seller@example.com",
        role=models.UserRole.SHG,
        district="Hyderabad",
        state="Telangana",
        trust_score=85.0,
        trust_coins=250,
        trust_badge="Gold",
        language_preference="English",
        low_bandwidth_mode=False,
        notification_enabled=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_product(db: Session, test_seller: models.User) -> models.Product:
    """Create a test product"""
    product = models.Product(
        seller_id=test_seller.id,
        name="Handmade Basket",
        description="Beautiful handmade bamboo basket",
        category="Handicrafts",
        subcategory="Baskets",
        price=500.00,
        stock=50,
        min_order_quantity=1,
        unit="piece",
        status=models.ProductStatus.ACTIVE,
        images=["basket1.jpg", "basket2.jpg"],
        tags=["handmade", "bamboo", "eco-friendly"]
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture
def test_order(db: Session, test_user: models.User, test_seller: models.User, test_product: models.Product) -> models.Order:
    """Create a test order"""
    order = models.Order(
        buyer_id=test_user.id,
        seller_id=test_seller.id,
        order_number="ORD001",
        final_amount=1000.00,
        shipping_address="123 Test Street, Hyderabad",
        order_status=models.OrderStatus.CONFIRMED,
        payment_status=models.PaymentStatus.COMPLETED,
        payment_method="UPI"
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Add order item
    item = models.OrderItem(
        order_id=order.id,
        product_id=test_product.id,
        quantity=2,
        unit_price=500.00,
        total_price=1000.00
    )
    db.add(item)
    db.commit()

    return order


@pytest.fixture
def auth_headers(client: TestClient, test_user: models.User) -> dict:
    """Get authentication headers for a test user"""
    # For testing, we'll create a mock token
    # In production, this would go through the actual login flow
    import jwt
    from core.config import settings

    token_data = {
        "sub": str(test_user.phone),
        "user_id": test_user.id,
        "role": test_user.role,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client: TestClient, db: Session) -> dict:
    """Get authentication headers for admin user"""
    admin_user = models.User(
        phone="7777777777",
        name="Admin User",
        email="admin@example.com",
        role=models.UserRole.ADMIN,
        district="Hyderabad",
        state="Telangana",
        trust_score=100.0,
        trust_coins=1000,
        trust_badge="Gold"
    )
    db.add(admin_user)
    db.commit()

    import jwt
    from core.config import settings

    token_data = {
        "sub": str(admin_user.phone),
        "user_id": admin_user.id,
        "role": admin_user.role,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return {"Authorization": f"Bearer {token}"}


# Test data fixtures
@pytest.fixture
def sample_product_data() -> dict:
    """Sample product creation data"""
    return {
        "name": "Handicraft Item",
        "description": "Beautiful handmade item",
        "category": "Handicrafts",
        "price": 500.00,
        "stock": 100,
        "min_order_quantity": 1,
        "unit": "piece",
        "images": ["item1.jpg"],
        "tags": ["handmade", "traditional"]
    }


@pytest.fixture
def sample_order_data(test_product: models.Product) -> dict:
    """Sample order creation data"""
    return {
        "items": [
            {
                "product_id": test_product.id,
                "quantity": 2
            }
        ],
        "shipping_address": "123 Test Street, Hyderabad, 500001",
        "payment_method": "UPI"
    }


# Async test support
@pytest.fixture
async def async_client(db: Session) -> AsyncGenerator[TestClient, None]:
    """Create async test client"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# Mark slow tests
slow = pytest.mark.slow


# Mark integration tests
integration = pytest.mark.integration


# Mark unit tests
unit = pytest.mark.unit
