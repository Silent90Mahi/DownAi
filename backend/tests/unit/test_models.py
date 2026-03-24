"""
Unit Tests for Models
Test model creation, validation, and business logic
"""
import pytest
from datetime import datetime
from app import models


class TestUserModel:
    @pytest.mark.unit
    def test_user_creation(self, db):
        user = models.User(
            phone="9876543210",
            name="John Doe",
            email="john@example.com",
            role=models.UserRole.SHG,
            district="Mumbai",
            state="Maharashtra"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.id is not None
        assert user.phone == "9876543210"
        assert user.name == "John Doe"
        assert user.role == models.UserRole.SHG
        assert user.trust_score == 50.0
        assert user.trust_coins == 0

    @pytest.mark.unit
    def test_user_trust_badge_assignment(self, db):
        user = models.User(
            phone="9876543211",
            name="Jane Doe",
            role=models.UserRole.SHG,
            trust_score=85.0
        )
        
        db.add(user)
        db.commit()
        
        assert user.trust_badge == "Gold"

    @pytest.mark.unit
    def test_user_default_values(self, db):
        user = models.User(
            phone="9876543212",
            name="Test User",
            role=models.UserRole.BUYER
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.language_preference == "English"
        assert user.low_bandwidth_mode == False
        assert user.notification_enabled == True


class TestProductModel:
    @pytest.mark.unit
    def test_product_creation(self, db, test_seller):
        product = models.Product(
            seller_id=test_seller.id,
            name="Handcrafted Bag",
            description="Eco-friendly jute bag",
            category="Handicrafts",
            price=299.00,
            stock=25,
            unit="piece"
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        assert product.id is not None
        assert product.name == "Handcrafted Bag"
        assert product.status == models.ProductStatus.ACTIVE
        assert product.min_order_quantity == 1

    @pytest.mark.unit
    def test_product_stock_management(self, db, test_product):
        initial_stock = test_product.stock
        
        test_product.stock -= 5
        db.commit()
        db.refresh(test_product)
        
        assert test_product.stock == initial_stock - 5

    @pytest.mark.unit
    def test_product_inactive_status(self, db, test_seller):
        product = models.Product(
            seller_id=test_seller.id,
            name="Out of Stock Item",
            category="Handicrafts",
            price=100.00,
            stock=0,
            status=models.ProductStatus.INACTIVE
        )
        
        db.add(product)
        db.commit()
        
        assert product.status == models.ProductStatus.INACTIVE


class TestOrderModel:
    @pytest.mark.unit
    def test_order_creation(self, db, test_user, test_seller):
        order = models.Order(
            buyer_id=test_user.id,
            seller_id=test_seller.id,
            order_number="ORD-TEST-001",
            final_amount=500.00,
            shipping_address="123 Test Address",
            payment_method="UPI"
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        assert order.id is not None
        assert order.order_status == models.OrderStatus.PENDING
        assert order.payment_status == models.PaymentStatus.PENDING

    @pytest.mark.unit
    def test_order_status_transition(self, db, test_order):
        assert test_order.order_status == models.OrderStatus.CONFIRMED
        
        test_order.order_status = models.OrderStatus.SHIPPED
        db.commit()
        
        assert test_order.order_status == models.OrderStatus.SHIPPED

    @pytest.mark.unit
    def test_order_total_calculation(self, db, test_order):
        items = db.query(models.OrderItem).filter(
            models.OrderItem.order_id == test_order.id
        ).all()
        
        total = sum(item.total_price for item in items)
        assert total == test_order.final_amount
