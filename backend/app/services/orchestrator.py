"""
Ooumph Agentic Orchestrator
Routes user queries to appropriate AI agents
"""
import os
import uuid
import json
import hashlib
import time
import asyncio
from datetime import datetime
from typing import Dict, Optional, AsyncGenerator, Any, Tuple
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError
from sqlalchemy.orm import Session
from . import market_service, matching_service, supplier_service
from .. import models
from ..models import Order, CoinTransaction, User, Product, Post, Supplier, Material
from core.config import settings
from core.logging import get_logger
from sqlalchemy import desc

logger = get_logger(__name__)

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class FallbackMonitor:
    """Monitor fallback activation rates for OpenAI API failures"""
    
    def __init__(self):
        self.total_requests = 0
        self.fallback_activations = 0
        self.error_counts: Dict[str, int] = {}
        self._lock = None
    
    def _get_lock(self):
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
    
    async def record_request(self, used_fallback: bool, error_type: Optional[str] = None):
        async with self._get_lock():
            self.total_requests += 1
            if used_fallback:
                self.fallback_activations += 1
            if error_type:
                self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    def get_metrics(self) -> Dict[str, Any]:
        rate = (self.fallback_activations / self.total_requests * 100) if self.total_requests > 0 else 0
        return {
            "total_requests": self.total_requests,
            "fallback_activations": self.fallback_activations,
            "fallback_rate_percent": round(rate, 2),
            "error_breakdown": dict(self.error_counts)
        }
    
    def reset(self):
        self.total_requests = 0
        self.fallback_activations = 0
        self.error_counts = {}


fallback_monitor = FallbackMonitor()


def _sanitize_error_message(error: Exception) -> str:
    """Sanitize error messages to remove sensitive information"""
    error_str = str(error)
    
    sensitive_patterns = [
        settings.OPENAI_API_KEY if settings.OPENAI_API_KEY else None,
        settings.SECRET_KEY if settings.SECRET_KEY else None,
    ]
    
    for pattern in sensitive_patterns:
        if pattern and pattern in error_str:
            error_str = error_str.replace(pattern, "[REDACTED]")
    
    return error_str


def _classify_openai_error(error: Exception) -> Tuple[str, bool]:
    """Classify OpenAI errors and determine if fallback should be used"""
    if isinstance(error, AuthenticationError):
        return "authentication_error", True
    elif isinstance(error, RateLimitError):
        return "rate_limit_error", True
    elif isinstance(error, APIConnectionError):
        return "connection_error", True
    elif isinstance(error, APIError):
        return "api_error", True
    else:
        return "unknown_error", True


