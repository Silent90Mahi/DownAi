"""
Ooumph Agentic Orchestrator
Routes user queries to appropriate AI agents
"""
import os
import uuid
import json
import hashlib
import time
from datetime import datetime
from typing import Dict, Optional, AsyncGenerator, Any, Tuple
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from . import voice_service, market_service, matching_service, supplier_service
from .. import models
from ..models import Order, CoinTransaction, User, Product, Post, Supplier, Material
from core.config import settings
from sqlalchemy import desc

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


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
You manage the following AI agents:

1. Vaani (वाणी) - General Assistant
   - General conversation and help
   - Multilingual support (English, Telugu, Hindi, Urdu)
   - Always friendly, warm, and helpful

2. Market Expert - Market Intelligence Agent
   - Market demand analysis
   - Price recommendations
   - Seasonal trends
   - Competition analysis

3. Order Assistant - Order Management Agent
   - Order tracking and status
   - Delivery management
   - Order cancellation
   - Order history

4. Supplier Advisor - Supplier Network Agent
   - Supplier search
   - Bulk purchase coordination
   - Price comparison
   - Supplier ratings

5. Community Guide - Community Hub Agent
   - Federation hierarchy information
   - Community posts and alerts
   - Peer SHG connections
   - District overview

6. Finance Assistant - Wallet & Payments Agent
   - Trust coin balance
   - Transaction history
   - Wallet connections
   - Payment simulation

7. Support Bot - General Support Agent
   - App navigation help
   - Troubleshooting
   - Feature explanations
   - Bug reporting

Analyze the user's query and determine which agent is most appropriate.
Reply with ONLY the agent name: VAANI, BAZAAR, JODI, SAMAGRI, SAMPARK, VISHWAS, SUPPORT, or GENERAL.
For general queries or greetings, use VAANI.
"""

async def process_chat_query(query: str, user_data: dict, db: Session,
                            language: str = "English") -> Dict:
    """
    Process chat query and route to appropriate agent
    """
    session_id = str(uuid.uuid4())

    # Save user message to chat history
    await save_chat_message(
        user_data.get("id"),
        session_id,
        "user",
        query,
        language=language,
        db=db
    )

    try:
        # Determine which agent to use
        agent_decision = await determine_agent(query, db)

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
            "suggestions": response_data.get("suggestions", [])
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
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query}
                ],
                temperature=0
            )
            agent_decision = response.choices[0].message.content.strip().upper()
        else:
            # Keyword-based fallback
            agent_decision = keyword_based_routing(query)
    except Exception:
        agent_decision = keyword_based_routing(query)

    # Map to expected values
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
    
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            response = await client.chat.completions.create(
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
                max_tokens=200
            )
            reply = response.choices[0].message.content.strip()
            return {"reply": reply, "agent": "SUPPORT"}
        except Exception:
            pass
    
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
    profile_context = await get_user_profile_context(user_id, db) if user_id else "No profile data available."
    
    try:
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
            response = await client.chat.completions.create(
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
                max_tokens=150
            )
            reply = response.choices[0].message.content.strip()
        else:
            reply = get_fallback_vaani_response(query, user_data)

        return {"reply": reply, "agent": "VAANI"}
    except Exception as e:
        print(f"Vaani OpenAI error: {e}")
        return {"reply": get_fallback_vaani_response(query, user_data), "agent": "VAANI"}

def get_fallback_vaani_response(query: str, user_data: dict) -> str:
    """Fallback Vaani responses - Action-oriented"""
    query_lower = query.lower()

    if any(kw in query_lower for kw in ["hello", "hi", "namaste", "hey", "vanakkam"]):
        return "Namaste! I'm here to help with your SHG marketplace. What would you like to do today? Sell products, check orders, or explore market prices?"

    if any(kw in query_lower for kw in ["help", "what can you do", "how can you help"]):
        return "I can help you take action! 🛒 Sell products → Go to 'Sell Product', 📦 Track orders → Go to 'Orders', 💰 Check prices → Go to 'Market Analyzer', 🏭 Find suppliers → Go to 'Raw Materials'. What would you like to do?"

    if any(kw in query_lower for kw in ["sell", "selling", "list", "add product"]):
        return "Ready to sell? 📱 Go to Dashboard → Sell Product → Add photos, description & price → Publish! Your product will reach thousands of verified buyers. Start now!"

    if any(kw in query_lower for kw in ["buyer", "buyers", "find buyer", "customer"]):
        return "Find buyers now! 📱 Go to Dashboard → Buyer Matches → Browse interested buyers → Send proposals. Higher trust scores get priority matching!"

    if any(kw in query_lower for kw in ["price", "pricing", "market price", "cost", "rate"]):
        return "Check market prices now! 📱 Go to Market Analyzer → Select your product category → View demand trends & recommended prices. Set competitive prices today!"

    if any(kw in query_lower for kw in ["order", "orders", "delivery", "shipping", "track"]):
        return "Track your orders now! 📱 Go to Orders → Select order → View real-time status. You can also update address or request cancellation if needed."

    if any(kw in query_lower for kw in ["raw material", "supplier", "sourcing", "materials"]):
        return "Find suppliers now! 📱 Go to Raw Materials → Search by category → Compare prices & ratings → Request quote or join bulk purchase. Save 15-25%!"

    if any(kw in query_lower for kw in ["trust", "score", "badge", "coins", "balance", "wallet"]):
        return f"Your trust score: {user_data.get('trust_score', 50)} | Badge: {user_data.get('trust_badge', 'Bronze')} | Coins: {user_data.get('trust_coins', 0)}. 📱 Go to Wallet to redeem coins for discounts!"

    if any(kw in query_lower for kw in ["navigate", "how to", "where", "find page", "go to"]):
        return "I can guide you! Main pages: Dashboard (home), Sell Product (add listings), Orders (track), Market Analyzer (prices), Raw Materials (suppliers), Wallet (coins). Which do you need?"

    if "thank" in query_lower:
        return "You're welcome! Is there anything else you'd like to do? I'm here to help you succeed in your SHG business! 🌟"

    return "I specialize in helping with your SHG marketplace - products, buyers, orders, and trust scores. What action would you like to take today?"

async def bazaar_buddhi_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Bazaar Buddhi agent - Market Expert"""
    user_id = user_data.get("id")
    district = user_data.get("district", "Andhra Pradesh")
    profile_context = await get_user_profile_context(user_id, db) if user_id else "No profile data available."
    
    try:
        market_data = db.query(models.MarketData).filter(
            models.MarketData.district == district
        ).order_by(desc(models.MarketData.date)).limit(3).all()
        market_info = "\n".join([
            f"• {m.category}: Demand={m.demand_level or 'N/A'}, Trend={m.demand_trend or 'Stable'}"
            for m in market_data
        ]) if market_data else "No market data available for your district."
    except Exception:
        market_info = "Market data temporarily unavailable."
    
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are Agent BAZAAR (बाज़ार), the Market Expert for the Ooumph SHG marketplace.

