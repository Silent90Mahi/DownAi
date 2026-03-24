"""
Data Generator Service - Comprehensive Dummy Data Generation
Generates 1000+ records for all models to populate the SHG platform
"""
import os
import random
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from .. import models

fake = Faker('en_IN')

# AP Districts for realistic geographic distribution
AP_DISTRICTS = [
    "Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna",
    "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam",
    "Vizianagaram", "West Godavari", "Kadapa", "Kakinada", "Tirupati",
    "Nandyal", "Eluru", "Amaravati", "Guntakal", "Rajahmundry",
    "Kothagudem", "Nalgonda", "Khammam", "Mahbubnagar", "Hyderabad"
]

# Product categories from original specification
PRODUCT_CATEGORIES = {
    "Handicrafts": [
        "Bamboo Crafts", "Pottery", "Embroidery", "Wood Carvings",
        "Jute Products", "Metal Crafts", "Paper Mache", "Leather Crafts",
        "Terracotta", "Cane Crafts", "Shell Crafts", "Coir Products"
    ],
    "Textiles": [
        "Sarees", "Fabrics", "Garments", "Handloom Items",
        "Traditional Dress Materials", "Bed Sheets", "Curtains", "Rugs",
        "Towels", "Napkins", "Bags", "Textile Accessories"
    ],
    "Food Products": [
        "Pickles", "Spices", "Snacks", "Sweets", "Papads",
        "Flours", "Oils", "Dry Fruits", "Processed Foods",
        "Beverages", "Confectionery", "Baked Goods", "Dairy Products"
    ],
    "Agricultural": [
        "Rice", "Pulses", "Oilseeds", "Spices", "Grains",
        "Vegetables", "Fruits", "Nuts", "Seeds", "Herbs",
        "Organic Products", "Forest Produce", "Honey", "Jaggery"
    ]
}

# SHG Names - Realistic Indian names
SHG_PREFIXES = [
    "Sri", "Srimathi", "Mahila", "Nari", "Jyothi", "Lakshmi", "Sakthi",
    "Durga", "Kala", "Sneha", "Pragathi", "Swathi", "Divya", "Priya"
]

SHG_SUFFIXES = [
    "Mahila Mandal", "SHG Federation", "Women's Group", "Self Help Group",
    "Produts", "Crafts", "Handicrafts", "Textiles", "Foods", "Agro"
]

# Buyer Types
BUYER_TYPES = [
    "Retailer", "Wholesaler", "Exporter", "Government", "Institutional",
    "Online Seller", "Department Store", "Supermarket", "Hotel", "Restaurant"
]

# Material Categories
MATERIAL_CATEGORIES = {
    "Raw Materials": ["Cotton", "Jute", "Bamboo", "Clay", "Wood", "Metal", "Leather"],
    "Packaging": ["Boxes", "Bags", "Paper", "Plastic", "Jute", "Cloth"],
    "Ingredients": ["Spices", "Flours", "Oils", "Preservatives", "Colors", "Dyes"],
    "Equipment": ["Looms", "Tools", "Machinery", "Kilns", "Containers"]
}

# Notification Types
NOTIFICATION_TYPES = [
    "order_update", "buyer_match", "demand_alert", "trust_update",
    "coin_earned", "community_alert", "bulk_request", "training",
    "exhibition", "payment_received", "product_approved", "reminder"
]