async def safe_openai_call(
    messages: list,
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 200,
    stream: bool = False,
    agent_name: str = "UNKNOWN"
):
    """
    Safe wrapper for OpenAI API calls with error handling and logging
    
    Returns:
        Tuple of (response_or_stream, used_fallback, error_type)
    """
    used_fallback = False
    error_type = None
    
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "CHANGE_OPENAI_API_KEY":
        logger.warning(
            "OpenAI API key not configured",
            extra={"agent": agent_name, "reason": "missing_api_key"}
        )
        await fallback_monitor.record_request(used_fallback=True, error_type="missing_api_key")
        return None, True, "missing_api_key"
    
    try:
        logger.debug(
            "Making OpenAI API request",
            extra={
                "agent": agent_name,
                "model": model or settings.OPENAI_MODEL,
                "stream": stream
            }
        )
        
        response = await client.chat.completions.create(
            model=model or settings.OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        
        await fallback_monitor.record_request(used_fallback=False)
        
        logger.debug(
            "OpenAI API request successful",
            extra={"agent": agent_name, "stream": stream}
        )
        
        return response, False, None
        
    except AuthenticationError as e:
        error_type = "authentication_error"
        logger.error(
            "OpenAI authentication failed",
            extra={
                "agent": agent_name,
                "error_type": error_type,
                "error_message": "Invalid API key"
            }
        )
        await fallback_monitor.record_request(used_fallback=True, error_type=error_type)
        return None, True, error_type
        
    except RateLimitError as e:
        error_type = "rate_limit_error"
        logger.warning(
            "OpenAI rate limit exceeded",
            extra={
                "agent": agent_name,
                "error_type": error_type
            }
        )
        await fallback_monitor.record_request(used_fallback=True, error_type=error_type)
        return None, True, error_type
        
    except APIConnectionError as e:
        error_type = "connection_error"
        logger.error(
            "OpenAI connection failed",
            extra={
                "agent": agent_name,
                "error_type": error_type,
                "error_message": "Network connectivity issue"
            }
        )
        await fallback_monitor.record_request(used_fallback=True, error_type=error_type)
        return None, True, error_type
        
    except APIError as e:
        error_type = "api_error"
        sanitized_message = _sanitize_error_message(e)
        logger.error(
            "OpenAI API error",
            extra={
                "agent": agent_name,
                "error_type": error_type,
                "error_message": sanitized_message
            }
        )
        await fallback_monitor.record_request(used_fallback=True, error_type=error_type)
        return None, True, error_type
        
    except Exception as e:
        error_type = "unknown_error"
        sanitized_message = _sanitize_error_message(e)
        logger.error(
            "Unexpected error in OpenAI call",
            extra={
                "agent": agent_name,
                "error_type": error_type,
                "error_message": sanitized_message
            },
            exc_info=True
        )
        await fallback_monitor.record_request(used_fallback=True, error_type=error_type)
        return None, True, error_type


def generate_dynamic_fallback(query: str, agent_name: str, fetched_data: dict, user_data: dict) -> str:
    """
    Generate a dynamic fallback response based on the actual query and fetched data.
    This analyzes the query keywords and constructs a relevant response using real data.
    """
    query_lower = query.lower()
    
    query_keywords = {
        "balance": ["balance", "coins", "wallet", "money", "trust coin", "how much"],
        "orders": ["order", "orders", "delivery", "shipping", "track", "purchase", "bought", "sold"],
        "products": ["product", "products", "sell", "selling", "buy", "buying", "item", "items", "price", "cost"],
        "suppliers": ["supplier", "suppliers", "material", "materials", "raw", "vendor", "sourcing"],
        "market": ["market", "trend", "demand", "price", "pricing", "analytics", "forecast"],
        "community": ["community", "post", "announcement", "shg", "federation", "group", "member"],
        "help": ["help", "how to", "guide", "navigate", "where", "what can you", "how do i"],
        "greeting": ["hello", "hi", "namaste", "hey", "vanakkam", "good morning", "good evening"]
    }
    
    detected_intents = []
    for intent, keywords in query_keywords.items():
        if any(kw in query_lower for kw in keywords):
            detected_intents.append(intent)
    
    if not detected_intents:
        detected_intents = ["general"]
    
    response_parts = []
    
    if "greeting" in detected_intents:
        greetings = ["Namaste!", "Hello!", "Vanakkam!", "Welcome!"]
        import random
        response_parts.append(random.choice(greetings))
        response_parts.append(f"I'm {agent_name}, your SHG marketplace assistant.")
    
    for intent in detected_intents:
        if intent == "balance" and "wallet" in fetched_data:
            response_parts.append(f"💰 Wallet Status: {fetched_data['wallet']}")
        
        elif intent == "orders" and "orders" in fetched_data:
            response_parts.append(f"📋 Your Orders:\n{fetched_data['orders']}")
        
        elif intent == "products" and "products" in fetched_data:
            response_parts.append(f"📦 Products:\n{fetched_data['products']}")
        
        elif intent == "suppliers" and "suppliers" in fetched_data:
            response_parts.append(f"🏭 Suppliers:\n{fetched_data['suppliers']}")
            if "materials" in fetched_data:
                response_parts.append(f"🧱 Materials:\n{fetched_data['materials']}")
        
        elif intent == "market" and "market" in fetched_data:
            response_parts.append(f"📊 Market Data:\n{fetched_data['market']}")
        
        elif intent == "community" and "community" in fetched_data:
            response_parts.append(f"👥 Community:\n{fetched_data['community']}")
    
    if not response_parts:
        for key, value in fetched_data.items():
            if value and value != f"No {key} available." and value != f"No {key} found.":
                response_parts.append(f"📌 {key.title()}:\n{value}")
    
    if len(response_parts) == 0:
        response_parts.append(f"I'm {agent_name}. I can help you with products, orders, suppliers, market trends, and more.")
        response_parts.append("What would you like to know?")
    
    return "\n\n".join(response_parts)


async def get_user_orders_context(user_id: int, db: Session) -> str:
    """Fetch recent orders context for the user"""
    try:
        orders = db.query(Order).filter(
            (Order.buyer_id == user_id) | (Order.seller_id == user_id)
        ).order_by(desc(Order.created_at)).limit(5).all()
        
        if not orders:
            return "No orders found."
        
        context_parts = []
        for order in orders:
            status = order.order_status.value if order.order_status else "Unknown"
            context_parts.append(
                f"Order #{order.order_number}: Status={status}, "
                f"Amount=₹{order.final_amount}, Created={order.created_at.strftime('%Y-%m-%d') if order.created_at else 'N/A'}"
            )
        
        return "Recent Orders:\n" + "\n".join(context_parts)
    except Exception:
        return "Unable to fetch orders."


async def get_user_wallet_context(user_id: int, db: Session) -> str:
    """Fetch wallet and trust coin context for the user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return "User not found."
        
        recent_transactions = db.query(CoinTransaction).filter(
            CoinTransaction.user_id == user_id
        ).order_by(desc(CoinTransaction.created_at)).limit(5).all()
        
        context = f"Wallet Status:\n"
        context += f"- Trust Coins Balance: {user.trust_coins}\n"
        context += f"- Trust Score: {user.trust_score}/100\n"
        context += f"- Trust Badge: {user.trust_badge}\n"
        
        if recent_transactions:
            context += "\nRecent Transactions:\n"
            for txn in recent_transactions:
                sign = "+" if txn.amount > 0 else ""
                context += f"- {sign}{txn.amount} coins: {txn.source} ({txn.transaction_type})\n"
        
        return context
    except Exception:
        return "Unable to fetch wallet information."


async def get_user_profile_context(user_id: int, db: Session) -> str:
    """Fetch profile context for the user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return "User not found."
        
        products_count = db.query(Product).filter(
            Product.seller_id == user_id,
            Product.status == models.ProductStatus.ACTIVE
        ).count()
        
        context = f"Profile Summary:\n"
        context += f"- Name: {user.name}\n"
        context += f"- Role: {user.role.value}\n"
        context += f"- District: {user.district or 'Not set'}\n"
        context += f"- Hierarchy Level: {user.hierarchy_level.value}\n"
        context += f"- Active Products: {products_count}\n"
        context += f"- Trust Score: {user.trust_score}/100 ({user.trust_badge})\n"
        
        return context
    except Exception:
        return "Unable to fetch profile information."

class PlatformDataChecker:
    """
    Checks platform data availability for users.
    Used by agents to provide context-aware responses based on actual platform data.
    """
    
    def __init__(self, user_id: int, db: Session):
        self.user_id = user_id
        self.db = db
        self._cache: Dict[str, Any] = {}
    
    async def check_orders(self) -> Dict[str, Any]:
        """Check if user has orders and return order data summary"""
        if "orders" in self._cache:
            return self._cache["orders"]
        
        try:
            buyer_orders = self.db.query(Order).filter(
                Order.buyer_id == self.user_id
            ).count()
            
            seller_orders = self.db.query(Order).filter(
                Order.seller_id == self.user_id
            ).count()
            
            total_orders = buyer_orders + seller_orders
            
            recent_orders = self.db.query(Order).filter(
                (Order.buyer_id == self.user_id) | (Order.seller_id == self.user_id)
            ).order_by(desc(Order.created_at)).limit(3).all()
            
            pending_orders = self.db.query(Order).filter(
                (Order.buyer_id == self.user_id) | (Order.seller_id == self.user_id),
                Order.order_status.in_([
                    models.OrderStatus.PLACED,
                    models.OrderStatus.CONFIRMED,
                    models.OrderStatus.PROCESSING,
                    models.OrderStatus.SHIPPED
                ])
            ).count()
            
            result = {
                "has_data": total_orders > 0,
                "total_orders": total_orders,
                "buyer_orders": buyer_orders,
                "seller_orders": seller_orders,
                "pending_orders": pending_orders,
                "recent_orders": [
                    {
                        "order_number": o.order_number,
                        "status": o.order_status.value if o.order_status else "Unknown",
                        "amount": o.final_amount,
                        "created_at": o.created_at.strftime('%Y-%m-%d') if o.created_at else None
                    }
                    for o in recent_orders
                ]
            }
            self._cache["orders"] = result
            return result
        except Exception:
            return {"has_data": False, "total_orders": 0, "error": True}
    
    async def check_products(self) -> Dict[str, Any]:
        """Check if user has products listed and return product data summary"""
        if "products" in self._cache:
            return self._cache["products"]
        
        try:
            total_products = self.db.query(Product).filter(
                Product.seller_id == self.user_id
            ).count()
            
            active_products = self.db.query(Product).filter(
                Product.seller_id == self.user_id,
                Product.status == models.ProductStatus.ACTIVE
            ).count()
            
            draft_products = self.db.query(Product).filter(
                Product.seller_id == self.user_id,
                Product.status == models.ProductStatus.DRAFT
            ).count()
            
            sold_out_products = self.db.query(Product).filter(
                Product.seller_id == self.user_id,
                Product.status == models.ProductStatus.SOLD_OUT
            ).count()
            
            recent_products = self.db.query(Product).filter(
                Product.seller_id == self.user_id
            ).order_by(desc(Product.created_at)).limit(3).all()
            
            categories = self.db.query(Product.category).filter(
                Product.seller_id == self.user_id,
                Product.status == models.ProductStatus.ACTIVE
            ).distinct().all()
            
            result = {
                "has_data": total_products > 0,
                "total_products": total_products,
                "active_products": active_products,
                "draft_products": draft_products,
                "sold_out_products": sold_out_products,
                "categories": [c[0] for c in categories if c[0]],
                "recent_products": [
                    {
                        "name": p.name,
                        "category": p.category,
                        "price": p.price,
                        "status": p.status.value if p.status else "Unknown"
                    }
                    for p in recent_products
                ]
            }
            self._cache["products"] = result
            return result
        except Exception:
            return {"has_data": False, "total_products": 0, "error": True}
    
    async def check_wallet(self) -> Dict[str, Any]:
        """Check user's wallet and trust coin data"""
        if "wallet" in self._cache:
            return self._cache["wallet"]
        
        try:
            user = self.db.query(User).filter(User.id == self.user_id).first()
            if not user:
                return {"has_data": False, "error": True}
            
            total_transactions = self.db.query(CoinTransaction).filter(
                CoinTransaction.user_id == self.user_id
            ).count()
            
            recent_transactions = self.db.query(CoinTransaction).filter(
                CoinTransaction.user_id == self.user_id
            ).order_by(desc(CoinTransaction.created_at)).limit(5).all()
            
            earned_coins = self.db.query(CoinTransaction).filter(
                CoinTransaction.user_id == self.user_id,
                CoinTransaction.amount > 0
            ).count()
            
            spent_coins = self.db.query(CoinTransaction).filter(
                CoinTransaction.user_id == self.user_id,
                CoinTransaction.amount < 0
            ).count()
            
            result = {
                "has_data": total_transactions > 0 or user.trust_coins > 0,
                "trust_coins": user.trust_coins,
                "trust_score": user.trust_score,
                "trust_badge": user.trust_badge,
                "total_transactions": total_transactions,
                "earned_transactions": earned_coins,
                "spent_transactions": spent_coins,
                "quality_score": user.quality_score,
                "delivery_score": user.delivery_score,
                "financial_score": user.financial_score,
                "community_score": user.community_score,
                "recent_transactions": [
                    {
                        "amount": t.amount,
                        "type": t.transaction_type,
                        "source": t.source,
                        "date": t.created_at.strftime('%Y-%m-%d') if t.created_at else None
                    }
                    for t in recent_transactions
                ]
            }
            self._cache["wallet"] = result
            return result
        except Exception:
            return {"has_data": False, "error": True}
    
    async def check_suppliers(self, district: str = None) -> Dict[str, Any]:
        """Check available suppliers and raw materials data"""
        if "suppliers" in self._cache:
            return self._cache["suppliers"]
        
        try:
            query = self.db.query(Supplier)
            if district:
                query = query.filter(Supplier.district == district)
            
            total_suppliers = query.count()
            verified_suppliers = query.filter(Supplier.is_verified == True).count()
            
            total_materials = self.db.query(Material).join(Supplier).count()
            if district:
                total_materials = self.db.query(Material).join(Supplier).filter(
                    Supplier.district == district
                ).count()
            
            bulk_requests = self.db.query(models.BulkRequest)
            if district:
                bulk_requests = bulk_requests.filter(models.BulkRequest.district == district)
            open_bulk_requests = bulk_requests.filter(
                models.BulkRequest.status == "Open"
            ).count()
            
            top_suppliers = self.db.query(Supplier).filter(
                Supplier.is_verified == True
            )
            if district:
                top_suppliers = top_suppliers.filter(Supplier.district == district)
            top_suppliers = top_suppliers.order_by(desc(Supplier.rating)).limit(3).all()
            
            categories = self.db.query(Material.category).join(Supplier).distinct().all()
            
            result = {
                "has_data": total_suppliers > 0,
                "total_suppliers": total_suppliers,
                "verified_suppliers": verified_suppliers,
                "total_materials": total_materials,
                "open_bulk_requests": open_bulk_requests,
                "categories_available": [c[0] for c in categories if c[0]],
                "top_suppliers": [
                    {
                        "name": s.business_name,
                        "rating": s.rating,
                        "type": s.business_type,
                        "verified": s.is_verified
                    }
                    for s in top_suppliers
                ]
            }
            self._cache["suppliers"] = result
            return result
        except Exception:
            return {"has_data": False, "total_suppliers": 0, "error": True}
    
    async def check_community(self) -> Dict[str, Any]:
        """Check community posts and federation data"""
        if "community" in self._cache:
            return self._cache["community"]
        
        try:
            user = self.db.query(User).filter(User.id == self.user_id).first()
            
            total_posts = self.db.query(Post).count()
            announcements = self.db.query(Post).filter(
                Post.is_announcement == True
            ).count()
            
            recent_announcements = self.db.query(Post).filter(
                Post.is_announcement == True
            ).order_by(desc(Post.created_at)).limit(3).all()
            
            user_posts = self.db.query(Post).filter(
                Post.author_id == self.user_id
            ).count()
            
            result = {
                "has_data": total_posts > 0,
                "total_posts": total_posts,
                "announcements": announcements,
                "user_posts": user_posts,
                "hierarchy_level": user.hierarchy_level.value if user else "SHG",
                "district": user.district if user else None,
                "recent_announcements": [
                    {
                        "title": p.title,
                        "content": p.content[:100] + "..." if len(p.content) > 100 else p.content,
                        "date": p.created_at.strftime('%Y-%m-%d') if p.created_at else None
                    }
                    for p in recent_announcements
                ]
            }
            self._cache["community"] = result
            return result
        except Exception:
            return {"has_data": False, "total_posts": 0, "error": True}
    
    async def get_all_availability_flags(self, district: str = None) -> Dict[str, bool]:
        """Get all data availability flags for quick agent reference"""
        orders = await self.check_orders()
        products = await self.check_products()
        wallet = await self.check_wallet()
        suppliers = await self.check_suppliers(district)
        community = await self.check_community()
        
        return {
            "has_orders": orders.get("has_data", False),
            "has_products": products.get("has_data", False),
            "has_wallet_activity": wallet.get("has_data", False),
            "has_suppliers": suppliers.get("has_data", False),
            "has_community": community.get("has_data", False),
            "has_pending_orders": orders.get("pending_orders", 0) > 0,
            "has_active_products": products.get("active_products", 0) > 0,
            "has_trust_coins": wallet.get("trust_coins", 0) > 0,
            "is_verified_seller": products.get("active_products", 0) > 0,
            "community_level": community.get("hierarchy_level", "SHG")
        }
    
    async def get_platform_summary(self, district: str = None) -> str:
        """Get a human-readable summary of platform data availability"""
        flags = await self.get_all_availability_flags(district)
        
        summary_parts = []
        
        if flags["has_orders"]:
            orders = self._cache.get("orders", {})
            summary_parts.append(f"Orders: {orders.get('total_orders', 0)} total ({orders.get('pending_orders', 0)} pending)")
        else:
            summary_parts.append("Orders: No orders yet")
        
        if flags["has_products"]:
            products = self._cache.get("products", {})
            summary_parts.append(f"Products: {products.get('active_products', 0)} active listings")
        else:
            summary_parts.append("Products: No products listed")
        
        if flags["has_wallet_activity"]:
            wallet = self._cache.get("wallet", {})
            summary_parts.append(f"Wallet: {wallet.get('trust_coins', 0)} coins, {wallet.get('trust_badge', 'Bronze')} badge")
        else:
            summary_parts.append("Wallet: No activity")
        
        if flags["has_suppliers"]:
            suppliers = self._cache.get("suppliers", {})
            summary_parts.append(f"Suppliers: {suppliers.get('verified_suppliers', 0)} verified in area")
        else:
            summary_parts.append("Suppliers: None in area")
        
        if flags["has_community"]:
            community = self._cache.get("community", {})
            summary_parts.append(f"Community: {community.get('hierarchy_level', 'SHG')} level")
        
        return " | ".join(summary_parts)
    
    def get_no_data_message(self, data_type: str, language: str = "English") -> str:
        """Get a helpful message when data is not available"""
        messages = {
            "orders": {
                "English": "You don't have any orders yet. Start by browsing products or listing your own!",
                "Hindi": "आपके पास अभी तक कोई ऑर्डर नहीं है। उत्पादों को ब्राउज़ करके या अपना खुद का लिस्टिंग करके शुरू करें!",
                "Telugu": "మీకు ఇంకా ఆర్డర్లు లేవు. ఉత్పత్తులను బ్రౌజ్ చేయడం ద్వారా లేదా మీ స్వంత జాబితా చేయడం ద్వారా ప్రారంభించండి!"
            },
            "products": {
                "English": "You haven't listed any products yet. Go to 'Sell Product' to start selling!",
                "Hindi": "आपने अभी तक कोई उत्पाद सूचीबद्ध नहीं किया है। बिक्री शुरू करने के लिए 'उत्पाद बेचें' पर जाएं!",
                "Telugu": "మీరు ఇంకా ఏ ఉత్పత్తులను జాబితా చేయలేదు. అమ్మడం ప్రారంభించడానికి 'ఉత్పత్తిని విక్రయించండి'కి వెళ్ళండి!"
            },
            "wallet": {
                "English": "No wallet activity yet. Complete orders to earn Trust Coins!",
                "Hindi": "अभी तक कोई वॉलेट गतिविधि नहीं। ट्रस्ट कॉइन्स कमाने के लिए ऑर्डर पूरा करें!",
                "Telugu": "ఇంకా వాలెట్ కార్యాచరణ లేదు. ట్రస్ట్ నాణెం సంపాదించడానికి ఆర్డర్లను పూర్తి చేయండి!"
            },
            "suppliers": {
                "English": "No suppliers found in your area. Try expanding your search or check back later.",
                "Hindi": "आपके क्षेत्र में कोई आपूर्तिकर्ता नहीं मिला। अपनी खोज का विस्तार करें या बाद में जांचें।",
                "Telugu": "మీ ప్రాంతంలో సరఫరాదారులు కనుగొనబడలేదు. మీ శోధనను విస్తరించండి లేదా తర్వాత తనిఖీ చేయండి."
            },
            "community": {
                "English": "No community posts yet. Be the first to share with your SHG network!",
                "Hindi": "अभी तक कोई सामुदायिक पोस्ट नहीं। अपने SHG नेटवर्क के साथ साझा करने वाले पहले बनें!",
                "Telugu": "ఇంకా కమ్యూనిటీ పోస్ట్‌లు లేవు. మీ SHG నెట్‌వర్క్‌తో షేర్ చేసే మొదటి వ్యక్తి అవ్వండి!"
            }
        }
        
        return messages.get(data_type, {}).get(language, messages.get(data_type, {}).get("English", "No data available."))


async def check_platform_data_for_agent(
    user_id: int, 
    db: Session, 
    agent_type: str,
    district: str = None
) -> Tuple[PlatformDataChecker, Dict[str, Any]]:
    """
    Convenience function to check platform data for a specific agent.
    Returns the checker instance and relevant data for the agent.
    """
    checker = PlatformDataChecker(user_id, db)
    
    agent_data = {"checker": checker}
    
    if agent_type in ["JODI", "VAANI"]:
        agent_data["orders"] = await checker.check_orders()
    
    if agent_type in ["BAZAAR", "VAANI"]:
        agent_data["products"] = await checker.check_products()
    
    if agent_type in ["VISHWAS", "VAANI"]:
        agent_data["wallet"] = await checker.check_wallet()
    
    if agent_type in ["SAMAGRI", "VAANI"]:
        agent_data["suppliers"] = await checker.check_suppliers(district)
    
    if agent_type in ["SAMPARK", "VAANI"]:
        agent_data["community"] = await checker.check_community()
    
    agent_data["flags"] = await checker.get_all_availability_flags(district)
    
    return checker, agent_data


CACHE_TTL = 300
_stream_cache: Dict[str, Dict[str, Any]] = {}

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

_redis_client = None

def _get_redis_client():
    global _redis_client
    if _redis_client is None and REDIS_AVAILABLE:
        try:
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            _redis_client.ping()
        except Exception:
            _redis_client = None
    return _redis_client

def _generate_cache_key(query: str, agent: str, language: str) -> str:
    key_string = f"stream:{agent}:{language}:{query}"
    return hashlib.md5(key_string.encode()).hexdigest()

async def _get_cached_response(query: str, agent: str, language: str) -> Optional[str]:
    cache_key = _generate_cache_key(query, agent, language)
    
    redis_client = _get_redis_client()
    if redis_client:
        try:
            cached = redis_client.get(cache_key)
            if cached:
                return cached
        except Exception:
            pass
    
    if cache_key in _stream_cache:
        entry = _stream_cache[cache_key]
        if time.time() < entry.get("expires", 0):
            return entry.get("response")
        else:
            del _stream_cache[cache_key]
    
    return None

async def _cache_response(query: str, agent: str, language: str, response: str):
    cache_key = _generate_cache_key(query, agent, language)
    
    redis_client = _get_redis_client()
    if redis_client:
        try:
            redis_client.setex(cache_key, CACHE_TTL, response)
            return
        except Exception:
            pass
    
    _stream_cache[cache_key] = {
        "response": response,
        "expires": time.time() + CACHE_TTL
    }
    
    if len(_stream_cache) > 500:
        current_time = time.time()
        expired_keys = [k for k, v in _stream_cache.items() if v.get("expires", 0) < current_time]
        for k in expired_keys:
            del _stream_cache[k]

SYSTEM_PROMPT = """
You are the Ooumph Agentic Ecosystem Orchestrator.
You manage the following AI agents. ALL agents are PLATFORM-FIRST and only respond about platform data:

1. VAANI (वाणी) - Platform General Assistant
   - ONLY responds about platform features, products, orders, marketplace
   - Redirects non-platform questions to relevant platform pages
   - Multilingual support (English, Telugu, Hindi, Urdu)

2. BAZAAR - Platform Market Intelligence Agent
   - ONLY provides market data from platform database
   - Platform price recommendations and demand analysis
   - Redirects to Market Analyzer page

3. JODI - Platform Order Management Agent
   - ONLY fetches and discusses actual platform orders
   - Real order status from platform database
   - Redirects to Orders page for actions

4. SAMAGRI - Platform Supplier Network Agent
   - ONLY recommends suppliers from platform database
   - Platform-verified suppliers only
   - Redirects to Raw Materials page

5. SAMPARK - Platform Community Hub Agent
   - ONLY shares platform community data (posts, members, hierarchy)
   - Platform federation information only
   - Redirects to Community page

6. VISHWAS - Platform Wallet & Trust Agent
   - ONLY provides actual wallet data from platform
   - Real trust scores and coin balances
   - Redirects to Wallet page

7. SUPPORT - Platform Navigation Agent
   - ONLY helps navigate the Ooumph platform
   - App feature guidance and troubleshooting
   - Redirects to appropriate pages

IMPORTANT: All agents are PLATFORM-ONLY. They do NOT provide general knowledge, external information, or advice outside the Ooumph platform. They always guide users to relevant platform pages.

Analyze the user's query and determine which agent is most appropriate.
Reply with ONLY the agent name: VAANI, BAZAAR, JODI, SAMAGRI, SAMPARK, VISHWAS, or SUPPORT.
For general queries or greetings, use VAANI.
"""

async def process_chat_query(query: str, user_data: dict, db: Session,
                            language: str = "English", agent_id: str = None) -> Dict:
    """
    Process chat query and route to appropriate agent
    If agent_id is provided, use that agent directly instead of auto-detection
    """
    session_id = str(uuid.uuid4())

    await save_chat_message(
        user_data.get("id"),
        session_id,
        "user",
        query,
        language=language,
        db=db
    )

    try:
        agent_decision = agent_id if agent_id else await determine_agent(query, db)

        # Get response from appropriate agent
        response_data = await get_agent_response(
            agent_decision,
            query,
            user_data,
            db,
            language
        )

        # Save assistant response to chat history
        await save_chat_message(
            user_data.get("id"),
            session_id,
            "assistant",
            response_data["reply"],
            agent_triggered=agent_decision,
            language=language,
            db=db
        )

        return {
            "reply": response_data["reply"],
            "agent_triggered": agent_decision,
            "language": language,
            "session_id": session_id,
            "is_voice_response": response_data.get("is_voice_response", False),
            "audio_url": response_data.get("audio_url"),
            "suggestions": response_data.get("suggestions", []),
            "needs_global_search": response_data.get("needs_global_search", False),
            "is_fallback": response_data.get("is_fallback", False),
        }

    except Exception as e:
        # Fallback response
        reply = "I apologize, but I'm having trouble processing your request right now. Please try again or contact support if the issue persists."

        return {
            "reply": reply,
            "agent_triggered": "VAANI",
            "language": language,
            "session_id": session_id,
            "error": str(e)
        }

async def determine_agent(query: str, db: Session) -> str:
    """Determine which agent should handle the query"""
    try:
        response, used_fallback, error_type = await safe_openai_call(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ],
            temperature=0,
            max_tokens=20,
            agent_name="ORCHESTRATOR"
        )
        
        if used_fallback or response is None:
            agent_decision = keyword_based_routing(query)
            logger.info(
                "Using keyword-based routing fallback",
                extra={"reason": error_type or "no_response"}
            )
        else:
            agent_decision = response.choices[0].message.content.strip().upper()
            
    except Exception as e:
        logger.warning(
            "Agent determination failed, using fallback",
            extra={"error_message": _sanitize_error_message(e)}
        )
        agent_decision = keyword_based_routing(query)

    agent_mapping = {
        "VAANI": "GENERAL",
        "GENERAL": "VAANI",
        "BAZAAR": "BAZAAR",
        "BAZAAR BUDDHI": "BAZAAR",
        "JODI": "JODI",
        "SAMAGRI": "SAMAGRI",
        "VISHWAS": "VISHWAS",
        "SAMPARK": "SAMPARK"
    }

    return agent_mapping.get(agent_decision, "VAANI")