Your capabilities:
- MARKET PRICE ANALYSIS: Provide current market prices and trends for products
- DEMAND TRENDS: Show what products are in high demand in the user's district
- PRODUCT RECOMMENDATIONS: Suggest products to make/sell based on market conditions
- COMPETITION ANALYSIS: Help understand market saturation and positioning
- SEASONAL INSIGHTS: Advise on best times to sell specific products

User's Profile Context:
{profile_context}

Market Data for {district}:
{market_info}

Guidelines:
- Provide specific numbers and percentages when possible
- Suggest actionable pricing strategies
- Recommend trending product categories
- Mention seasonal opportunities (festivals, harvest, etc.)
- Guide users to Market Analyzer page for detailed analysis
- Keep responses under 100 words
- Use simple language suitable for rural SHG women
- Always suggest next steps (check prices, list products, etc.)"""
                    },
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=200
            )
            reply = response.choices[0].message.content.strip()
            return {"reply": reply, "agent": "BAZAAR"}
        except Exception:
            pass
    
    suggestions = [
        f"Current market trends in {district} show good demand for handmade products",
        "Consider listing on multiple platforms for better visibility",
        "Premium quality products can command 15-20% higher prices",
        "The upcoming festival season is a good time to sell"
    ]

    reply = f"Agent BAZAAR here! Market insights for {district}:\n\n"
    reply += f"📊 Market Trends:\n{market_info}\n\n"
    reply += "💡 Key Insights:\n"
    for s in suggestions[:3]:
        reply += f"• {s}\n"
    reply += "\nVisit Market Analyzer page for detailed product-level insights!"

    return {"reply": reply, "agent": "BAZAAR", "suggestions": suggestions}

async def jodi_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Jodi agent - Order Management Specialist"""
    user_id = user_data.get("id")
    orders_context = await get_user_orders_context(user_id, db) if user_id else "No order data available."
    
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            response = await client.chat.completions.create(
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
                max_tokens=200
            )
            reply = response.choices[0].message.content.strip()
            return {"reply": reply, "agent": "JODI"}
        except Exception:
            pass
    
    reply = "Agent JODI here! I help with order management.\n\n"
    reply += f"📋 Your Recent Orders:\n{orders_context}\n\n"
    reply += "I can help you:\n"
    reply += "• Track order status\n"
    reply += "• Update delivery address\n"
    reply += "• Cancel orders\n\n"
    reply += "Please provide your order number or go to Orders page for details."

    return {"reply": reply, "agent": "JODI"}