class DataGenerator:
    """Comprehensive data generator for SHG platform"""

    def __init__(self, db: Session):
        self.db = db
        self.generated_users = []
        self.generated_products = []
        self.generated_suppliers = []
        self.generated_buyers = []

    # ================================================
    # USER GENERATION
    # ================================================

    async def generate_users(self, count: int = 1000) -> List[models.User]:
        """Generate 1000+ users with realistic distribution"""
        print(f"Generating {count} users...")

        # Distribution: 70% SHGs, 10% Buyers, 10% Suppliers, 5% DPDs, 5% Admins
        users_data = []

        for i in range(count):
            role_distribution = random.random()
            if role_distribution < 0.70:
                role = "SHG"
                hierarchy = models.HierarchyLevel.SHG
            elif role_distribution < 0.80:
                role = "Buyer"
                hierarchy = models.HierarchyLevel.NONE
            elif role_distribution < 0.90:
                role = "Supplier"
                hierarchy = models.HierarchyLevel.NONE
            elif role_distribution < 0.95:
                role = "DPD"
                hierarchy = models.HierarchyLevel.TLF
            else:
                role = "Admin"
                hierarchy = models.HierarchyLevel.NONE

            # Generate realistic trust score (bell curve: 40-80)
            trust_score = min(max(random.gauss(60, 15), 0), 100)

            # Generate component scores
            quality_score = min(max(random.gauss(trust_score, 10), 0), 100)
            delivery_score = min(max(random.gauss(trust_score, 10), 0), 100)
            financial_score = min(max(random.gauss(trust_score, 10), 0), 100)
            community_score = min(max(random.gauss(trust_score, 10), 0), 100)
            sustainability_score = min(max(random.gauss(trust_score, 10), 0), 100)
            digital_score = min(max(random.gauss(trust_score, 10), 0), 100)

            # Calculate badge based on trust score
            if trust_score >= 80:
                badge = "Gold"
            elif trust_score >= 60:
                badge = "Silver"
            else:
                badge = "Bronze"

            # Generate name based on role
            if role == "SHG":
                prefix = random.choice(SHG_PREFIXES)
                suffix = random.choice(SHG_SUFFIXES)
                name = f"{prefix} {fake.first_name()} {suffix}"
            else:
                name = fake.company() if role in ["Buyer", "Supplier"] else fake.name()

            user_data = {
                "phone": f"+91{random.randint(7000000000, 9999999999)}",
                "phone_verified": True,
                "name": name,
                "email": f"user{i}_{fake.email()}" if random.random() > 0.3 else None,
                "role": models.UserRole(role),
                "hierarchy_level": hierarchy,
                "district": random.choice(AP_DISTRICTS),
                "state": "Andhra Pradesh",
                "address": fake.street_address(),
                "pincode": f"{random.randint(500000, 539999)}",
                "trust_score": trust_score,
                "trust_coins": random.randint(0, 500) if role == "SHG" else 0,
                "trust_badge": badge,
                "quality_score": quality_score,
                "delivery_score": delivery_score,
                "financial_score": financial_score,
                "community_score": community_score,
                "sustainability_score": sustainability_score,
                "digital_score": digital_score,
                "profile_image": f"https://i.pravatar.cc/150?u={i}",
                "language_preference": random.choice(["English", "Telugu", "Hindi", "Tamil"]),
                "low_bandwidth_mode": random.choice([True, False]),
                "notification_enabled": random.choice([True, False]),
                "created_at": fake.date_time_between(start_date='-2y', end_date='now'),
                "last_login": fake.date_time_between(start_date='-7d', end_date='now')
            }

            users_data.append(user_data)

        # Bulk create users
        users = []
        for user_data in users_data:
            user = models.User(**user_data)
            self.db.add(user)
            users.append(user)

        self.db.commit()

        # Create federation relationships
        shgs = [u for u in users if u.role == models.UserRole.SHG]
        slfs = [u for u in users if u.hierarchy_level == models.HierarchyLevel.SLF]
        tlfs = [u for u in users if u.hierarchy_level == models.HierarchyLevel.TLF]

        for shg in shgs[:min(len(shgs), len(slfs))]:
            if slfs:
                shg.federation_id = random.choice(slfs).id

        for slf in slfs:
            if tlfs:
                slf.federation_id = random.choice(tlfs).id

        self.db.commit()

        self.generated_users = users
        print(f"✓ Generated {len(users)} users")
        return users

    # ================================================
    # PRODUCT GENERATION
    # ================================================

    async def generate_products(self, count: int = 5000) -> List[models.Product]:
        """Generate 5000+ products across all categories"""
        print(f"Generating {count} products...")

        if not self.generated_users:
            shgs = self.db.query(models.User).filter(
                models.User.role == models.UserRole.SHG
            ).all()
        else:
            shgs = [u for u in self.generated_users if u.role == models.UserRole.SHG]

        products = []

        for i in range(count):
            # Select random category and subcategory
            category = random.choice(list(PRODUCT_CATEGORIES.keys()))
            subcategory = random.choice(PRODUCT_CATEGORIES[category])

            # Generate product name
            prefixes = ["Premium", "Handcrafted", "Traditional", "Organic", "Natural", "Authentic", "Homemade", "Fresh"]
            prefix = random.choice(prefixes) if random.random() > 0.5 else ""
            product_name = f"{prefix} {subcategory}".strip()

            # Generate realistic price (₹10 to ₹10000)
            base_price = random.randint(10, 10000)

            # Generate stock
            quantity = random.randint(0, 1000)
            status = "Active" if quantity > 0 else "Sold Out"

            # Generate images (use placeholder services)
            images = [f"https://picsum.photos/400/300?random={i+j}" for j in range(random.randint(1, 4))]

            product_data = {
                "name": product_name,
                "description": fake.text(max_nb_chars=500) if random.random() > 0.3 else f"High quality {subcategory} made by skilled artisans.",
                "category": category,
                "subcategory": subcategory,
                "price": base_price,
                "stock": quantity,
                "min_order_quantity": random.choice([1, 5, 10, 25, 50]),
                "unit": random.choice(["piece", "kg", "gram", "liter", "packet", "box", "set"]),
                "images": images,
                "thumbnail": images[0] if images else None,
                "status": models.ProductStatus(status),
                "is_featured": random.choice([True, False]) if random.random() > 0.8 else False,
                "quality_rating": round(random.uniform(3.0, 5.0), 1),
                "total_reviews": random.randint(0, 500),
                "trust_verified": random.choice([True, False]),
                "seller_id": random.choice(shgs).id,
                "tags": random.sample(["Handmade", "Organic", "Traditional", "Natural", "Premium"], random.randint(0, 3)),
                "created_at": fake.date_time_between(start_date='-1y', end_date='now')
            }

            product = models.Product(**product_data)
            self.db.add(product)
            products.append(product)

        self.db.commit()
        self.generated_products = products
        print(f"✓ Generated {len(products)} products")
        return products

    # ================================================
    # ORDER GENERATION
    # ================================================

    async def generate_orders(self, count: int = 10000) -> List[models.Order]:
        """Generate 10000+ orders with complete status history"""
        print(f"Generating {count} orders...")

        if not self.generated_users:
            buyers = [u for u in self.db.query(models.User).filter(
                models.User.role == models.UserRole.BUYER
            ).all()] or []
            shgs = [u for u in self.db.query(models.User).filter(
                models.User.role == models.UserRole.SHG
            ).all()]
        else:
            buyers = [u for u in self.generated_users if u.role == models.UserRole.BUYER]
            shgs = [u for u in self.generated_users if u.role == models.UserRole.SHG]

        if not self.generated_products:
            products = self.db.query(models.Product).limit(1000).all()
        else:
            products = self.generated_products[:1000]

        orders = []
        statuses = ["Placed", "Confirmed", "Shipped", "Delivered", "Cancelled"]
        payment_statuses = ["Pending", "Completed", "Failed", "Refunded"]
        payment_methods = ["UPI", "Bank Transfer", "Cash on Delivery", "Trust Coins"]

        for i in range(count):
            buyer = random.choice(buyers) if buyers else None
            seller = random.choice(shgs) if shgs else None
            product = random.choice(products) if products else None

            if not buyer or not seller or not product:
                continue

            # Generate realistic order progression
            status = random.choice(statuses)
            quantity = random.randint(1, 50)
            total_amount = product.price * quantity
            discount_amount = round(total_amount * random.uniform(0, 0.2), 2) if random.random() > 0.5 else 0
            tax_amount = round((total_amount - discount_amount) * 0.18, 2)
            final_amount = total_amount - discount_amount + tax_amount

            # Generate dates based on status
            created_at = fake.date_time_between(start_date='-6m', end_date='now')

            if status == "Confirmed":
                confirmed_at = created_at + timedelta(hours=random.randint(1, 24))
                shipped_at = None
                delivered_at = None
            elif status == "Shipped":
                confirmed_at = created_at + timedelta(hours=random.randint(1, 24))
                shipped_at = confirmed_at + timedelta(days=random.randint(1, 5))
                delivered_at = None
            elif status == "Delivered":
                confirmed_at = created_at + timedelta(hours=random.randint(1, 24))
                shipped_at = confirmed_at + timedelta(days=random.randint(1, 5))
                delivered_at = shipped_at + timedelta(days=random.randint(2, 7))
            elif status == "Cancelled":
                confirmed_at = None
                shipped_at = None
                delivered_at = created_at + timedelta(hours=random.randint(1, 48))
            else:
                confirmed_at = None
                shipped_at = None
                delivered_at = None

            order_data = {
                "order_number": f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{i:04d}",
                "buyer_id": buyer.id,
                "seller_id": seller.id,
                "total_amount": total_amount,
                "discount_amount": discount_amount,
                "tax_amount": tax_amount,
                "final_amount": final_amount,
                "order_status": models.OrderStatus(status),
                "payment_status": random.choice(payment_statuses),
                "payment_method": random.choice(payment_methods),
                "delivery_name": fake.name(),
                "delivery_phone": f"+91{random.randint(7000000000, 9999999999)}",
                "delivery_address": fake.street_address(),
                "delivery_city": fake.city(),
                "delivery_district": random.choice(AP_DISTRICTS),
                "delivery_pincode": f"{random.randint(500000, 539999)}",
                "tracking_number": f"TKN{random.randint(1000000000, 9999999999)}" if status in ["Shipped", "Delivered"] else None,
                "expected_delivery": (created_at + timedelta(days=random.randint(5, 15))).date() if created_at else None,
                "shipped_at": shipped_at,
                "delivered_at": delivered_at,
                "coins_used": random.randint(0, 100) if random.random() > 0.8 else 0,
                "created_at": created_at
            }

            order = models.Order(**order_data)
            self.db.add(order)
            self.db.flush()  # Flush to get the order.id
            orders.append(order)

            # Create order items
            order_item_data = {
                "order_id": order.id,
                "product_id": product.id,
                "product_name": product.name,
                "quantity": quantity,
                "unit_price": product.price,
                "total_price": total_amount
            }

            order_item = models.OrderItem(**order_item_data)
            self.db.add(order_item)

        self.db.commit()
        print(f"✓ Generated {len(orders)} orders")
        return orders

    # ================================================
    # SUPPLIER GENERATION
    # ================================================

    async def generate_suppliers(self, count: int = 500) -> List[models.Supplier]:
        """Generate 500+ suppliers"""
        print(f"Generating {count} suppliers...")

        # Get users with Supplier role
        supplier_users = self.db.query(models.User).filter(models.User.role == "Supplier").all()

        suppliers = []

        for i in range(count):
            business_name = fake.company()
            business_type = random.choice(["Proprietary", "Partnership", "LLP", "Cooperative"])

            # Assign product categories
            categories = []
            for _ in range(random.randint(1, 4)):
                category = random.choice(list(MATERIAL_CATEGORIES.keys()))
                if category not in categories:
                    categories.append(category)

            # Link to a supplier user if available, otherwise we'll need to create the user
            user_id = supplier_users[i].id if i < len(supplier_users) else None

            if user_id is None:
                print(f"  Warning: Not enough Supplier users. Need {count}, have {len(supplier_users)}")
                break

            supplier_data = {
                "user_id": user_id,
                "business_name": business_name,
                "gst_number": f"{random.randint(10, 99)}ABCDEFGHIJKLMNOPQRSTUVWXYZ{random.randint(1000, 9999)}"[:15],
                "business_type": business_type,
                "district": random.choice(AP_DISTRICTS),
                "state": "Andhra Pradesh",
                "address": fake.street_address(),
                "pincode": f"{random.randint(500000, 539999)}",
                "trust_score": min(max(random.gauss(65, 15), 0), 100),
                "rating": round(random.uniform(3.0, 5.0), 1),
                "total_reviews": random.randint(10, 500),
                "is_verified": random.choice([True, False]),
                "categories_supplied": categories,
                "service_areas": random.sample(AP_DISTRICTS, random.randint(3, 10))
            }

            supplier = models.Supplier(**supplier_data)
            self.db.add(supplier)
            suppliers.append(supplier)

        self.db.commit()
        self.generated_suppliers = suppliers
        print(f"✓ Generated {len(suppliers)} suppliers")
        return suppliers

    # ================================================
    # BUYER GENERATION
    # ================================================

    async def generate_buyers(self, count: int = 300) -> List[models.Buyer]:
        """Generate 300+ buyers"""
        print(f"Generating {count} buyers...")

        # Get users with Buyer role
        buyer_users = self.db.query(models.User).filter(models.User.role == "Buyer").all()

        buyers = []

        for i in range(count):
            buyer_type = random.choice(BUYER_TYPES)
            preferred_categories = random.sample(list(PRODUCT_CATEGORIES.keys()), random.randint(1, 3))

            # Link to a buyer user if available
            user_id = buyer_users[i].id if i < len(buyer_users) else None

            if user_id is None:
                print(f"  Warning: Not enough Buyer users. Need {count}, have {len(buyer_users)}")
                break

            buyer_data = {
                "user_id": user_id,
                "business_name": fake.company(),
                "buyer_type": buyer_type,
                "gem_registered": random.choice([True, False]) if random.random() > 0.8 else False,
                "gem_vendor_code": f"GEM{random.randint(10000, 99999)}" if random.random() > 0.8 else None,
                "ondc_registered": random.choice([True, False]) if random.random() > 0.7 else False,
                "esaras_registered": random.choice([True, False]) if random.random() > 0.9 else False,
                "preferred_categories": preferred_categories,
                "buying_capacity": random.choice(["Small (₹10K/month)", "Medium (₹50K/month)", "Large (₹1L/month)", "Enterprise (₹10L/month)"]),
                "district": random.choice(AP_DISTRICTS),
                "state": "Andhra Pradesh",
                "trust_score": min(max(random.gauss(65, 15), 0), 100),
                "rating": round(random.uniform(3.5, 5.0), 1),
                "total_orders": random.randint(5, 500)
            }

            buyer = models.Buyer(**buyer_data)
            self.db.add(buyer)
            buyers.append(buyer)

        self.db.commit()
        self.generated_buyers = buyers
        print(f"✓ Generated {len(buyers)} buyers")
        return buyers

    # ================================================
    # MATERIAL GENERATION
    # ================================================

    async def generate_materials(self, count: int = 2000) -> List[models.Material]:
        """Generate 2000+ raw materials"""
        print(f"Generating {count} materials...")

        if not self.generated_suppliers:
            suppliers = self.db.query(models.Supplier).all()
        else:
            suppliers = self.generated_suppliers

        materials = []

        for i in range(count):
            category = random.choice(list(MATERIAL_CATEGORIES.keys()))
            subcategory = random.choice(MATERIAL_CATEGORIES[category])

            supplier = random.choice(suppliers) if suppliers else None

            material_data = {
                "supplier_id": supplier.id if supplier else None,
                "name": f"{random.choice(['Premium', 'Standard', 'Economy'])} {subcategory}",
                "description": fake.text(max_nb_chars=300),
                "category": category,
                "subcategory": subcategory,
                "price_per_unit": round(random.uniform(10, 5000), 2),
                "unit": random.choice(["kg", "gram", "liter", "piece", "meter", "box", "bag"]),
                "min_order_quantity": random.randint(5, 100),
                "bulk_discount_available": random.choice([True, False]),
                "bulk_discount_percentage": round(random.uniform(5, 30), 1),
                "stock_available": random.randint(0, 10000),
                "is_available": random.choice([True, True, True, False]),
                "quality_grade": random.choice(["Premium", "Standard", "Economy"]),
                "is_organic": random.choice([True, False]),
                "certifications": random.sample(["FSSAI", "ISO", "Organic India", "BIS", "GMP"], random.randint(0, 3)),
                "district": supplier.district if supplier else random.choice(AP_DISTRICTS),
                "state": "Andhra Pradesh",
                "images": [f"https://picsum.photos/300/200?random={i}"],
                "thumbnail": f"https://picsum.photos/300/200?random={i}",
                "supplier_rating": round(random.uniform(3.5, 5.0), 1),
                "total_reviews": random.randint(5, 200)
            }

            material = models.Material(**material_data)
            self.db.add(material)
            materials.append(material)

        self.db.commit()
        print(f"✓ Generated {len(materials)} materials")
        return materials

    # ================================================
    # BULK REQUEST GENERATION
    # ================================================

    async def generate_bulk_requests(self, count: int = 100) -> List[models.BulkRequest]:
        """Generate 100+ bulk requests"""
        print(f"Generating {count} bulk requests...")

        if not self.generated_users:
            shgs = self.db.query(models.User).filter(
                models.User.role == models.UserRole.SHG
            ).all()
        else:
            shgs = [u for u in self.generated_users if u.role == models.UserRole.SHG]

        bulk_requests = []

        for i in range(count):
            creator = random.choice(shgs) if shgs else None

            request_data = {
                "request_number": f"BULK{datetime.now().strftime('%Y%m%d%H%M%S')}{i:04d}",
                "creator_id": creator.id if creator else None,
                "title": f"Bulk Purchase of {random.choice(['Raw Materials', 'Packaging', 'Spices', 'Grains', 'Textiles', 'Handicrafts'])}",
                "description": fake.text(max_nb_chars=300),
                "target_quantity": random.randint(100, 10000),
                "current_quantity": random.randint(0, 8000),
                "minimum_participants": random.randint(2, 20),
                "current_participants": random.randint(0, 15),
                "district": random.choice(AP_DISTRICTS),
                "serving_districts": random.sample(AP_DISTRICTS, random.randint(3, 8)),
                "expected_savings_percentage": round(random.uniform(10, 30), 1),
                "status": "Open",
                "expires_at": fake.date_time_between(start_date='now', end_date='+60d')
            }

            bulk_request = models.BulkRequest(**request_data)
            self.db.add(bulk_request)
            bulk_requests.append(bulk_request)

        self.db.commit()
        print(f"✓ Generated {len(bulk_requests)} bulk requests")
        return bulk_requests

    # ================================================
    # TRUST HISTORY GENERATION
    # ================================================

    async def generate_trust_history(self, count: int = 10000) -> List[models.TrustHistory]:
        """Generate 10000+ trust history entries"""
        print(f"Generating {count} trust history entries...")

        if not self.generated_users:
            users = self.db.query(models.User).all()
        else:
            users = self.generated_users

        trust_history = []

        for i in range(count):
            user = random.choice(users)

            # Calculate score change
            change_type = random.choice(["increase", "decrease"])
            change_amount = round(random.uniform(0.5, 5), 1)

            if change_type == "increase":
                previous_score = max(0, user.trust_score - change_amount)
                new_score = min(100, user.trust_score + change_amount)
            else:
                previous_score = min(100, user.trust_score + change_amount)
                new_score = max(0, user.trust_score - change_amount)

            # Determine reason
            reasons = [
                "order_complete", "on_time_delivery", "quality_product",
                "training_complete", "community_help", "certification",
                "late_delivery", "order_cancel", "poor_quality"
            ]
            reason = random.choice(reasons)

            # Determine badge change
            badge_change = random.choice([None, "Bronze to Silver", "Silver to Gold", "Gold to Silver", "Silver to Bronze"])

            history_data = {
                "user_id": user.id,
                "previous_score": previous_score,
                "new_score": new_score,
                "score_change": round(new_score - previous_score, 1),
                "reason": reason,
                "reference_type": random.choice(["order", "product", "training", "community"]),
                "reference_id": random.randint(1, 100000),
                "badge_change": badge_change,
                "created_at": fake.date_time_between(start_date='-1y', end_date='now')
            }

            entry = models.TrustHistory(**history_data)
            self.db.add(entry)
            trust_history.append(entry)

        self.db.commit()
        print(f"✓ Generated {len(trust_history)} trust history entries")
        return trust_history

    # ================================================
    # COIN TRANSACTION GENERATION
    # ================================================

    async def generate_coin_transactions(self, count: int = 50000) -> List[models.CoinTransaction]:
        """Generate 50000+ coin transactions"""
        print(f"Generating {count} coin transactions...")

        if not self.generated_users:
            users = self.db.query(models.User).all()
        else:
            users = self.generated_users

        transactions = []
        transaction_types = ["earned", "redeemed"]

        for i in range(count):
            user = random.choice(users)

            transaction_type = random.choice(transaction_types)

            if transaction_type == "earned":
                sources = [
                    "order_complete", "on_time_delivery", "positive_review",
                    "training_complete", "product_listed", "community_help",
                    "certification", "referral"
                ]
                amount = random.randint(1, 50)
            else:
                sources = [
                    "discount", "premium_listing", "promotion", "feature_access"
                ]
                amount = -random.randint(5, 100)

            balance_after = user.trust_coins + amount

            transaction_data = {
                "user_id": user.id,
                "amount": amount,
                "transaction_type": transaction_type,
                "source": random.choice(sources),
                "reference_type": random.choice(["order", "product", "training", "community"]),
                "reference_id": random.randint(1, 100000),
                "description": f"{transaction_type.title()} from {random.choice(sources)}",
                "balance_after": max(0, balance_after),
                "created_at": fake.date_time_between(start_date='-1y', end_date='now')
            }

            transaction = models.CoinTransaction(**transaction_data)
            self.db.add(transaction)
            transactions.append(transaction)

        self.db.commit()
        print(f"✓ Generated {len(transactions)} coin transactions")
        return transactions

    # ================================================
    # NOTIFICATION GENERATION
    # ================================================

    async def generate_notifications(self, count: int = 5000) -> List[models.Notification]:
        """Generate 5000+ notifications"""
        print(f"Generating {count} notifications...")

        if not self.generated_users:
            users = self.db.query(models.User).all()
        else:
            users = self.generated_users

        notifications = []

        for i in range(count):
            user = random.choice(users)
            notification_type = random.choice(NOTIFICATION_TYPES)

            titles = {
                "order_update": "Order Status Update",
                "buyer_match": "New Buyer Match Found",
                "demand_alert": "High Demand Alert",
                "trust_update": "Trust Score Updated",
                "coin_earned": "Coins Earned!",
                "community_alert": "Community Announcement",
                "bulk_request": "New Bulk Request",
                "training": "Training Opportunity",
                "exhibition": "Exhibition Invitation",
                "payment_received": "Payment Received",
                "product_approved": "Product Approved",
                "reminder": "Reminder"
            }

            messages = {
                "order_update": f"Your order status has been updated to {random.choice(['Confirmed', 'Shipped', 'Delivered'])}",
                "buyer_match": f"{random.randint(1, 10)} buyers matched for your products",
                "demand_alert": f"High demand for {random.choice(list(PRODUCT_CATEGORIES.keys()))} in your district",
                "trust_update": f"Your trust score is now {user.trust_score}",
                "coin_earned": f"You earned {random.randint(1, 50)} coins!",
                "community_alert": random.choice(["New training available", "Community meeting scheduled", "Alert from DPD"]),
                "bulk_request": f"Bulk request for {random.choice(['Raw Materials', 'Packaging', 'Spices', 'Grains'])} created in your district",
                "training": f"Free training on {random.choice(['Quality Standards', 'Packaging', 'Marketing'])}",
                "exhibition": f"Exhibition in {random.choice(AP_DISTRICTS)} - Register now",
                "payment_received": f"Payment of ₹{random.randint(1000, 50000)} received",
                "product_approved": "Your product has been approved",
                "reminder": random.choice(["Complete your profile", "Upload product images", "Update inventory"])
            }

            notification_data = {
                "user_id": user.id,
                "title": titles[notification_type],
                "message": messages[notification_type],
                "notification_type": notification_type,
                "reference_type": random.choice(["order", "product", "bulk_request", "training"]),
                "reference_id": random.randint(1, 100000),
                "action_url": random.choice([f"/orders/{random.randint(1, 10000)}", f"/products/{random.randint(1, 5000)}", "/profile", None]),
                "action_label": random.choice(["View", "Complete", "Update", None]),
                "is_read": random.choice([True, False, False, False]),
                "read_at": fake.date_time_between(start_date='-30d', end_date='now') if random.random() > 0.3 else None,
                "created_at": fake.date_time_between(start_date='-30d', end_date='now')
            }

            notification = models.Notification(**notification_data)
            self.db.add(notification)
            notifications.append(notification)

        self.db.commit()
        print(f"✓ Generated {len(notifications)} notifications")
        return notifications

    # ================================================
    # MARKET DATA GENERATION
    # ================================================

    async def generate_market_data(self, count: int = 500) -> List[models.MarketData]:
        """Generate 500+ market data records"""
        print(f"Generating {count} market data records...")

        market_data_list = []

        for i in range(count):
            category = random.choice(list(PRODUCT_CATEGORIES.keys()))
            district = random.choice(AP_DISTRICTS)

            # Generate demand metrics
            demand_levels = ["High", "Medium", "Low"]
            demand_level = random.choice(demand_levels)
            demand_score = {"High": random.randint(70, 100), "Medium": random.randint(40, 69), "Low": random.randint(10, 39)}[demand_level]

            # Generate pricing
            avg_price = random.randint(50, 5000)
            min_price = int(avg_price * 0.8)
            max_price = int(avg_price * 1.2)

            market_data_entry = {
                "category": category,
                "subcategory": random.choice(PRODUCT_CATEGORIES[category]),
                "district": district,
                "demand_level": demand_level,
                "demand_score": demand_score,
                "demand_trend": random.choice(["up", "down", "stable"]),
                "average_price": avg_price,
                "min_price": min_price,
                "max_price": max_price,
                "recommended_price_min": min_price,
                "recommended_price_max": max_price,
                "is_seasonal": random.choice([True, False, False]),
                "peak_season_start": f"{random.randint(1, 12):02d}" if random.random() > 0.7 else None,
                "peak_season_end": f"{random.randint(1, 12):02d}" if random.random() > 0.7 else None,
                "current_season": random.choice(["Peak", "Off", "Normal"]) if random.random() > 0.5 else None,
                "competitor_count": random.randint(5, 100),
                "market_saturation": random.choice(["Low", "Medium", "High"]),
                "date": fake.date_time_between(start_date='-30d', end_date='now')
            }

            market_data = models.MarketData(**market_data_entry)
            self.db.add(market_data)
            market_data_list.append(market_data)

        self.db.commit()
        print(f"✓ Generated {len(market_data_list)} market data records")
        return market_data_list

    # ================================================
    # ANALYTICS DATA GENERATION
    # ================================================

    async def generate_analytics_data(self, count: int = 365) -> List[models.AnalyticsData]:
        """Generate 365+ days of analytics data"""
        print(f"Generating {count} days of analytics data...")

        analytics_data = []

        for i in range(count):
            date = fake.date_time_between(start_date='-365d', end_date='now')
            district = random.choice(AP_DISTRICTS)

            # Generate realistic growth trends
            base_users = 100 + i  # Growth over time
            base_products = 50 + i * 2
            base_orders = 20 + i

            analytics_entry = {
                "date": date.date(),
                "district": district,
                "federation_id": None,
                "total_users": base_users + random.randint(-10, 20),
                "active_users": int(base_users * random.uniform(0.6, 0.9)),
                "new_users": random.randint(0, 10),
                "total_products": base_products + random.randint(-5, 15),
                "active_listings": int(base_products * random.uniform(0.7, 0.95)),
                "total_orders": base_orders + random.randint(-3, 10),
                "completed_orders": int(base_orders * random.uniform(0.8, 0.95)),
                "total_revenue": round((base_orders * random.randint(100, 1000)) * random.uniform(0.8, 1.2), 2),
                "avg_trust_score": round(random.uniform(50, 75), 1),
                "total_coins_earned": random.randint(50, 500),
                "total_coins_redeemed": random.randint(20, 300),
                "vaani_interactions": random.randint(10, 100),
                "bazaar_queries": random.randint(5, 50),
                "jodi_matches": random.randint(3, 30),
                "samagri_searches": random.randint(5, 40)
            }

            analytics = models.AnalyticsData(**analytics_entry)
            self.db.add(analytics)
            analytics_data.append(analytics)

        self.db.commit()
        print(f"✓ Generated {len(analytics_data)} analytics data records")
        return analytics_data

    # ================================================
    # CHAT HISTORY GENERATION
    # ================================================

    async def generate_chat_history(self, count: int = 1000) -> List[models.ChatHistory]:
        """Generate 1000+ chat history entries"""
        print(f"Generating {count} chat history entries...")

        if not self.generated_users:
            users = self.db.query(models.User).limit(500).all()
        else:
            users = self.generated_users[:500]

        chat_history = []

        agents = ["Vaani", "Bazaar Buddhi", "Jodi", "Samagri", "Vishwas", "Sampark"]

        for i in range(count):
            user = random.choice(users) if users else None

            # Generate conversation
            is_user_message = random.choice([True, False])

            if is_user_message:
                role = "user"
                agent_triggered = None
                content = fake.sentence() if random.random() > 0.5 else fake.catch_phrase()
            else:
                role = "assistant"
                agent_triggered = random.choice(agents)

                # Generate agent-specific responses
                responses = {
                    "Vaani": f"Hello! I'm Vaani, your voice assistant. How can I help you today?",
                    "Bazaar Buddhi": f"Based on current market analysis, demand for {random.choice(list(PRODUCT_CATEGORIES.keys()))} is {random.choice(['high', 'medium', 'low'])} in {random.choice(AP_DISTRICTS)}.",
                    "Jodi": f"I found {random.randint(1, 10)} potential buyers for your products. Would you like me to connect you?",
                    "Samagri": f"I found {random.randint(1, 10)} suppliers offering {random.choice(['Raw Materials', 'Quality Products', 'Bulk Items'])} at competitive prices.",
                    "Vishwas": f"Your trust score is currently {random.randint(50, 80)}. Keep delivering quality products to improve it!",
                    "Sampark": f"Your federation has {random.randint(10, 50)} active members. Total revenue this month: ₹{random.randint(10000, 100000)}."
                }
                content = responses[agent_triggered]

            chat_data = {
                "user_id": user.id if user else None,
                "session_id": f"session_{random.randint(10000, 99999)}",
                "role": role,
                "content": content,
                "agent_triggered": agent_triggered,
                "language": random.choice(["English", "Telugu", "Hindi", "Tamil"]),
                "created_at": fake.date_time_between(start_date='-30d', end_date='now')
            }

            chat = models.ChatHistory(**chat_data)
            self.db.add(chat)
            chat_history.append(chat)

        self.db.commit()
        print(f"✓ Generated {len(chat_history)} chat history entries")
        return chat_history

    # ================================================
    # BUYER REQUIREMENT GENERATION
    # ================================================

    async def generate_buyer_requirements(self, count: int = 500) -> List[models.BuyerRequirement]:
        """Generate 500+ buyer requirements"""
        print(f"Generating {count} buyer requirements...")

        if not self.generated_buyers:
            buyers = self.db.query(models.Buyer).all()
        else:
            buyers = self.generated_buyers

        requirements = []

        for i in range(count):
            buyer = random.choice(buyers) if buyers else None
            category = random.choice(list(PRODUCT_CATEGORIES.keys()))

            requirement_data = {
                "buyer_id": buyer.id if buyer else None,
                "title": f"Looking for {random.choice(['bulk', 'regular'])} {category} products",
                "description": fake.text(max_nb_chars=300),
                "category": category,
                "quantity": random.randint(10, 1000),
                "unit": random.choice(["pieces", "kg", "boxes", "sets"]),
                "budget_range_min": random.randint(1000, 50000),
                "budget_range_max": random.randint(50000, 500000),
                "status": random.choice(["Open", "Closed", "In Progress"]),
                "matched_shgs": [],
                "total_matches": random.randint(0, 50),
                "required_by": fake.date_time_between(start_date='now', end_date='+60d'),
                "expires_at": fake.date_time_between(start_date='now', end_date='+30d'),
                "created_at": fake.date_time_between(start_date='-30d', end_date='now')
            }

            requirement = models.BuyerRequirement(**requirement_data)
            self.db.add(requirement)
            requirements.append(requirement)

        self.db.commit()
        print(f"✓ Generated {len(requirements)} buyer requirements")
        return requirements