def keyword_based_routing(query: str) -> str:
    """Fallback keyword-based routing with context awareness"""
    query_lower = query.lower()

    order_context_keywords = ["address", "order", "delivery", "shipment", "shipping"]
    wallet_context_keywords = ["wallet", "payment", "balance", "coins", "coin"]

    if any(kw in query_lower for kw in ["update", "change", "modify", "edit"]):
        if any(ctx in query_lower for ctx in order_context_keywords):
            return "JODI"
        if any(ctx in query_lower for ctx in wallet_context_keywords):
            return "VISHWAS"
        if any(ctx in query_lower for ctx in ["profile", "account", "settings"]):
            return "SUPPORT"

    if any(kw in query_lower for kw in ["market", "demand", "price", "sell", "trend", "competition", "pricing", "analyze", "rates", "rate"]):
        return "BAZAAR"

    if any(kw in query_lower for kw in ["order", "delivery", "track", "cancel", "shipment", "shipping", "status", "address", "package", "dispatch", "arrive", "arriving", "delivered", "return", "refund"]):
        return "JODI"

    if any(kw in query_lower for kw in ["supplier", "raw material", "bulk purchase", "sourcing", "materials", "vendor", "quote", "procurement", "wholesale", "stock", "inventory"]):
        return "SAMAGRI"

    if any(kw in query_lower for kw in ["trust", "score", "badge", "coin", "coins", "wallet", "payment", "balance", "transaction", "redeem", "earnings", "payout", "credit", "debit"]):
        return "VISHWAS"

    if any(kw in query_lower for kw in ["federation", "slf", "tlf", "community", "district", "shg", "post", "comment", "member", "group", "network", "connect", "meeting"]):
        return "SAMPARK"

    if any(kw in query_lower for kw in ["help", "support", "bug", "issue", "problem", "how to", "navigate", "feature", "trouble", "error", "not working", "can't", "cannot"]):
        return "SUPPORT"

    return "VAANI"

