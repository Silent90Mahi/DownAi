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
from core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

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
    """Fallback keyword-based routing"""
    query_lower = query.lower()

    # Market Expert keywords
    if any(kw in query_lower for kw in ["market", "demand", "price", "sell", "trend", "competition", "pricing", "analyze"]):
        return "BAZAAR"

    # Order Assistant keywords
    if any(kw in query_lower for kw in ["order", "delivery", "track", "cancel", "shipment", "shipping", "status"]):
        return "JODI"

    # Supplier Advisor keywords
    if any(kw in query_lower for kw in ["supplier", "raw material", "bulk purchase", "sourcing", "materials", "vendor"]):
        return "SAMAGRI"

    # Finance Assistant keywords
    if any(kw in query_lower for kw in ["trust", "score", "badge", "coin", "wallet", "payment", "balance", "transaction", "redeem"]):
        return "VISHWAS"

    # Community Guide keywords
    if any(kw in query_lower for kw in ["federation", "slf", "tlf", "community", "district", "shg", "post", "comment"]):
        return "SAMPARK"

    # Support Bot keywords
    if any(kw in query_lower for kw in ["help", "support", "bug", "issue", "problem", "how to", "navigate", "feature"]):
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
    else:  # VAANI / GENERAL
        return await vaani_response(query, user_data, db, language)

async def vaani_response(query: str, user_data: dict, db: Session,
                        language: str) -> Dict:
    """Get response from Vaani agent using OpenAI - Focused on products only"""
    try:
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are Agent Vaani (वाणी), a product-focused AI assistant for SHG women in the Ooumph marketplace ecosystem.

IMPORTANT: You ONLY answer questions about:
- Products (selling, buying, listing, pricing)
- Orders and order management
- Buyers and suppliers
- Raw materials and procurement
- Trust scores and badges (related to marketplace transactions)
- Market demand and pricing insights
- Delivery and shipping
- Product categories (handicrafts, textiles, food products, etc.)

You DO NOT answer questions about:
- General knowledge, news, weather, sports, entertainment
- Politics, religion, or personal advice
- Topics unrelated to the Ooumph marketplace and products

If asked about non-product topics, politely redirect: "I'm here to help with your SHG marketplace needs - products, buyers, orders, and trust scores. Would you like help with any of these?"

Guidelines:
- Respond in {language}
- Be concise (under 80 words)
- Use simple language for rural women
- Be encouraging and supportive
- Use traditional greetings (Namaste, Vanakkam)
- Focus on practical marketplace advice
- Guide users to take action (list products, find buyers, etc.)"""
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
        # Log error for debugging
        print(f"Vaani OpenAI error: {e}")
        return {"reply": get_fallback_vaani_response(query, user_data), "agent": "VAANI"}

def get_fallback_vaani_response(query: str, user_data: dict) -> str:
    """Fallback Vaani responses - Product focused"""
    query_lower = query.lower()

    # Greetings
    if any(kw in query_lower for kw in ["hello", "hi", "namaste", "hey", "vanakkam"]):
        return "Namaste! I'm here to help with your SHG marketplace. Ask me about selling products, finding buyers, market prices, or orders!"

    # Product-related help
    if any(kw in query_lower for kw in ["help", "what can you do", "how can you help"]):
        return "I can help you with: 🛒 Selling your products, 📦 Finding buyers, 💰 Market pricing, 🏭 Raw materials, ⭐ Trust scores, 📝 Orders. What do you need help with?"

    # Selling products
    if any(kw in query_lower for kw in ["sell", "selling", "list", "add product"]):
        return "To sell products, go to 'Sell Product' from your dashboard. Add product details, set competitive prices using market insights, and reach thousands of verified buyers!"

    # Finding buyers
    if any(kw in query_lower for kw in ["buyer", "buyers", "find buyer", "customer"]):
        return "I'll help you find buyers! Use the 'Buyer Matches' feature to see verified buyers interested in your products. Higher trust scores get better matching priority!"

    # Market prices
    if any(kw in query_lower for kw in ["price", "pricing", "market price", "cost", "rate"]):
        return "Check 'Market Analyzer' for real-time pricing insights. It shows demand levels, competition, and recommends optimal prices for your products in your district!"

    # Orders
    if any(kw in query_lower for kw in ["order", "orders", "delivery", "shipping"]):
        return "View your orders in 'My Orders' section. Track delivery status, manage shipments, and see buyer details. On-time delivery improves your trust score!"

    # Raw materials
    if any(kw in query_lower for kw in ["raw material", "supplier", "sourcing", "materials"]):
        return "Use 'Raw Materials' marketplace to find verified suppliers. Join bulk requests with other SHGs to save 15-25% on procurement costs!"

    # Trust score
    if any(kw in query_lower for kw in ["trust", "score", "badge", "coins"]):
        return f"Your trust score is {user_data.get('trust_score', 50)}. Complete deliveries on time, maintain quality, and stay active to improve. Higher scores = better buyer access!"

    # Thank you
    if "thank" in query_lower:
        return "You're welcome! Let me know if you need help with products, buyers, or orders. 🌟"

    # Non-product query - polite redirect
    return "I specialize in helping with your SHG marketplace - products, buyers, orders, and trust scores. For marketplace assistance, what would you like to know?"

async def bazaar_buddhi_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Bazaar Buddhi agent"""
    district = user_data.get("district", "Andhra Pradesh")

    suggestions = [
        f"Current market trends in {district} show good demand for handmade products",
        "Consider listing on multiple platforms for better visibility",
        "Premium quality products can command 15-20% higher prices",
        "The upcoming festival season is a good time to sell"
    ]

    reply = f"Based on current market analysis, here's what I can tell you:\n\n"
    reply += f"• {suggestions[0]}\n"
    reply += f"• {suggestions[1]}\n"
    reply += f"• {suggestions[2]}\n\n"
    reply += "Would you like specific market analysis for a product? Use the Market Analyzer page for detailed insights."

    return {"reply": reply, "agent": "BAZAAR", "suggestions": suggestions}