# ================================================
# SEED FUNCTIONS - Orchestrate data generation
# ================================================

async def seed_all_data(db: Session, users: int = 1000, products: int = 5000, orders: int = 10000):
    """Main function to seed all data"""
    print("=" * 60)
    print("SEEDING SHG PLATFORM DATA")
    print("=" * 60)

    generator = DataGenerator(db)

    try:
        # Phase 1: Users (must be first due to foreign keys)
        await generator.generate_users(users)

        # Phase 2: Core data
        await generator.generate_products(products)
        await generator.generate_suppliers(500)
        await generator.generate_buyers(300)

        # Phase 3: Materials and bulk requests
        await generator.generate_materials(2000)
        await generator.generate_bulk_requests(100)
        await generator.generate_buyer_requirements(500)

        # Phase 4: Orders and transactions
        await generator.generate_orders(orders)

        # Phase 5: Trust system data
        await generator.generate_trust_history(10000)
        await generator.generate_coin_transactions(50000)

        # Phase 6: Platform data
        await generator.generate_notifications(5000)
        await generator.generate_market_data(500)
        await generator.generate_analytics_data(365)
        await generator.generate_chat_history(1000)

        print("=" * 60)
        print("✓ DATA SEEDING COMPLETED SUCCESSFULLY")
        print("=" * 60)

        return {
            "users": users,
            "products": products,
            "orders": orders,
            "suppliers": 500,
            "buyers": 300,
            "materials": 2000,
            "bulk_requests": 100,
            "trust_history": 10000,
            "coin_transactions": 50000,
            "notifications": 5000,
            "market_data": 500,
            "analytics_data": 365,
            "chat_history": 1000
        }

    except Exception as e:
        print(f"✗ Error seeding data: {e}")
        raise


# ================================================
# STANDALONE SEED FUNCTIONS
# ================================================

async def seed_users_only(db: Session, count: int = 1000):
    """Generate only users"""
    generator = DataGenerator(db)
    await generator.generate_users(count)
    print(f"✓ Generated {count} users")


async def seed_products_only(db: Session, count: int = 5000):
    """Generate only products (requires users first)"""
    generator = DataGenerator(db)
    await generator.generate_products(count)
    print(f"✓ Generated {count} products")


async def seed_orders_only(db: Session, count: int = 10000):
    """Generate only orders (requires users and products first)"""
    generator = DataGenerator(db)
    await generator.generate_orders(count)
    print(f"✓ Generated {count} orders")