async def get_agent_response(agent: str, query: str, user_data: dict,
                            db: Session, language: str) -> Dict:
    """Get response from specific agent"""
    if agent == "BAZAAR":
        return await bazaar_buddhi_response(query, user_data, db)
    elif agent == "JODI":
        return await jodi_response(query, user_data, db)
    elif agent == "SAMAGRI":
        return await samagri_response(query, user_data, db)
    elif agent == "VISHWAS":
        return await vishwas_response(query, user_data, db)
    elif agent == "SAMPARK":
        return await sampark_response(query, user_data, db)
    elif agent == "SUPPORT":
        return await support_response(query, user_data, db, language)
    else:  # VAANI / GENERAL
        return await vaani_response(query, user_data, db, language)


async def support_response(query: str, user_data: dict, db: Session, language: str) -> Dict:
    """Get response from Support agent - Navigation & Help"""
    user_id = user_data.get("id")
    profile_context = await get_user_profile_context(user_id, db) if user_id else "No profile data available."
    
    response, used_fallback, error_type = await safe_openai_call(
        messages=[
            {
                "role": "system",
                "content": f"""You are Agent SUPPORT, the Navigation & Help Specialist for the Ooumph SHG marketplace.

Your capabilities:
- APP NAVIGATION: Help users find and use different features
- FEATURE EXPLANATIONS: Explain how marketplace features work
- TROUBLESHOOTING: Guide users through common issues
- ONBOARDING HELP: Assist new users with getting started
- BUG REPORTING: Guide users on how to report issues

User's Profile Context:
{profile_context}

App Navigation Guide:
- Dashboard: Home screen with overview
- Sell Product: Add and manage your product listings
- My Products: View and edit your listed products
- Orders: Track and manage orders
- Market Analyzer: View market trends and pricing
- Raw Materials: Find suppliers and materials
- Wallet: Trust coins and transactions
- Community: Connect with other SHGs
- Profile: Manage your account settings

Guidelines:
- Respond in {language}
- Provide clear step-by-step navigation instructions
- Be patient and helpful
- Use simple language suitable for rural SHG women
- Suggest specific pages and features to try
- Keep responses under 100 words
- Always offer to help with follow-up questions"""
            },
            {"role": "user", "content": query}
        ],
        temperature=0.7,
        max_tokens=200,
        agent_name="SUPPORT"
    )
    
    if not used_fallback and response:
        reply = response.choices[0].message.content.strip()
        return {"reply": reply, "agent": "SUPPORT"}
    
    logger.info("Using fallback response for SUPPORT agent", extra={"reason": error_type})
    
    reply = "Agent SUPPORT here! I can help you navigate the app.\n\n"
    reply += "📱 Quick Navigation Guide:\n"
    reply += "• Dashboard → Your home screen\n"
    reply += "• Sell Product → Add new products\n"
    reply += "• Orders → Track your orders\n"
    reply += "• Market Analyzer → Check prices & trends\n"
    reply += "• Raw Materials → Find suppliers\n"
    reply += "• Wallet → View trust coins\n\n"
    reply += "What would you like help with?"

    return {"reply": reply, "agent": "SUPPORT"}

