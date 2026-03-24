from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text, JSON, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime
import enum
from .database import Base

class UserRole(str, enum.Enum):
    SHG = "SHG"
    ADMIN = "Admin"
    DPD = "DPD"
    BUYER = "Buyer"
    SUPPLIER = "Supplier"

class HierarchyLevel(str, enum.Enum):
    SHG = "SHG"
    SLF = "SLF"
    TLF = "TLF"
    NONE = "None"

class OrderStatus(str, enum.Enum):
    PLACED = "Placed"
    CONFIRMED = "Confirmed"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"

class PaymentStatus(str, enum.Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"
    REFUNDED = "Refunded"

class ProductStatus(str, enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    SOLD_OUT = "Sold Out"
    INACTIVE = "Inactive"

# ============================================================================
# USER MODEL
# ============================================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(15), unique=True, index=True, nullable=False)
    phone_verified = Column(Boolean, default=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.SHG, nullable=False)
    hierarchy_level = Column(SQLEnum(HierarchyLevel), default=HierarchyLevel.SHG)

    # Location and Profile
    district = Column(String(50))
    state = Column(String(50), default="Andhra Pradesh")
    address = Column(Text)
    pincode = Column(String(10))
    profile_image = Column(String(500))
    language_preference = Column(String(10), default="English")

    # Trust System
    trust_score = Column(Float, default=50.0)
    trust_coins = Column(Integer, default=0)
    trust_badge = Column(String(20), default="Bronze")

    # Trust Score Components
    quality_score = Column(Float, default=50.0)
    delivery_score = Column(Float, default=50.0)
    financial_score = Column(Float, default=50.0)
    community_score = Column(Float, default=50.0)
    sustainability_score = Column(Float, default=50.0)
    digital_score = Column(Float, default=50.0)

    # Federation Links
    federation_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Settings
    low_bandwidth_mode = Column(Boolean, default=False)
    notification_enabled = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    products = relationship("Product", back_populates="seller", cascade="all, delete-orphan")
    seller_transactions = relationship("Transaction", foreign_keys="Transaction.seller_id", back_populates="seller")
    buyer_transactions = relationship("Transaction", foreign_keys="Transaction.buyer_id", back_populates="buyer")
    orders_as_buyer = relationship("Order", foreign_keys="Order.buyer_id", back_populates="buyer")
    orders_as_seller = relationship("Order", foreign_keys="Order.seller_id", back_populates="seller")
    trust_history = relationship("TrustHistory", back_populates="user", cascade="all, delete-orphan")
    coin_transactions = relationship("CoinTransaction", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="actor", cascade="all, delete-orphan")
    children = relationship("User", backref="parent", remote_side=[id])
    bulk_requests = relationship("BulkRequest", back_populates="creator", cascade="all, delete-orphan")
    supplier_profile = relationship("Supplier", back_populates="user", uselist=False, cascade="all, delete-orphan")
    buyer_profile = relationship("Buyer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

# ============================================================================
# PRODUCT MODEL
# ============================================================================
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True, nullable=False)
    description = Column(Text)
    category = Column(String(50), index=True, nullable=False)
    subcategory = Column(String(50))
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    min_order_quantity = Column(Integer, default=1)
    unit = Column(String(20), default="piece")

    # Images
    images = Column(JSON)
    thumbnail = Column(String(500))

    # Status and Metadata
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.DRAFT, index=True)
    is_featured = Column(Boolean, default=False)
    tags = Column(JSON)

    # Trust and Quality
    quality_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    trust_verified = Column(Boolean, default=False)

    # Seller Info
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Composite indexes for common query patterns
    __table_args__ = (
        Index('ix_products_category_status', 'category', 'status'),
        Index('ix_products_seller_status', 'seller_id', 'status'),
        Index('ix_products_status_created', 'status', 'created_at'),
        Index('ix_products_category_price', 'category', 'price'),
    )

    # Relationships
    seller = relationship("User", back_populates="products")
    transaction_items = relationship("TransactionItem", back_populates="product")

# ============================================================================
# TRANSACTION MODEL
# ============================================================================
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    buyer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Integer)
    total_amount = Column(Float)
    status = Column(String(50))

    # Payment
    payment_id = Column(String(100))
    payment_method = Column(String(50))
    payment_status = Column(String(50), default="Pending")

    # Delivery
    delivery_address = Column(Text)
    delivery_city = Column(String(50))
    delivery_district = Column(String(50))
    delivery_pincode = Column(String(10))
    delivery_status = Column(String(50), default="Not Shipped")
    expected_delivery = Column(DateTime(timezone=True))
    actual_delivery = Column(DateTime(timezone=True))

    # Trust Impact
    trust_score_impact = Column(Float, default=0.0)
    coins_earned = Column(Integer, default=0)

    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product")
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="buyer_transactions")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="seller_transactions")