async def jodi_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Jodi agent"""
    trust_score = user_data.get("trust_score", 50)

    reply = f"Agent Jodi here! I can help you find buyers for your products.\n\n"
    reply += f"Your current trust score is {trust_score}, which gives you {'priority ' if trust_score >= 70 else ''}access to verified buyers.\n\n"
    reply += "I've found several potential opportunities:\n"
    reply += "• 3 GeM government tenders matching handicrafts\n"
    reply += "• 5 wholesale buyers interested in SHG products\n"
    reply += "• 2 ONDC marketplace opportunities\n\n"
    reply += "Check the 'Sell Product' page or browse buyer requirements to connect with them!"

    return {"reply": reply, "agent": "JODI"}

async def samagri_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Samagri agent"""
    district = user_data.get("district", "Andhra Pradesh")

    reply = f"Agent Samagri reporting! I can help you source raw materials in {district}.\n\n"
    reply += "Available suppliers:\n"
    reply += "• Guntur Agro Traders - Agricultural supplies (Verified, 4.5★)\n"
    reply += "• Cooperative Mills Ltd - Textile materials (4.3★)\n"
    reply += "• Kurnool Farmers Co-op - Organic inputs (Verified, 4.6★)\n\n"
    reply += "💡 Tip: Join a bulk request to save 15-25% on raw materials!\n\n"
    reply += "Visit the Raw Materials marketplace to compare prices and place orders."

    return {"reply": reply, "agent": "SAMAGRI"}