async def vaani_response(query: str, user_data: dict, db: Session,
                        language: str) -> Dict:
    """Get response from Vaani agent using OpenAI - Action-oriented general assistant"""
    user_id = user_data.get("id")
    district = user_data.get("district", "Andhra Pradesh")
    
    profile_context = await get_user_profile_context(user_id, db) if user_id else "No profile data available."
    
    products_info = "No products available."
    orders_info = "No orders available."
    wallet_info = "No wallet data available."
    suppliers_info = "No suppliers available."
    community_info = "No community posts available."
    
    try:
        all_products = db.query(Product).limit(10).all()
        if all_products:
            products_list = []
            for p in all_products:
                products_list.append(f"• {p.name}: ₹{p.price} (Stock: {p.stock_quantity}, Category: {p.category or 'General'})")
            products_info = "\n".join(products_list)
    except Exception as e:
        logger.warning(f"Failed to fetch products for VAANI: {e}")
    
    try:
        if user_id:
            user_orders = db.query(Order).filter(
                (Order.buyer_id == user_id) | (Order.seller_id == user_id)
            ).limit(5).all()
            if user_orders:
                orders_list = []
                for o in user_orders:
                    orders_list.append(f"• Order #{o.id}: {o.product.name if o.product else 'Unknown'} - {o.order_status.value if o.order_status else 'Unknown'} - ₹{o.total_amount}")
                orders_info = "\n".join(orders_list)
    except Exception as e:
        logger.warning(f"Failed to fetch orders for VAANI: {e}")
    
    try:
        if user_id:
            wallet = db.query(CoinTransaction).filter(
                CoinTransaction.user_id == user_id
            ).first()
            if wallet:
                wallet_info = f"Trust Coins: {user_data.get('trust_coins', 0)}, Trust Score: {user_data.get('trust_score', 50)}"
    except Exception as e:
        logger.warning(f"Failed to fetch wallet for VAANI: {e}")
    
    try:
        all_suppliers = db.query(Supplier).limit(5).all()
        if all_suppliers:
            suppliers_list = []
            for s in all_suppliers:
                suppliers_list.append(f"• {s.business_name} ({s.business_type or 'General'}) - {s.rating}★")
            suppliers_info = "\n".join(suppliers_list)
    except Exception as e:
        logger.warning(f"Failed to fetch suppliers for VAANI: {e}")
    
    try:
        all_posts = db.query(Post).order_by(desc(Post.created_at)).limit(5).all()
        if all_posts:
            posts_list = []
            for p in all_posts:
                posts_list.append(f"• {p.title or p.content[:50]}...")
            community_info = "\n".join(posts_list)
    except Exception as e:
        logger.warning(f"Failed to fetch community posts for VAANI: {e}")
    
    platform_summary = f"""
Platform Products:
{products_info}

User's Orders:
{orders_info}

Wallet Status:
{wallet_info}

Available Suppliers:
{suppliers_info}

Community Posts:
{community_info}
"""
    
    response, used_fallback, error_type = await safe_openai_call(
        messages=[
            {
                "role": "system",
                "content": f"""You are Agent VAANI (वाणी), the friendly general assistant for the Ooumph SHG marketplace.

You are ACTION-ORIENTED and HELPFUL. Always guide users toward specific actions they can take.

User's Profile Context:
{profile_context}

User's District: {district}

CURRENT PLATFORM DATA (use this to answer questions):
{platform_summary}

Your primary areas:
- Products (selling, buying, listing, pricing)
- Orders and order management
- Buyers and suppliers
- Raw materials and procurement
- Trust scores and badges
- Market demand and pricing insights
- Delivery and shipping
- General marketplace navigation

You DO NOT answer questions about:
- General knowledge, news, weather, sports, entertainment
- Politics, religion, or personal advice
- Topics unrelated to the Ooumph marketplace

If asked about non-marketplace topics, politely redirect: "I'm here to help with your SHG marketplace needs - products, buyers, orders, and trust scores. What would you like help with?"

ACTION-ORIENTED Guidelines:
- Respond in {language}
- Be concise (under 100 words)
- Use simple language for rural women
- Be encouraging and supportive
- Use traditional greetings (Namaste, Vanakkam)
- ALWAYS suggest a specific action the user can take
- When mentioning products/orders/suppliers, use the ACTUAL data provided above
- Guide users to relevant pages: Dashboard, Sell Product, Orders, Wallet, Market Analyzer"""
            },
            {"role": "user", "content": query}
        ],
        temperature=0.7,
        max_tokens=200,
        agent_name="VAANI"
    )
    
    if not used_fallback and response:
        reply = response.choices[0].message.content.strip()
        return {"reply": reply, "agent": "VAANI"}
    
    logger.info("Using dynamic fallback response for VAANI agent", extra={"reason": error_type})
    
    fetched_data = {
        "products": products_info,
        "orders": orders_info,
        "wallet": wallet_info,
        "suppliers": suppliers_info,
        "community": community_info
    }
    reply = generate_dynamic_fallback(query, "VAANI", fetched_data, user_data)

    return {"reply": reply, "agent": "VAANI"}

async def bazaar_buddhi_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Bazaar Buddhi agent - PLATFORM-FIRST Market Expert"""
    user_id = user_data.get("id")
    district = user_data.get("district", "Andhra Pradesh")
    profile_context = await get_user_profile_context(user_id, db) if user_id else "No profile data available."
    
    products_info = "No products available."
    market_info = "No market data available."
    
    try:
        all_products = db.query(Product).limit(15).all()
        if all_products:
            products_list = []
            for p in all_products:
                status = p.status.value if p.status else "Unknown"
                products_list.append(f"• {p.name}: ₹{p.price} (Stock: {p.stock_quantity}, Category: {p.category or 'General'}, Status: {status})")
            products_info = "\n".join(products_list)
    except Exception as e:
        logger.warning(f"Failed to fetch products for BAZAAR: {e}")
    
    try:
        market_data = db.query(models.MarketData).order_by(desc(models.MarketData.date)).limit(10).all()
        if market_data:
            market_list = []
            for m in market_data:
                market_list.append(f"• {m.category or 'General'}: Demand={m.demand_level or 'Medium'}, Trend={m.demand_trend or 'Stable'}, Price=₹{m.price_min or 0}-{m.price_max or 0}")
            market_info = "\n".join(market_list)
    except Exception as e:
        logger.warning(f"Failed to fetch market data for BAZAAR: {e}")
    
    response, used_fallback, error_type = await safe_openai_call(
        messages=[
            {
                "role": "system",
                "content": f"""You are Agent BAZAAR (बाज़ार), the Market Expert for the Ooumph SHG marketplace.

Your capabilities:
- MARKET ANALYSIS: Analyze market trends and demand
- PRICING ADVICE: Help set competitive prices based on market data
- PRODUCT INSIGHTS: Share information about products on the platform
- DEMAND FORECASTING: Predict demand trends

User's Profile Context:
{profile_context}

User's District: {district}

ALL Products on Platform:
{products_info}

Market Data:
{market_info}

Guidelines:
- ALWAYS mention specific products by name when discussing market trends
- Use actual prices and stock levels from the product data above
- Suggest pricing strategies based on the market data
- Guide users to Market Analyzer page for detailed insights
- Keep responses under 120 words
- Use simple language suitable for rural SHG women
- Be helpful and provide actionable insights"""
            },
            {"role": "user", "content": query}
        ],
        temperature=0.7,
        max_tokens=250,
        agent_name="BAZAAR"
    )
    
    if not used_fallback and response:
        reply = response.choices[0].message.content.strip()
        return {"reply": reply, "agent": "BAZAAR"}
    
    logger.info("Using dynamic fallback response for BAZAAR agent", extra={"reason": error_type})
    
    fetched_data = {
        "products": products_info,
        "market": market_info
    }
    reply = generate_dynamic_fallback(query, "BAZAAR", fetched_data, user_data)

    return {"reply": reply, "agent": "BAZAAR"}

async def jodi_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Jodi agent - Order Management Specialist"""
    user_id = user_data.get("id")
    
    orders_info = "No orders available."
    order_count = 0
    pending_orders = 0
    delivered_orders = 0
    
    try:
        if user_id:
            user_orders = db.query(Order).filter(
                (Order.buyer_id == user_id) | (Order.seller_id == user_id)
            ).limit(10).all()
            
            order_count = len(user_orders)
            pending_orders = len([o for o in user_orders if o.order_status and o.order_status.value in ['pending', 'confirmed', 'shipped']])
            delivered_orders = len([o for o in user_orders if o.order_status and o.order_status.value == 'delivered'])
            
            if user_orders:
                orders_list = []
                for o in user_orders:
                    product_name = o.product.name if o.product else "Unknown Product"
                    buyer_seller = "You sold" if o.seller_id == user_id else "You bought"
                    orders_list.append(f"• Order #{o.id}: {product_name} - {o.order_status.value if o.order_status else 'Unknown'} - ₹{o.total_amount} ({buyer_seller})")
                orders_info = "\n".join(orders_list)
    except Exception as e:
        logger.warning(f"Failed to fetch orders for JODI: {e}")
    
    response, used_fallback, error_type = await safe_openai_call(
        messages=[
            {
                "role": "system",
                "content": f"""You are Agent JODI (जोड़ी), the Order Management Specialist for the Ooumph SHG marketplace.

Your capabilities:
- ORDER TRACKING: Track orders and provide status updates
- ORDER MANAGEMENT: Help with order cancellations, address changes
- ORDER INSIGHTS: Analyze order patterns and provide recommendations
- BUYER/SELLER COORDINATION: Help coordinate between buyers and sellers

Current User's Orders:
{orders_info}

Order Statistics:
- Total Orders: {order_count}
- Pending/Active: {pending_orders}
- Delivered: {delivered_orders}

Guidelines:
- ALWAYS mention specific orders by ID and product name when discussing orders
- Provide actual order statuses from the data above
- For address changes: "You can update the delivery address from the Orders page if the order hasn't shipped yet"
- For cancellations: "Go to Orders page to request cancellation"
- Guide users to Orders page for actions
- Keep responses under 120 words
- Use simple language suitable for rural SHG women"""
            },
            {"role": "user", "content": query}
        ],
        temperature=0.7,
        max_tokens=250,
        agent_name="JODI"
    )
    
    if not used_fallback and response:
        reply = response.choices[0].message.content.strip()
        return {"reply": reply, "agent": "JODI"}
    
    logger.info("Using dynamic fallback response for JODI agent", extra={"reason": error_type})
    
    fetched_data = {
        "orders": orders_info
    }
    reply = generate_dynamic_fallback(query, "JODI", fetched_data, user_data)

    return {"reply": reply, "agent": "JODI"}