# ============================================================================
# ORDER MODEL
# ============================================================================
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)

    # Participants
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Order Details
    total_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)

    # Status
    order_status = Column(SQLEnum(OrderStatus), default=OrderStatus.PLACED, index=True)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, index=True)

    # Payment
    payment_method = Column(String(50))
    payment_id = Column(String(100))
    coins_used = Column(Integer, default=0)

    # Delivery
    delivery_name = Column(String(100))
    delivery_phone = Column(String(15))
    delivery_address = Column(Text, nullable=False)
    delivery_city = Column(String(50), nullable=False)
    delivery_district = Column(String(50), nullable=False)
    delivery_pincode = Column(String(10), nullable=False)
    delivery_notes = Column(Text)

    # Tracking
    tracking_number = Column(String(100))
    courier_partner = Column(String(100))
    expected_delivery = Column(DateTime(timezone=True))
    shipped_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))

    # Composite indexes for common query patterns
    __table_args__ = (
        Index('ix_orders_buyer_status', 'buyer_id', 'order_status'),
        Index('ix_orders_seller_status', 'seller_id', 'order_status'),
        Index('ix_orders_status_created', 'order_status', 'created_at'),
        Index('ix_orders_payment_status', 'payment_status'),
    )

    # Trust Impact
    trust_score_change = Column(Float, default=0.0)
    coins_earned = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="orders_as_buyer")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="orders_as_seller")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

# ============================================================================
# ORDER ITEM MODEL
# ============================================================================
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

# ============================================================================
# TRANSACTION ITEM MODEL
# ============================================================================
class TransactionItem(Base):
    __tablename__ = "transaction_items"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price_at_time = Column(Float)

    # Relationships
    transaction = relationship("Transaction")
    product = relationship("Product", back_populates="transaction_items")

# ============================================================================
# SUPPLIER MODEL
# ============================================================================
class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_name = Column(String(200), nullable=False)
    gst_number = Column(String(15))
    business_type = Column(String(50))

    # Location
    district = Column(String(50))
    state = Column(String(50), default="Andhra Pradesh")
    address = Column(Text)
    pincode = Column(String(10))

    # Trust
    trust_score = Column(Float, default=50.0)
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)

    # Categories
    categories_supplied = Column(JSON)
    service_areas = Column(JSON)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="supplier_profile")
    materials = relationship("Material", back_populates="supplier", cascade="all, delete-orphan")

# ============================================================================
# BUYER MODEL
# ============================================================================
class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_name = Column(String(200), nullable=False)
    buyer_type = Column(String(50))

    # Government/Portal info
    gem_registered = Column(Boolean, default=False)
    gem_vendor_code = Column(String(50))
    ondc_registered = Column(Boolean, default=False)
    esaras_registered = Column(Boolean, default=False)

    # Requirements
    preferred_categories = Column(JSON)
    buying_capacity = Column(String(50))

    # Trust
    trust_score = Column(Float, default=50.0)
    rating = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)

    # Location
    district = Column(String(50))
    state = Column(String(50), default="Andhra Pradesh")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="buyer_profile")
    requirements = relationship("BuyerRequirement", back_populates="buyer", cascade="all, delete-orphan")