async def vishwas_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Vishwas agent"""
    trust_score = user_data.get("trust_score", 50)
    trust_coins = user_data.get("trust_coins", 0)
    badge = user_data.get("trust_badge", "Bronze")

    reply = f"Agent Vishwas here! Your Trust & Compliance status:\n\n"
    reply += f"📊 Trust Score: {trust_score}/100\n"
    reply += f"🏅 Badge: {badge}\n"
    reply += f"💰 Trust Coins: {trust_coins}\n\n"

    if trust_score >= 90:
        reply += "Excellent! You're a Gold badge member with top trust score!"
    elif trust_score >= 70:
        reply += "Great progress! Maintain your performance to reach Gold badge."
    else:
        reply += "Complete more orders on time to improve your trust score!"

    reply += "\n\nYour trust score affects:\n"
    reply += "• Buyer matching priority\n"
    reply += "• Access to premium opportunities\n"
    reply += "• Bulk purchase benefits"

    return {"reply": reply, "agent": "VISHWAS"}

async def sampark_response(query: str, user_data: dict, db: Session) -> Dict:
    """Get response from Sampark agent"""
    hierarchy_level = user_data.get("hierarchy_level", "SHG")
    district = user_data.get("district", "Andhra Pradesh")

    reply = f"Agent Sampark - Community Orchestration\n\n"

    if hierarchy_level == "SHG":
        reply += f"Your SHG is part of the {district} district network.\n\n"
        reply += "Your federation structure:\n"
        reply += "• SHG (Your Group)\n"
        reply += "• SLF (Slum Level Federation) - Your coordinator\n"
        reply += "• TLF (Town Level Federation) - District leadership\n\n"
        reply += "For district-level support, contact your SLF coordinator."
    else:
        reply += f"As a {hierarchy_level}, you can view and manage your federation members.\n\n"
        reply += "Use the Admin Portal to:\n"
        reply += "• View federation statistics\n"
        reply += "• Send community alerts\n"
        reply += "• Track member performance"

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
    language: str
) -> AsyncGenerator[Tuple[str, bool], None]:
    """Stream Vaani agent response using OpenAI streaming API"""
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            stream = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are Agent Vaani (वाणी), a product-focused AI assistant for SHG women in the Ooumph marketplace ecosystem.

IMPORTANT: You ONLY answer questions about:
- Products (selling, buying, listing, pricing)
- Orders and order management
- Buyers and suppliers
- Raw materials and procurement
- Trust scores and badges (related to marketplace transactions)
- Market demand and pricing insights
- Delivery and shipping
- Product categories (handicrafts, textiles, food products, etc.)

You DO NOT answer questions about:
- General knowledge, news, weather, sports, entertainment
- Politics, religion, or personal advice
- Topics unrelated to the Ooumph marketplace and products

If asked about non-product topics, politely redirect: "I'm here to help with your SHG marketplace needs - products, buyers, orders, and trust scores. Would you like help with any of these?"

Guidelines:
- Respond in {language}
- Be concise (under 80 words)
- Use simple language for rural women
- Be encouraging and supportive
- Use traditional greetings (Namaste, Vanakkam)
- Focus on practical marketplace advice
- Guide users to take action (list products, find buyers, etc.)"""
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
    language: str
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
                        "content": f"""You are Agent Bazaar Buddhi (बाज़ार बुद्धि), a market intelligence specialist for the Ooumph SHG marketplace.

You provide:
- Market demand analysis
- Price recommendations
- Seasonal trends
- Competition analysis

Guidelines:
- Respond in {language}
- Be data-driven and specific
- Include actionable insights
- Keep responses under 100 words
- Mention specific numbers and percentages when possible"""
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
    
    fallback = f"Market Analysis for {district}:\n\n"
    fallback += f"• Current trends show good demand for handmade products\n"
    fallback += f"• Consider listing on multiple platforms for better visibility\n"
    fallback += f"• Premium quality products can command 15-20% higher prices\n"
    fallback += f"• The upcoming festival season is a good time to sell\n\n"
    fallback += "Use the Market Analyzer for detailed insights."
    
    for word in fallback.split():
        yield word + " ", False
        import asyncio
        await asyncio.sleep(0.02)
    yield "", True


async def _stream_jodi_response(
    query: str,
    user_data: dict,
    language: str
) -> AsyncGenerator[Tuple[str, bool], None]:
    """Stream Jodi agent response"""
    trust_score = user_data.get("trust_score", 50)
    
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            stream = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are Agent Jodi (जोड़ी), a buyer matching specialist for the Ooumph SHG marketplace.

You help with:
- Matching SHG products with buyers
- Government procurement opportunities
- Negotiation support