async def samagri_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Samagri agent - Supplier & Materials Advisor"""
    user_id = user_data.get("id")
    district = user_data.get("district", "Andhra Pradesh")
    profile_context = await get_user_profile_context(user_id, db) if user_id else "No profile data available."
    
    suppliers_info = "No suppliers found."
    materials_info = "No materials available."
    
    try:
        all_suppliers = db.query(Supplier).limit(10).all()
        
        if all_suppliers:
            suppliers_list = []
            for s in all_suppliers:
                verified_badge = "✓ Verified" if s.is_verified else "Unverified"
                suppliers_list.append(
                    f"• {s.business_name} ({s.business_type or 'General'}) - {s.rating}★ {verified_badge} - {s.district or 'Unknown'}"
                )
            suppliers_info = "\n".join(suppliers_list)
        else:
            suppliers_info = "No suppliers registered yet."
    except Exception as e:
        logger.warning(f"Failed to fetch suppliers: {e}")
        suppliers_info = "Unable to fetch supplier data."
    
    try:
        materials = db.query(Material).join(Supplier).limit(10).all()
        if materials:
            materials_list = []
            for m in materials:
                materials_list.append(
                    f"• {m.name} - ₹{m.price_per_unit}/{m.unit} (Supplier: {m.supplier.business_name if m.supplier else 'Unknown'})"
                )
            materials_info = "\n".join(materials_list)
        else:
            materials_info = "No materials listed yet."
    except Exception as e:
        logger.warning(f"Failed to fetch materials: {e}")
        materials_info = "Materials data not available."
    
    response, used_fallback, error_type = await safe_openai_call(
        messages=[
            {
                "role": "system",
                "content": f"""You are Agent SAMAGRI (सामग्री), the Supplier & Materials Advisor for the Ooumph SHG marketplace.

Your capabilities:
- SUPPLIER SEARCH: Help find verified suppliers for raw materials
- QUOTE REQUESTS: Guide users on requesting price quotes from suppliers
- BULK PURCHASE COORDINATION: Help organize group buying to save costs
- PRICE COMPARISON: Compare materials across different suppliers
- MATERIAL RECOMMENDATIONS: Suggest quality materials for specific products

User's Profile Context:
{profile_context}

User's District: {district}

ALL Available Suppliers in the Platform:
{suppliers_info}

Available Materials:
{materials_info}

Guidelines:
- ALWAYS mention specific suppliers from the list above with their names and ratings
- Mention specific materials and their prices when relevant
- Recommend verified suppliers with good ratings
- Suggest bulk purchases for cost savings (15-25% typically)
- Guide users to Raw Materials marketplace for full catalog
- Explain how to request quotes from suppliers
- Keep responses under 150 words
- Use simple language suitable for rural SHG women
- Always suggest actionable next steps"""
            },
            {"role": "user", "content": query}
        ],
        temperature=0.7,
        max_tokens=250,
        agent_name="SAMAGRI"
    )
    
    if not used_fallback and response:
        reply = response.choices[0].message.content.strip()
        return {"reply": reply, "agent": "SAMAGRI"}
    
    logger.info("Using dynamic fallback response for SAMAGRI agent", extra={"reason": error_type})
    
    fetched_data = {
        "suppliers": suppliers_info,
        "materials": materials_info
    }
    reply = generate_dynamic_fallback(query, "SAMAGRI", fetched_data, user_data)

    return {"reply": reply, "agent": "SAMAGRI"}

async def vishwas_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Vishwas agent - Finance & Wallet Specialist"""
    user_id = user_data.get("id")
    
    trust_coins = user_data.get("trust_coins", 0)
    trust_score = user_data.get("trust_score", 50)
    trust_badge = user_data.get('trust_badge', 'Bronze')
    
    wallet_info = f"Trust Coins: {trust_coins}, Trust Score: {trust_score}, Badge: {trust_badge}"
    transactions_info = "No recent transactions."
    
    try:
        if user_id:
            recent_transactions = db.query(CoinTransaction).filter(
                CoinTransaction.user_id == user_id
            ).order_by(desc(CoinTransaction.created_at)).limit(5).all()
            
            if recent_transactions:
                tx_list = []
                for tx in recent_transactions:
                    tx_type = tx.transaction_type.value if tx.transaction_type else "Unknown"
                    tx_list.append(f"• {tx_type}: {tx.amount} coins - {tx.description or 'No description'} ({tx.created_at.strftime('%Y-%m-%d') if tx.created_at else 'Unknown date'})")
                transactions_info = "\n".join(tx_list)
    except Exception as e:
        logger.warning(f"Failed to fetch transactions for VISHWAS: {e}")
    
    response, used_fallback, error_type = await safe_openai_call(
        messages=[
            {
                "role": "system",
                "content": f"""You are Agent VISHWAS (विश्वास), the Finance & Wallet Specialist for the Ooumph SHG marketplace.

Your capabilities:
- BALANCE QUERIES: Handle "what is my balance", "trust coins", "how many coins" requests
- TRANSACTION HISTORY: Show recent transactions and their details
- WALLET CONNECTION HELP: Guide users on connecting and using their wallet
- REDEMPTION GUIDANCE: Explain how to redeem trust coins for benefits
- TRUST SCORE EXPLANATIONS: Explain trust badges and how to improve them

Current User's Wallet Status:
{wallet_info}

Recent Transactions:
{transactions_info}

Guidelines:
- ALWAYS provide current balance when asked: "Your trust coin balance is {trust_coins} coins"
- Mention specific transactions from the list when discussing history
- Explain trust coin earning opportunities (completing orders: +10 coins, 5-star reviews: +15 coins, referrals: +20 coins)
- Guide users to Wallet page for full transaction history
- Explain redemption options clearly (discounts, premium features)
- Be encouraging about improving trust scores
- Keep responses under 120 words
- Use simple language suitable for rural SHG women"""
            },
            {"role": "user", "content": query}
        ],
        temperature=0.7,
        max_tokens=250,
        agent_name="VISHWAS"
    )
    
    if not used_fallback and response:
        reply = response.choices[0].message.content.strip()
        return {"reply": reply, "agent": "VISHWAS"}
    
    logger.info("Using dynamic fallback response for VISHWAS agent", extra={"reason": error_type})
    
    fetched_data = {
        "wallet": wallet_info,
        "transactions": transactions_info
    }
    reply = generate_dynamic_fallback(query, "VISHWAS", fetched_data, user_data)

    return {"reply": reply, "agent": "VISHWAS"}

async def sampark_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Sampark agent - Community Guide"""
    user_id = user_data.get("id")
    hierarchy_level = user_data.get("hierarchy_level", "SHG")
    district = user_data.get("district", "Andhra Pradesh")
    profile_context = await get_user_profile_context(user_id, db) if user_id else "No profile data available."
    
    posts_info = "No community posts available."
    users_info = "No users data available."
    
    try:
        all_posts = db.query(Post).order_by(desc(Post.created_at)).limit(10).all()
        if all_posts:
            posts_list = []
            for p in all_posts:
                post_type = "📢 Announcement" if p.is_announcement else "📝 Post"
                posts_list.append(f"• {post_type}: {p.title or p.content[:50]}... by User #{p.user_id}")
            posts_info = "\n".join(posts_list)
    except Exception as e:
        logger.warning(f"Failed to fetch posts for SAMPARK: {e}")
    
    try:
        users_count = db.query(User).count()
        shg_count = db.query(User).filter(User.hierarchy_level == "SHG").count()
        slf_count = db.query(User).filter(User.hierarchy_level == "SLF").count()
        tlf_count = db.query(User).filter(User.hierarchy_level == "TLF").count()
        users_info = f"Total Users: {users_count} (SHG: {shg_count}, SLF: {slf_count}, TLF: {tlf_count})"
    except Exception as e:
        logger.warning(f"Failed to fetch user stats for SAMPARK: {e}")
    
    response, used_fallback, error_type = await safe_openai_call(
        messages=[
            {
                "role": "system",
                "content": f"""You are Agent SAMPARK (संपर्क), the Community Guide for the Ooumph SHG marketplace.