# ============================================================================
# BUYER REQUIREMENT MODEL
# ============================================================================
class BuyerRequirement(Base):
    __tablename__ = "buyer_requirements"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit = Column(String(20), default="piece")
    budget_range_min = Column(Float)
    budget_range_max = Column(Float)
    required_by = Column(DateTime(timezone=True))

    # Status
    status = Column(String(50), default="Open")

    # Matching
    matched_shgs = Column(JSON)
    total_matches = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))

    # Relationships
    buyer = relationship("Buyer", back_populates="requirements")

# ============================================================================
# MATERIAL MODEL
# ============================================================================
class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(50), index=True)
    subcategory = Column(String(50))

    # Pricing
    price_per_unit = Column(Float, nullable=False)
    unit = Column(String(20))
    min_order_quantity = Column(Integer, default=1)
    bulk_discount_available = Column(Boolean, default=False)
    bulk_discount_percentage = Column(Float, default=0.0)

    # Availability
    stock_available = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)

    # Quality
    quality_grade = Column(String(20))
    is_organic = Column(Boolean, default=False)
    certifications = Column(JSON)

    # Location
    district = Column(String(50))
    state = Column(String(50), default="Andhra Pradesh")

    # Images
    images = Column(JSON)
    thumbnail = Column(String(500))

    # Trust
    supplier_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    supplier = relationship("Supplier", back_populates="materials")
    bulk_requests = relationship("BulkRequestItem", back_populates="material")

# ============================================================================
# BULK REQUEST MODEL
# ============================================================================
class BulkRequest(Base):
    __tablename__ = "bulk_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String(50), unique=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)

    # Status
    status = Column(String(50), default="Open")

    # Group Details
    target_quantity = Column(Integer, nullable=False)
    current_quantity = Column(Integer, default=0)
    minimum_participants = Column(Integer, default=2)
    current_participants = Column(Integer, default=0)

    # Pricing
    expected_savings_percentage = Column(Float, default=0.0)

    # Location
    district = Column(String(50))
    serving_districts = Column(JSON)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))

    # Relationships
    creator = relationship("User", back_populates="bulk_requests")
    items = relationship("BulkRequestItem", back_populates="bulk_request", cascade="all, delete-orphan")
    participants = relationship("BulkRequestParticipant", back_populates="bulk_request", cascade="all, delete-orphan")

