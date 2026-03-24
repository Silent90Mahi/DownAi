from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ============================================================================
# COMMON SCHEMAS
# ============================================================================
class MessageResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    detail: str
    success: bool = False

# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400

class TokenData(BaseModel):
    phone: Optional[str] = None
    role: Optional[str] = None

class OTPRequest(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    otp: str
    device_info: Optional[Dict[str, Any]] = None

class UserCreate(BaseModel):
    phone: str
    name: str
    role: str = "SHG"
    password: Optional[str] = None
    email: Optional[str] = None
    district: Optional[str] = None
    language_preference: str = "English"

class UserLogin(BaseModel):
    phone: str
    password: Optional[str] = None  # For mock auth

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    language_preference: Optional[str] = None
    low_bandwidth_mode: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    phone: str
    name: str
    email: Optional[str]
    role: str
    hierarchy_level: Optional[str]
    district: Optional[str]
    state: str
    profile_image: Optional[str]
    language_preference: str
    trust_score: float
    trust_coins: int
    trust_badge: str
    quality_score: float
    delivery_score: float
    financial_score: float
    community_score: float
    sustainability_score: float
    digital_score: float
    low_bandwidth_mode: bool
    notification_enabled: bool
    federation_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# PRODUCT SCHEMAS
# ============================================================================
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    price: float
    stock: int
    min_order_quantity: int = 1
    unit: str = "piece"
    images: Optional[List[str]] = []
    tags: Optional[List[str]] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    min_order_quantity: Optional[int] = None
    unit: Optional[str] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str
    subcategory: Optional[str]
    price: float
    stock: int
    min_order_quantity: int
    unit: str
    images: Optional[List[str]]
    thumbnail: Optional[str]
    status: str
    is_featured: bool
    tags: Optional[List[str]]
    quality_rating: float
    total_reviews: int
    trust_verified: bool
    seller_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# ORDER SCHEMAS
# ============================================================================
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    delivery_name: str
    delivery_phone: str
    delivery_address: str
    delivery_city: str
    delivery_district: str
    delivery_pincode: str
    delivery_notes: Optional[str] = None
    payment_method: str = "UPI"
    coins_used: int = 0

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_price: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    order_number: str
    buyer_id: int
    seller_id: int
    total_amount: float
    discount_amount: float
    tax_amount: float
    final_amount: float
    order_status: str
    payment_status: str
    payment_method: str
    payment_id: Optional[str]
    coins_used: int
    delivery_name: str
    delivery_phone: str
    delivery_address: str
    delivery_city: str
    delivery_district: str
    delivery_pincode: str
    delivery_notes: Optional[str]
    tracking_number: Optional[str]
    courier_partner: Optional[str]
    expected_delivery: Optional[datetime]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    trust_score_change: float
    coins_earned: int
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True

# ============================================================================
# MARKET INTELLIGENCE SCHEMAS (Bazaar Buddhi)
# ============================================================================
class MarketAnalysisRequest(BaseModel):
    product_name: str
    category: str
    district: str
    price: Optional[float] = None

class MarketAnalysisResponse(BaseModel):
    product_name: str
    category: str
    district: str
    demand_level: str  # High, Medium, Low
    demand_score: float  # 0-100
    demand_trend: str  # Rising, Stable, Falling
    recommended_price_min: float
    recommended_price_max: float
    average_market_price: float
    competitor_count: int
    market_saturation: str
    is_seasonal: bool
    peak_season: Optional[str] = None
    best_selling_districts: List[str]
    suggestions: List[str]

class PriceSuggestionRequest(BaseModel):
    product_name: str
    category: str
    quality: str = "Standard"
    district: str
    cost_price: float

class PriceSuggestionResponse(BaseModel):
    product_name: str
    recommended_price_min: float
    recommended_price_max: float
    recommended_price: float
    profit_margin_min: float
    profit_margin_max: float
    reasoning: str
    market_factors: List[str]

# ============================================================================
# BUYER MATCHING SCHEMAS (Jodi)
# ============================================================================
class BuyerMatchRequest(BaseModel):
    product_id: int
    quantity: int
    price: float
    district: str

class BuyerMatchResponse(BaseModel):
    buyer_id: int
    business_name: str
    buyer_type: str
    district: str
    rating: float
    trust_score: float
    offer_price: float
    quantity_requested: int
    requirements: str
    gem_registered: bool
    ondc_registered: bool
    match_score: float
    contact_allowed: bool

class BuyerRequirementResponse(BaseModel):
    id: int
    buyer_id: int
    title: str
    description: str
    category: str
    quantity: int
    unit: str
    budget_range_min: Optional[float]
    budget_range_max: Optional[float]
    required_by: Optional[datetime]
    status: str
    created_at: datetime

# ============================================================================
# SUPPLIER/MATERIAL SCHEMAS (Samagri)
# ============================================================================
class SupplierResponse(BaseModel):
    id: int
    business_name: str
    district: str
    rating: float
    trust_score: float
    total_reviews: int
    is_verified: bool
    categories_supplied: List[str]
    service_areas: List[str]

    class Config:
        from_attributes = True

class MaterialResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str
    subcategory: Optional[str]
    price_per_unit: float
    unit: str
    min_order_quantity: int
    bulk_discount_available: bool
    bulk_discount_percentage: float
    stock_available: int
    is_available: bool
    quality_grade: Optional[str]
    is_organic: bool
    certifications: Optional[List[str]]
    district: str
    images: Optional[List[str]]
    supplier: SupplierResponse

    class Config:
        from_attributes = True

class MaterialSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    district: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    is_organic: Optional[bool] = None

class BulkRequestCreate(BaseModel):
    title: str
    description: str
    materials: List[Dict[str, Any]]
    target_quantity: int
    district: str
    serving_districts: List[str]
    expires_in_days: int = 30

# ============================================================================
# TRUST SCHEMAS (Vishwas)
# ============================================================================
class TrustScoreBreakdown(BaseModel):
    overall_score: float
    quality_score: float
    delivery_score: float
    financial_score: float
    community_score: float
    sustainability_score: float
    digital_score: float
    badge: str

class TrustHistoryResponse(BaseModel):
    id: int
    previous_score: float
    new_score: float
    score_change: float
    reason: str
    reference_type: Optional[str]
    reference_id: Optional[int]
    badge_change: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class CoinTransactionResponse(BaseModel):
    id: int
    amount: int
    transaction_type: str
    source: str
    description: Optional[str]
    reference_type: Optional[str]
    reference_id: Optional[int]
    balance_after: int
    created_at: datetime

    class Config:
        from_attributes = True

class CoinWalletResponse(BaseModel):
    balance: int
    total_earned: int
    total_spent: int
    recent_transactions: List[CoinTransactionResponse]

# ============================================================================
# COMMUNITY SCHEMAS (Sampark)
# ============================================================================
class FederationStatsResponse(BaseModel):
    federation_id: int
    federation_level: str
    total_members: int
    active_members: int
    total_products: int
    total_revenue: float
    avg_trust_score: float
    top_performers: List[Dict[str, Any]]

class CommunityMemberResponse(BaseModel):
    id: int
    name: str
    phone: str
    district: str
    trust_score: float
    trust_badge: str
    products_count: int
    revenue: float

class CommunityAlertCreate(BaseModel):
    title: str
    message: str
    target_level: str  # SHG, SLF, TLF, All
    district: Optional[str] = None

# ============================================================================
# VOICE/CHAT SCHEMAS (Vaani)
# ============================================================================
class ChatRequest(BaseModel):
    query: str
    language: str = "English"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    agent_triggered: str
    language: str
    session_id: str
    is_voice_response: bool = False
    audio_url: Optional[str] = None

class VoiceTranscribeRequest(BaseModel):
    audio_data: str  # Base64 encoded
    language: str = "auto"

class VoiceTranscribeResponse(BaseModel):
    transcription: str
    detected_language: str
    confidence: float

class VoiceSynthesizeRequest(BaseModel):
    text: str
    language: str = "English"
    voice: str = "alloy"

class VoiceSynthesizeResponse(BaseModel):
    audio_url: str
    duration_seconds: float

# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================
class DashboardStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_products: int
    active_listings: int
    total_orders: int
    completed_orders: int
    total_revenue: float
    avg_trust_score: float
    total_coins_earned: int
    total_coins_redeemed: int

class DistrictStatsResponse(BaseModel):
    district: str
    total_users: int
    total_products: int
    total_orders: int
    total_revenue: float
    avg_trust_score: float

class UserAnalyticsResponse(BaseModel):
    user_id: int
    total_products: int
    total_orders_sold: int
    total_orders_bought: int
    total_revenue: float
    total_purchases: float
    trust_score: float
    trust_coins: int
    completion_rate: float
    avg_rating: float

# ============================================================================
# PAYMENT SCHEMAS
# ============================================================================
class PaymentInitiateRequest(BaseModel):
    order_id: int
    amount: float
    payment_method: str = "UPI"
    use_coins: bool = False
    coins_to_use: int = 0

class PaymentInitiateResponse(BaseModel):
    payment_id: str
    amount: float
    qr_code_url: Optional[str] = None
    upi_link: Optional[str] = None
    status: str
    expires_at: datetime

class PaymentStatusResponse(BaseModel):
    payment_id: str
    status: str
    amount: float
    payment_method: str
    transaction_id: Optional[str] = None
    completed_at: Optional[datetime] = None

# ============================================================================
# NOTIFICATION SCHEMAS
# ============================================================================
class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    notification_type: str
    reference_type: Optional[str]
    reference_id: Optional[int]
    is_read: bool
    action_url: Optional[str]
    action_label: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# AUDIT LOG SCHEMAS
# ============================================================================
class AuditLogResponse(BaseModel):
    id: int
    actor_id: int
    actor_name: str
    action: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    details: Optional[Dict[str, Any]]
    is_compliance_violation: bool
    severity: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

# ============================================================================
# REPORT SCHEMAS
# ============================================================================
class ReportGenerateRequest(BaseModel):
    report_type: str  # user, federation, district, market
    filters: Dict[str, Any] = {}
    date_range: Optional[Dict[str, str]] = None
    format: str = "pdf"  # pdf, csv

class ReportResponse(BaseModel):
    report_id: str
    report_type: str
    status: str
    download_url: Optional[str] = None
    generated_at: datetime

# ============================================================================
# WEBSOCKET & NOTIFICATION SCHEMAS
# ============================================================================
class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str = "info"  # info, success, warning, error
    action_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BroadcastCreate(BaseModel):
    title: str
    message: str
    notification_type: Optional[str] = "info"
    target_type: str  # all, users, room
    target_users: Optional[List[int]] = None
    target_room: Optional[str] = None
    timestamp: Optional[str] = None


class SyncAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class SyncStatus(str, Enum):
    PENDING = "pending"
    SYNCED = "synced"
    CONFLICT = "conflict"


class ResolutionType(str, Enum):
    SERVER_WINS = "server_wins"
    CLIENT_WINS = "client_wins"
    MERGE = "merge"


class SyncRecordInput(BaseModel):
    entity_type: str
    entity_id: int
    action: SyncAction
    data: Dict[str, Any]
    client_timestamp: Optional[datetime] = None


class SyncRecordResponse(BaseModel):
    id: int
    user_id: int
    entity_type: str
    entity_id: int
    action: str
    data: Dict[str, Any]
    server_data: Optional[Dict[str, Any]]
    sync_status: str
    client_timestamp: Optional[datetime]
    created_at: datetime
    synced_at: Optional[datetime]

    class Config:
        from_attributes = True


class SyncUploadRequest(BaseModel):
    records: List[SyncRecordInput]


class SyncUploadDetail(BaseModel):
    record_id: int
    entity_type: str
    entity_id: int
    status: str
    message: Optional[str] = None


class SyncUploadResponse(BaseModel):
    accepted: int
    conflicts: int
    details: List[SyncUploadDetail]


class SyncStatusResponse(BaseModel):
    pending_count: int
    last_sync: Optional[datetime]
    conflicts_count: int


class SyncResolveRequest(BaseModel):
    record_id: int
    resolution: ResolutionType


class SyncDeltaRequest(BaseModel):
    since: datetime


class SyncDeltaResponse(BaseModel):
    changes: List[SyncRecordResponse]
    timestamp: datetime