Your capabilities:
- FEDERATION HIERARCHY: Explain SHG → SLF → TLF structure and roles
- COMMUNITY POSTS: Share posts, announcements, alerts, and community news
- PEER SHG CONNECTIONS: Help connect with other SHGs in the district
- DISTRICT OVERVIEW: Provide information about the local SHG network
- SUPPORT COORDINATION: Guide users to appropriate federation support

User's Profile Context:
{profile_context}

User's Hierarchy Level: {hierarchy_level}
District: {district}

Community Statistics:
{users_info}

Recent Community Posts:
{posts_info}

Federation Structure:
- SHG (Self Help Group): Base level, 10-20 members
- SLF (Slum Level Federation): Cluster of SHGs, coordinator support
- TLF (Town Level Federation): District leadership, admin portal access

Guidelines:
- Mention specific posts and announcements by title when relevant
- Explain federation structure clearly and simply
- Guide users to appropriate contacts based on their needs
- Help SHGs connect with peers for collaboration
- Keep responses under 120 words
- Use simple language suitable for rural SHG women"""
            },
            {"role": "user", "content": query}
        ],
        temperature=0.7,
        max_tokens=250,
        agent_name="SAMPARK"
    )
    
    if not used_fallback and response:
        reply = response.choices[0].message.content.strip()
        return {"reply": reply, "agent": "SAMPARK"}
    
    logger.info("Using dynamic fallback response for SAMPARK agent", extra={"reason": error_type})
    
    fetched_data = {
        "community": posts_info,
        "users": users_info
    }
    reply = generate_dynamic_fallback(query, "SAMPARK", fetched_data, user_data)

    return {"reply": reply, "agent": "SAMPARK"}

async def stream_agent_response(
    agent: str,
    query: str,
    user_data: dict,
    db: Session,
    language: str = "English"
) -> AsyncGenerator[Tuple[str, bool], None]:
    """
    Stream agent response with caching support.
    Yields tuples of (content_chunk, is_done).
    """
    cached = await _get_cached_response(query, agent, language)
    if cached:
        yield cached, False
        yield "", True
        return
    
    full_response = ""
    
    try:
        if agent == "VAANI":
            async for chunk, done in _stream_vaani_response(query, user_data, language):
                if not done:
                    full_response += chunk
                yield chunk, done
        elif agent == "BAZAAR":
            async for chunk, done in _stream_bazaar_response(query, user_data, language):
                if not done:
                    full_response += chunk
                yield chunk, done
        elif agent == "JODI":
            async for chunk, done in _stream_jodi_response(query, user_data, language):
                if not done:
                    full_response += chunk
                yield chunk, done
        elif agent == "SAMAGRI":
            async for chunk, done in _stream_samagri_response(query, user_data, language):
                if not done:
                    full_response += chunk
                yield chunk, done
        elif agent == "VISHWAS":
            async for chunk, done in _stream_vishwas_response(query, user_data, language):
                if not done:
                    full_response += chunk
                yield chunk, done
        elif agent == "SAMPARK":
            async for chunk, done in _stream_sampark_response(query, user_data, language):
                if not done:
                    full_response += chunk
                yield chunk, done
        elif agent == "SUPPORT":
            async for chunk, done in _stream_support_response(query, user_data, language):
                if not done:
                    full_response += chunk
                yield chunk, done
        else:
            async for chunk, done in _stream_vaani_response(query, user_data, language):
                if not done:
                    full_response += chunk
                yield chunk, done
        
        if full_response:
            await _cache_response(query, agent, language, full_response)
            
    except Exception as e:
        yield f"Error: {str(e)}", False
        yield "", True


async def _stream_vaani_response(
    query: str,
    user_data: dict,
    language: str,
    profile_context: str = "No profile data available."
) -> AsyncGenerator[Tuple[str, bool], None]:
    """Stream Vaani agent response using OpenAI streaming API"""
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            stream = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are Agent VAANI (वाणी), the friendly general assistant for the Ooumph SHG marketplace.

You are ACTION-ORIENTED and HELPFUL. Always guide users toward specific actions they can take.

User's Profile Context:
{profile_context}

Your primary areas:
- Products (selling, buying, listing, pricing)
- Orders and order management
- Buyers and suppliers
- Raw materials and procurement
- Trust scores and badges
- Market demand and pricing insights
- Delivery and shipping
- General marketplace navigation

You DO NOT answer questions about:
- General knowledge, news, weather, sports, entertainment
- Politics, religion, or personal advice
- Topics unrelated to the Ooumph marketplace

If asked about non-marketplace topics, politely redirect: "I'm here to help with your SHG marketplace needs - products, buyers, orders, and trust scores. What would you like help with?"

ACTION-ORIENTED Guidelines:
- Respond in {language}
- Be concise (under 80 words)
- Use simple language for rural women
- Be encouraging and supportive
- Use traditional greetings (Namaste, Vanakkam)
- ALWAYS suggest a specific action the user can take
- Guide users to relevant pages: Dashboard, Sell Product, Orders, Wallet, Market Analyzer
- Mention specific features they can use
- Provide next steps, not just information"""
                    },
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=150,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content, False
            
            yield "", True
            return
        except Exception:
            pass
    
    fallback = get_fallback_vaani_response(query, user_data)
    for word in fallback.split():
        yield word + " ", False
        import asyncio
        await asyncio.sleep(0.02)
    yield "", True


async def _stream_bazaar_response(
    query: str,
    user_data: dict,
    language: str,
    profile_context: str = "No profile data available.",
    market_info: str = "Market data unavailable."
) -> AsyncGenerator[Tuple[str, bool], None]:
    """Stream Bazaar Buddhi agent response"""
    district = user_data.get("district", "Andhra Pradesh")
    
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            stream = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are Agent BAZAAR (बाज़ार), the Market Expert for the Ooumph SHG marketplace.

Your capabilities:
- MARKET PRICE ANALYSIS: Provide current market prices and trends
- DEMAND TRENDS: Show what products are in high demand
- PRODUCT RECOMMENDATIONS: Suggest products to make/sell
- COMPETITION ANALYSIS: Help understand market positioning
- SEASONAL INSIGHTS: Advise on best times to sell

User's Profile Context:
{profile_context}

Market Data for {district}:
{market_info}

Guidelines:
- Respond in {language}
- Provide specific numbers and percentages when possible
- Suggest actionable pricing strategies
- Recommend trending product categories
- Mention seasonal opportunities
- Guide users to Market Analyzer for detailed analysis
- Keep responses under 100 words
- Use simple language suitable for rural SHG women
- Always suggest next steps"""
                    },
                    {"role": "user", "content": f"User from {district} asks: {query}"}
                ],
                temperature=0.7,
                max_tokens=200,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content, False
            
            yield "", True
            return
        except Exception:
            pass
    
    fallback = f"Agent BAZAAR here! Market insights for {district}:\n\n"
    fallback += f"📊 Market Trends:\n{market_info}\n\n"
    fallback += f"• Current trends show good demand for handmade products\n"
    fallback += f"• Premium quality products can command 15-20% higher prices\n"
    fallback += "Use the Market Analyzer for detailed insights."
    
    for word in fallback.split():
        yield word + " ", False
        import asyncio
        await asyncio.sleep(0.02)
    yield "", True


async def _stream_jodi_response(
    query: str,
    user_data: dict,
    language: str,
    orders_context: str = "No order data available."
) -> AsyncGenerator[Tuple[str, bool], None]:
    """Stream Jodi agent response"""
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            stream = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are Agent JODI (जोड़ी), the Order Management Specialist for the Ooumph SHG marketplace.

Your capabilities:
- ORDER STATUS QUERIES: Handle "where is my order", "track order", "order status" requests
- DELIVERY ADDRESS UPDATES: Help with "update delivery address", "change address" requests  
- ORDER CANCELLATION: Process "cancel order" requests with proper guidance
- ORDER HISTORY: Show past orders and their details

Current User's Orders Context:
{orders_context}

Guidelines:
- If user asks about orders without providing order ID, ask for the order number
- Always guide users to the Orders page for detailed tracking
- For address changes, explain the process and any time limitations
- For cancellations, mention any applicable policies
- Be helpful and action-oriented - suggest next steps
- Keep responses under 100 words
- Use simple language suitable for rural SHG women
- Include relevant order details from the context when available"""
                    },
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=200,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content, False
            
            yield "", True
            return
        except Exception:
            pass
    
    fallback = f"Agent JODI here! I help with order management.\n\n"
    fallback += f"📋 Your Recent Orders:\n{orders_context}\n\n"
    fallback += "I can help you:\n"
    fallback += "• Track order status\n"
    fallback += "• Update delivery address\n"
    fallback += "• Cancel orders\n\n"
    fallback += "Please provide your order number or go to Orders page."
    
    for word in fallback.split():
        yield word + " ", False
        import asyncio
        await asyncio.sleep(0.02)
    yield "", True