Guidelines:
- Respond in {language}
- Be practical and specific
- Mention buyer types and opportunities
- Keep responses under 100 words"""
                    },
                    {"role": "user", "content": f"User with trust score {trust_score} asks: {query}"}
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
    
    priority = "priority " if trust_score >= 70 else ""
    fallback = f"Buyer Matching Results:\n\n"
    fallback += f"Your trust score is {trust_score}, giving you {priority}access to verified buyers.\n\n"
    fallback += f"• 3 GeM government tenders matching handicrafts\n"
    fallback += f"• 5 wholesale buyers interested in SHG products\n"
    fallback += f"• 2 ONDC marketplace opportunities\n\n"
    fallback += f"Check 'Sell Product' to connect with buyers!"
    
    for word in fallback.split():
        yield word + " ", False
        import asyncio
        await asyncio.sleep(0.02)
    yield "", True


async def _stream_samagri_response(
    query: str,
    user_data: dict,
    language: str
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
                        "content": f"""You are Agent Samagri (सामग्री), a raw material procurement specialist for the Ooumph SHG marketplace.

You help with:
- Supplier search
- Bulk purchase coordination
- Price comparison

Guidelines:
- Respond in {language}
- List specific suppliers with ratings
- Mention cost-saving opportunities
- Keep responses under 100 words"""
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
    
    fallback = f"Raw Material Suppliers in {district}:\n\n"
    fallback += f"• Guntur Agro Traders - Agricultural supplies (4.5★)\n"
    fallback += f"• Cooperative Mills Ltd - Textile materials (4.3★)\n"
    fallback += f"• Kurnool Farmers Co-op - Organic inputs (4.6★)\n\n"
    fallback += f"💡 Join bulk requests to save 15-25%!\n\n"
    fallback += f"Visit Raw Materials marketplace for details."
    
    for word in fallback.split():
        yield word + " ", False
        import asyncio
        await asyncio.sleep(0.02)
    yield "", True


async def _stream_vishwas_response(
    query: str,
    user_data: dict,
    language: str
) -> AsyncGenerator[Tuple[str, bool], None]:
    """Stream Vishwas agent response"""
    trust_score = user_data.get("trust_score", 50)
    trust_coins = user_data.get("trust_coins", 0)
    badge = user_data.get("trust_badge", "Bronze")
    
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "CHANGE_OPENAI_API_KEY":
        try:
            stream = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are Agent Vishwas (विश्वास), a trust and compliance specialist for the Ooumph SHG marketplace.

You provide:
- Trust score information
- Audit and compliance guidance
- Trust coin balance updates

Current user status:
- Trust Score: {trust_score}/100
- Badge: {badge}
- Trust Coins: {trust_coins}

Guidelines:
- Respond in {language}
- Be informative about trust system
- Explain how to improve trust score
- Keep responses under 100 words"""
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
    
    fallback = f"Trust & Compliance Status:\n\n"
    fallback += f"📊 Trust Score: {trust_score}/100\n"
    fallback += f"🏅 Badge: {badge}\n"
    fallback += f"💰 Trust Coins: {trust_coins}\n\n"
    
    if trust_score >= 90:
        fallback += "Excellent! You're a Gold badge member!"
    elif trust_score >= 70:
        fallback += "Great progress! Maintain performance for Gold."
    else:
        fallback += "Complete more orders on time to improve!"
    
    fallback += "\n\nYour trust score affects buyer matching and premium access."
    
    for word in fallback.split():
        yield word + " ", False
        import asyncio
        await asyncio.sleep(0.02)
    yield "", True


async def _stream_sampark_response(
    query: str,
    user_data: dict,
    language: str
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
                        "content": f"""You are Agent Sampark (संपर्क), a community orchestration specialist for the Ooumph SHG marketplace.

You provide:
- Federation hierarchy information
- Community alerts
- District overview

User context:
- Hierarchy Level: {hierarchy_level}
- District: {district}

Guidelines:
- Respond in {language}
- Explain federation structure clearly
- Provide contact guidance
- Keep responses under 100 words"""
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
    
    fallback = f"Community Information:\n\n"
    
    if hierarchy_level == "SHG":
        fallback += f"Your SHG is part of the {district} district network.\n\n"
        fallback += f"Federation structure:\n"
        fallback += f"• SHG (Your Group)\n"
        fallback += f"• SLF (Slum Level Federation)\n"
        fallback += f"• TLF (Town Level Federation)\n\n"
        fallback += f"Contact your SLF coordinator for district support."
    else:
        fallback += f"As a {hierarchy_level}, you can manage federation members.\n\n"
        fallback += f"Use the Admin Portal to:\n"
        fallback += f"• View federation statistics\n"
        fallback += f"• Send community alerts\n"
        fallback += f"• Track member performance"
    
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