async def samagri_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Samagri agent - Supplier & Materials Advisor"""
    user_id = user_data.get("id")
    district = user_data.get("district", "Andhra Pradesh")
    profile_context = await get_user_profile_context(user_id, db) if user_id else "No profile data available."
    
    try:
        suppliers = db.query(Supplier).filter(
            Supplier.district == district,
            Supplier.is_verified == True
        ).limit(3).all()
        suppliers_info = "\n".join([
            f"• {s.business_name} - {s.business_type or 'General'} (Rating: {s.rating}★)"
            for s in suppliers
        ]) if suppliers else "No verified suppliers in your district yet."
    except Exception:
        suppliers_info = "Unable to fetch supplier data."
    
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            response = await client.chat.completions.create(
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
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=200
            )
            reply = response.choices[0].message.content.strip()
            return {"reply": reply, "agent": "SAMAGRI"}
        except Exception:
            pass
    
    reply = f"Agent SAMAGRI here! Your Supplier & Materials guide for {district}.\n\n"
    reply += f"📦 Verified Suppliers:\n{suppliers_info}\n\n"
    reply += "💡 Tip: Join bulk requests to save 15-25% on materials!\n\n"
    reply += "I can help you:\n"
    reply += "• Find suppliers for specific materials\n"
    reply += "• Request price quotes\n"
    reply += "• Coordinate bulk purchases\n\n"
    reply += "Visit Raw Materials marketplace to browse all options!"

    return {"reply": reply, "agent": "SAMAGRI"}

async def vishwas_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Vishwas agent - Finance & Wallet Specialist"""
    user_id = user_data.get("id")
    wallet_context = await get_user_wallet_context(user_id, db) if user_id else "No wallet data available."
    
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            response = await client.chat.completions.create(
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
                max_tokens=200
            )
            reply = response.choices[0].message.content.strip()
            return {"reply": reply, "agent": "VISHWAS"}
        except Exception:
            pass
    
    reply = f"Agent VISHWAS here! Your Finance & Wallet summary:\n\n"
    reply += f"{wallet_context}\n\n"
    reply += "💡 Ways to earn Trust Coins:\n"
    reply += "• Complete orders on time (+10 coins)\n"
    reply += "• Get 5-star reviews (+15 coins)\n"
    reply += "• Refer new members (+20 coins)\n\n"
    reply += "Go to Wallet page to redeem coins for discounts!"

    return {"reply": reply, "agent": "VISHWAS"}

async def sampark_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Sampark agent - Community Guide"""
    user_id = user_data.get("id")
    hierarchy_level = user_data.get("hierarchy_level", "SHG")
    district = user_data.get("district", "Andhra Pradesh")
    profile_context = await get_user_profile_context(user_id, db) if user_id else "No profile data available."
    
    try:
        recent_posts = db.query(Post).filter(
            Post.is_announcement == True
        ).order_by(desc(Post.created_at)).limit(3).all()
        posts_info = "\n".join([
            f"• {p.title or p.content[:50]}..." for p in recent_posts
        ]) if recent_posts else "No recent announcements."
    except Exception:
        posts_info = "Unable to fetch community posts."
    
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            response = await client.chat.completions.create(
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
                max_tokens=200
            )
            reply = response.choices[0].message.content.strip()
            return {"reply": reply, "agent": "SAMPARK"}
        except Exception:
            pass
    
    reply = f"Agent SAMPARK here! Your Community Guide for {district}.\n\n"
    reply += f"👤 Your Level: {hierarchy_level}\n\n"
    
    if hierarchy_level == "SHG":
        reply += "🏛️ Federation Structure:\n"
        reply += "• SHG (Your Group) → Base level\n"
        reply += "• SLF (Slum Level Federation) → Your coordinator\n"
        reply += "• TLF (Town Level Federation) → District leadership\n\n"
        reply += f"📢 Recent Announcements:\n{posts_info}\n\n"
        reply += "Contact your SLF coordinator for district-level support!"
    else:
        reply += f"As a {hierarchy_level}, you can:\n"
        reply += "• View and manage federation members\n"
        reply += "• Send community alerts\n"
        reply += "• Track member performance\n\n"
        reply += "Use the Admin Portal for these features."

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