async def _stream_samagri_response(
    query: str,
    user_data: dict,
    language: str,
    profile_context: str = "No profile data available.",
    suppliers_info: str = "No supplier data available."
) -> AsyncGenerator[Tuple[str, bool], None]:
    """Stream Samagri agent response"""
    district = user_data.get("district", "Andhra Pradesh")
    
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            stream = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are Agent SAMAGRI (सामग्री), the Supplier & Materials Advisor for the Ooumph SHG marketplace.

Your capabilities:
- SUPPLIER SEARCH: Help find verified suppliers for raw materials
- QUOTE REQUESTS: Guide users on requesting price quotes from suppliers
- BULK PURCHASE COORDINATION: Help organize group buying to save costs
- PRICE COMPARISON: Compare materials across different suppliers
- MATERIAL RECOMMENDATIONS: Suggest quality materials for specific products

User's Profile Context:
{profile_context}

Available Suppliers in {district}:
{suppliers_info}

Guidelines:
- Recommend verified suppliers with good ratings
- Suggest bulk purchases for cost savings (15-25% typically)
- Guide users to Raw Materials marketplace for full catalog
- Explain how to request quotes from suppliers
- Mention delivery options and timeframes
- Keep responses under 100 words
- Use simple language suitable for rural SHG women
- Always suggest actionable next steps"""
                    },
                    {"role": "user", "content": f"User from {district} asks: {query}"}
                ],
                temperature=0.7,
                max_tokens=200,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content, False
            
            yield "", True
            return
        except Exception:
            pass
    
    fallback = f"Agent SAMAGRI here! Your Supplier & Materials guide for {district}.\n\n"
    fallback += f"📦 Verified Suppliers:\n{suppliers_info}\n\n"
    fallback += "💡 Tip: Join bulk requests to save 15-25% on materials!\n\n"
    fallback += "Visit Raw Materials marketplace to browse all options!"
    
    for word in fallback.split():
        yield word + " ", False
        import asyncio
        await asyncio.sleep(0.02)
    yield "", True


async def _stream_vishwas_response(
    query: str,
    user_data: dict,
    language: str,
    wallet_context: str = "No wallet data available."
) -> AsyncGenerator[Tuple[str, bool], None]:
    """Stream Vishwas agent response"""
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            stream = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are Agent VISHWAS (विश्वास), the Finance & Wallet Specialist for the Ooumph SHG marketplace.

Your capabilities:
- BALANCE QUERIES: Handle "what is my balance", "trust coins", "how many coins" requests
- TRANSACTION HISTORY: Show recent transactions and their details
- WALLET CONNECTION HELP: Guide users on connecting and using their wallet
- REDEMPTION GUIDANCE: Explain how to redeem trust coins for benefits
- TRUST SCORE EXPLANATIONS: Explain trust badges and how to improve them

Current User's Wallet Context:
{wallet_context}

Guidelines:
- Always provide current balance when asked
- Explain trust coin earning opportunities (completing orders, referrals, etc.)
- Guide users to Wallet page for full transaction history
- Explain redemption options clearly (discounts, premium features, etc.)
- Be encouraging about improving trust scores
- Keep responses under 100 words
- Use simple language suitable for rural SHG women
- Suggest actionable next steps"""
                    },
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=200,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content, False
            
            yield "", True
            return
        except Exception:
            pass
    
    fallback = f"Agent VISHWAS here! Your Finance & Wallet summary:\n\n"
    fallback += f"{wallet_context}\n\n"
    fallback += "💡 Ways to earn Trust Coins:\n"
    fallback += "• Complete orders on time (+10 coins)\n"
    fallback += "• Get 5-star reviews (+15 coins)\n"
    fallback += "• Refer new members (+20 coins)\n\n"
    fallback += "Go to Wallet page to redeem coins for discounts!"
    
    for word in fallback.split():
        yield word + " ", False
        import asyncio
        await asyncio.sleep(0.02)
    yield "", True


async def _stream_sampark_response(
    query: str,
    user_data: dict,
    language: str,
    profile_context: str = "No profile data available.",
    posts_info: str = "No recent announcements."
) -> AsyncGenerator[Tuple[str, bool], None]:
    """Stream Sampark agent response"""
    hierarchy_level = user_data.get("hierarchy_level", "SHG")
    district = user_data.get("district", "Andhra Pradesh")
    
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            stream = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are Agent SAMPARK (संपर्क), the Community Guide for the Ooumph SHG marketplace.

Your capabilities:
- FEDERATION HIERARCHY: Explain SHG → SLF → TLF structure and roles
- COMMUNITY POSTS: Share announcements, alerts, and community news
- PEER SHG CONNECTIONS: Help connect with other SHGs in the district
- DISTRICT OVERVIEW: Provide information about the local SHG network
- SUPPORT COORDINATION: Guide users to appropriate federation support

User's Profile Context:
{profile_context}

User's Hierarchy Level: {hierarchy_level}
District: {district}

Recent Announcements:
{posts_info}

Federation Structure:
- SHG (Self Help Group): Base level, 10-20 members
- SLF (Slum Level Federation): Cluster of SHGs, coordinator support
- TLF (Town Level Federation): District leadership, admin portal access

Guidelines:
- Explain federation structure clearly and simply
- Guide users to appropriate contacts based on their needs
- Share relevant community announcements
- Help SHGs connect with peers for collaboration
- Mention Admin Portal for TLF/SLF members
- Keep responses under 100 words
- Use simple language suitable for rural SHG women
- Suggest actionable next steps"""
                    },
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=200,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content, False
            
            yield "", True
            return
        except Exception:
            pass
    
    fallback = f"Agent SAMPARK here! Your Community Guide for {district}.\n\n"
    fallback += f"👤 Your Level: {hierarchy_level}\n\n"
    
    if hierarchy_level == "SHG":
        fallback += "🏛️ Federation Structure:\n"
        fallback += "• SHG (Your Group) → Base level\n"
        fallback += "• SLF (Slum Level Federation) → Your coordinator\n"
        fallback += "• TLF (Town Level Federation) → District leadership\n\n"
        fallback += f"📢 Recent Announcements:\n{posts_info}\n\n"
        fallback += "Contact your SLF coordinator for district-level support!"
    else:
        fallback += f"As a {hierarchy_level}, you can:\n"
        fallback += "• View and manage federation members\n"
        fallback += "• Send community alerts\n"
        fallback += "• Track member performance\n\n"
        fallback += "Use the Admin Portal for these features."
    
    for word in fallback.split():
        yield word + " ", False
        import asyncio
        await asyncio.sleep(0.02)
    yield "", True


async def _stream_support_response(
    query: str,
    user_data: dict,
    language: str,
    profile_context: str = "No profile data available."
) -> AsyncGenerator[Tuple[str, bool], None]:
    """Stream Support agent response"""
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            stream = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are Agent SUPPORT, the Navigation & Help Specialist for the Ooumph SHG marketplace.

Your capabilities:
- APP NAVIGATION: Help users find and use different features
- FEATURE EXPLANATIONS: Explain how marketplace features work
- TROUBLESHOOTING: Guide users through common issues
- ONBOARDING HELP: Assist new users with getting started
- BUG REPORTING: Guide users on how to report issues

User's Profile Context:
{profile_context}

App Navigation Guide:
- Dashboard: Home screen with overview
- Sell Product: Add and manage your product listings
- My Products: View and edit your listed products
- Orders: Track and manage orders
- Market Analyzer: View market trends and pricing
- Raw Materials: Find suppliers and materials
- Wallet: Trust coins and transactions
- Community: Connect with other SHGs
- Profile: Manage your account settings

Guidelines:
- Respond in {language}
- Provide clear step-by-step navigation instructions
- Be patient and helpful
- Use simple language suitable for rural SHG women
- Suggest specific pages and features to try
- Keep responses under 100 words
- Always offer to help with follow-up questions"""
                    },
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=200,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content, False
            
            yield "", True
            return
        except Exception:
            pass
    
    fallback = "Agent SUPPORT here! I can help you navigate the app.\n\n"
    fallback += "📱 Quick Navigation Guide:\n"
    fallback += "• Dashboard → Your home screen\n"
    fallback += "• Sell Product → Add new products\n"
    fallback += "• Orders → Track your orders\n"
    fallback += "• Market Analyzer → Check prices & trends\n"
    fallback += "• Raw Materials → Find suppliers\n"
    fallback += "• Wallet → View trust coins\n\n"
    fallback += "What would you like help with?"
    
    for word in fallback.split():
        yield word + " ", False
        import asyncio
        await asyncio.sleep(0.02)
    yield "", True


async def save_chat_message(user_id: int, session_id: str, role: str,
                           content: str, agent_triggered: Optional[str] = None,
                           language: str = "English",
                           audio_url: Optional[str] = None,
                           transcription: Optional[str] = None,
                           db: Session = None) -> Optional[models.ChatHistory]:
    """Save chat message to history"""
    try:
        chat = models.ChatHistory(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content,
            agent_triggered=agent_triggered,
            language=language,
            audio_url=audio_url,
            transcription=transcription,
            created_at=datetime.now()
        )

        db.add(chat)
        db.commit()

        return chat
    except Exception:
        return None