# ============================================================================
# BULK REQUEST ITEM MODEL
# ============================================================================
class BulkRequestItem(Base):
    __tablename__ = "bulk_request_items"

    id = Column(Integer, primary_key=True, index=True)
    bulk_request_id = Column(Integer, ForeignKey("bulk_requests.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    material_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False)
    target_price = Column(Float)

    # Relationships
    bulk_request = relationship("BulkRequest", back_populates="items")
    material = relationship("Material", back_populates="bulk_requests")

# ============================================================================
# BULK REQUEST PARTICIPANT MODEL
# ============================================================================
class BulkRequestParticipant(Base):
    __tablename__ = "bulk_request_participants"

    id = Column(Integer, primary_key=True, index=True)
    bulk_request_id = Column(Integer, ForeignKey("bulk_requests.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(50), default="Committed")

    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    bulk_request = relationship("BulkRequest", back_populates="participants")

# ============================================================================
# TRUST HISTORY MODEL
# ============================================================================
class TrustHistory(Base):
    __tablename__ = "trust_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Score Changes
    previous_score = Column(Float, nullable=False)
    new_score = Column(Float, nullable=False)
    score_change = Column(Float, nullable=False)

    # Component Scores
    quality_score = Column(Float)
    delivery_score = Column(Float)
    financial_score = Column(Float)
    community_score = Column(Float)
    sustainability_score = Column(Float)
    digital_score = Column(Float)

    # Reason
    reason = Column(String(100), nullable=False)
    reference_type = Column(String(50))
    reference_id = Column(Integer)

    # Badge Changes
    badge_change = Column(String(50))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="trust_history")

# ============================================================================
# COIN TRANSACTION MODEL
# ============================================================================
class CoinTransaction(Base):
    __tablename__ = "coin_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Transaction Details
    amount = Column(Integer, nullable=False)
    transaction_type = Column(String(50), nullable=False)
    source = Column(String(100), nullable=False)

    # Reference
    reference_type = Column(String(50))
    reference_id = Column(Integer)
    description = Column(Text)

    # Balance
    balance_after = Column(Integer, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="coin_transactions")

# ============================================================================
# AUDIT LOG MODEL
# ============================================================================
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(500))

    # Trust & Compliance
    is_compliance_violation = Column(Boolean, default=False)
    severity = Column(String(20))

    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    actor = relationship("User", back_populates="audit_logs")

# ============================================================================
# MARKET DATA MODEL
# ============================================================================
class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), index=True, nullable=False)
    subcategory = Column(String(50))
    district = Column(String(50), index=True)

    # Demand Data
    demand_level = Column(String(20))
    demand_score = Column(Float)
    demand_trend = Column(String(20))

    # Pricing Data
    average_price = Column(Float)
    min_price = Column(Float)
    max_price = Column(Float)
    recommended_price_min = Column(Float)
    recommended_price_max = Column(Float)

    # Seasonal Data
    is_seasonal = Column(Boolean, default=False)
    peak_season_start = Column(String(20))
    peak_season_end = Column(String(20))
    current_season = Column(String(20))

    # Competition
    competitor_count = Column(Integer, default=0)
    market_saturation = Column(String(20))

    # Timestamps
    date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# ============================================================================
# ANALYTICS DATA MODEL
# ============================================================================
class AnalyticsData(Base):
    __tablename__ = "analytics_data"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), index=True)
    district = Column(String(50), index=True)
    federation_id = Column(Integer, index=True)

    # User Metrics
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)

    # Product Metrics
    total_products = Column(Integer, default=0)
    active_listings = Column(Integer, default=0)

    # Transaction Metrics
    total_orders = Column(Integer, default=0)
    completed_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)

    # Trust Metrics
    avg_trust_score = Column(Float, default=50.0)
    total_coins_earned = Column(Integer, default=0)
    total_coins_redeemed = Column(Integer, default=0)

    # Agent Metrics
    vaani_interactions = Column(Integer, default=0)
    bazaar_queries = Column(Integer, default=0)
    jodi_matches = Column(Integer, default=0)
    samagri_searches = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ============================================================================
# NOTIFICATION MODEL
# ============================================================================
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Notification Details
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)

    # Reference
    reference_type = Column(String(50))
    reference_id = Column(Integer)

    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))

    # Action
    action_url = Column(String(500))
    action_label = Column(String(50))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")

# ============================================================================
# CHAT HISTORY MODEL
# ============================================================================
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), index=True)

    # Message Details
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    agent_triggered = Column(String(50))

    # Audio
    audio_url = Column(String(500))
    transcription = Column(Text)

    # Language
    language = Column(String(10), default="English")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")


class SyncStatus(str, enum.Enum):
    PENDING = "pending"
    SYNCED = "synced"
    CONFLICT = "conflict"


class SyncAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class SyncRecord(Base):
    __tablename__ = "sync_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(SQLEnum(SyncAction), nullable=False)
    data = Column(JSON, nullable=False)
    server_data = Column(JSON)
    sync_status = Column(SQLEnum(SyncStatus), default=SyncStatus.PENDING, index=True)
    client_timestamp = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    synced_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index('ix_sync_records_user_status', 'user_id', 'sync_status'),
        Index('ix_sync_records_entity', 'entity_type', 'entity_id'),
        Index('ix_sync_records_created', 'created_at'),
    )

    user = relationship("User")
