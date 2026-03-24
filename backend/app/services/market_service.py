"""
Agent Bazaar Buddhi (बाज़ार बुद्धि) - Market Intelligence Service
Analyzes market demand, pricing, and trends for SHG products
"""
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from openai import OpenAI
from sqlalchemy.orm import Session
from .. import models

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy"))

# Districts of Andhra Pradesh
AP_DISTRICTS = [
    "Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna",
    "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam",
    "Vizianagaram", "West Godavari", "Kadapa", "Kakinada", "Tirupati",
    "Nandyal", "Eluru", "Amaravati", "Guntakal", "Rajahmundry",
    "Kothagudem", "Nalgonda", "Khammam", "Mahbubnagar", "Hyderabad"
]

# Product categories with seasonal patterns
PRODUCT_CATEGORIES = {
    "Handicrafts": {
        "peak_season": ["October", "November", "December", "January"],
        "trend": "Rising",
        "base_demand": 70
    },
    "Food Products": {
        "peak_season": ["November", "December", "April", "May"],
        "trend": "Stable",
        "base_demand": 80
    },
    "Textiles": {
        "peak_season": ["September", "October", "March", "April"],
        "trend": "Stable",
        "base_demand": 75
    },
    "Handmade Baskets": {
        "peak_season": ["October", "November", "December"],
        "trend": "Rising",
        "base_demand": 85
    },
    "Pickles": {
        "peak_season": ["March", "April", "May"],
        "trend": "Rising",
        "base_demand": 90
    },
    "Spices": {
        "peak_season": ["October", "November", "December"],
        "trend": "Stable",
        "base_demand": 85
    }
}

# Mock market data storage
_market_data_cache = {}

async def analyze_market(product_name: str, category: str, district: str,
                       price: Optional[float] = None, db: Session = None) -> Dict:
    """
    Analyze market conditions for a product

    Args:
        product_name: Name of the product
        category: Product category
        district: District for analysis
        price: Optional seller's price
        db: Database session

    Returns:
        Market analysis with demand, pricing, and suggestions
    """
    current_month = datetime.now().strftime("%B")

    # Get category info
    category_info = PRODUCT_CATEGORIES.get(category, {
        "peak_season": ["October", "November", "December"],
        "trend": "Stable",
        "base_demand": 60
    })

    # Calculate demand based on seasonality and random factors
    is_peak_season = current_month in category_info["peak_season"]
    seasonal_boost = 20 if is_peak_season else 0

    # Add some randomness for variety
    random_factor = random.randint(-10, 10)
    demand_score = min(100, max(0, category_info["base_demand"] + seasonal_boost + random_factor))

    # Determine demand level
    if demand_score >= 75:
        demand_level = "High"
    elif demand_score >= 50:
        demand_level = "Medium"
    else:
        demand_level = "Low"

    # Calculate market prices
    if price:
        price_variance = price * 0.2  # 20% variance
        avg_market_price = price + random.uniform(-price_variance, price_variance)
        recommended_min = avg_market_price * 0.9
        recommended_max = avg_market_price * 1.15
    else:
        # Generate mock price range
        base_price = random.randint(100, 2000)
        recommended_min = base_price * 0.9
        recommended_max = base_price * 1.3
        avg_market_price = (recommended_min + recommended_max) / 2

    # Calculate competition
    competitor_count = random.randint(5, 50)
    if competitor_count < 15:
        saturation = "Low"
    elif competitor_count < 35:
        saturation = "Medium"
    else:
        saturation = "High"

    # Find best selling districts (excluding current)
    best_districts = random.sample([d for d in AP_DISTRICTS if d != district], min(5, len(AP_DISTRICTS) - 1))

    # Generate suggestions using OpenAI if available
    suggestions = await generate_market_suggestions(
        product_name, category, district, demand_level, is_peak_season
    )

    return {
        "product_name": product_name,
        "category": category,
        "district": district,
        "demand_level": demand_level,
        "demand_score": demand_score,
        "demand_trend": category_info["trend"],
        "recommended_price_min": round(recommended_min, 2),
        "recommended_price_max": round(recommended_max, 2),
        "average_market_price": round(avg_market_price, 2),
        "competitor_count": competitor_count,
        "market_saturation": saturation,
        "is_seasonal": True,
        "peak_season": f"{category_info['peak_season'][0]} to {category_info['peak_season'][-1]}",
        "current_season": current_month,
        "is_peak_season": is_peak_season,
        "best_selling_districts": best_districts,
        "suggestions": suggestions
    }

async def get_price_suggestion(product_name: str, category: str, quality: str,
                              district: str, cost_price: float) -> Dict:
    """
    Get pricing recommendations based on cost and market conditions

    Args:
        product_name: Product name
        category: Product category
        quality: Quality grade (Premium, Standard, Economy)
        district: District
        cost_price: Cost price

    Returns:
        Price suggestion with margins and reasoning
    """
    # Quality multipliers
    quality_multipliers = {
        "Premium": 1.5,
        "Standard": 1.3,
        "Economy": 1.15
    }

    multiplier = quality_multipliers.get(quality, 1.3)

    # Calculate prices
    recommended_min = round(cost_price * multiplier * 0.95, 2)
    recommended_max = round(cost_price * multiplier * 1.1, 2)
    recommended = round((recommended_min + recommended_max) / 2, 2)

    # Calculate margins
    margin_min = round(((recommended_min - cost_price) / cost_price) * 100, 1)
    margin_max = round(((recommended_max - cost_price) / cost_price) * 100, 1)

    # Generate reasoning
    reasoning = f"For {quality} quality {category} in {district}, based on current market conditions and your cost price."

    # Market factors
    market_factors = [
        f"Quality {quality} commands {multiplier}x markup",
        f"Current season demand in {district}",
        "Market competition level",
        "Trust score advantage (if applicable)"
    ]

    return {
        "product_name": product_name,
        "cost_price": cost_price,
        "quality": quality,
        "recommended_price_min": recommended_min,
        "recommended_price_max": recommended_max,
        "recommended_price": recommended,
        "profit_margin_min": margin_min,
        "profit_margin_max": margin_max,
        "reasoning": reasoning,
        "market_factors": market_factors
    }

async def generate_market_suggestions(product_name: str, category: str,
                                     district: str, demand_level: str,
                                     is_peak_season: bool) -> List[str]:
    """
    Generate market suggestions using AI

    Args:
        product_name: Product name
        category: Category
        district: District
        demand_level: Current demand level
        is_peak_season: Whether it's peak season

    Returns:
        List of suggestions
    """
    try:
        if not os.environ.get("OPENAI_API_KEY"):
            # Return fallback suggestions
            return [
                f"{'Increase production' if demand_level == 'High' else 'Maintain current production'} for {category}",
                f"Consider selling in neighboring districts for better prices",
                f"{'Now is the best time to sell' if is_peak_season else 'Plan for peak season'}",
                "Maintain product quality for better trust scores"
            ]

        prompt = f"""
        As Agent Bazaar Buddhi, provide 3-4 specific market suggestions for:
        - Product: {product_name} ({category})
        - District: {district}
        - Demand: {demand_level}
        - Season: {'Peak' if is_peak_season else 'Off-peak'}

        Keep suggestions practical for SHG women. Be concise.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are Agent Bazaar Buddhi, a market intelligence expert. Provide brief, practical suggestions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=300
        )

        text = response.choices[0].message.content.strip()
        # Parse into list
        suggestions = [s.strip().lstrip('•-*').strip() for s in text.split('\n') if s.strip()]
        return suggestions[:4]

    except Exception:
        return [
            "Focus on quality to improve trust score",
            "List on multiple platforms for better visibility",
            "Consider bulk orders for better margins"
        ]

async def get_market_trends(category: Optional[str] = None,
                           district: Optional[str] = None) -> Dict:
    """
    Get overall market trends

    Args:
        category: Filter by category
        district: Filter by district

    Returns:
        Market trends summary
    """
    current_month = datetime.now().strftime("%B")

    categories_to_analyze = [category] if category else list(PRODUCT_CATEGORIES.keys())
    districts_to_analyze = [district] if district else AP_DISTRICTS[:5]

    trends = []
    for cat in categories_to_analyze:
        cat_info = PRODUCT_CATEGORIES.get(cat, {})
        is_peak = current_month in cat_info.get("peak_season", [])
        trends.append({
            "category": cat,
            "trend": cat_info.get("trend", "Stable"),
            "is_peak_season": is_peak,
            "demand_outlook": "High" if is_peak else "Moderate"
        })

    return {
        "current_month": current_month,
        "trends": trends,
        "top_performing_districts": random.sample(AP_DISTRICTS, 5),
        "emerging_categories": ["Handmade Baskets", "Organic Products", "Traditional Crafts"]
    }

def save_market_data(db: Session, category: str, district: str, data: Dict):
    """Save market data to database"""
    try:
        market_data = models.MarketData(
            category=category,
            district=district,
            demand_level=data.get("demand_level"),
            demand_score=data.get("demand_score"),
            demand_trend=data.get("demand_trend"),
            average_price=data.get("average_market_price"),
            recommended_price_min=data.get("recommended_price_min"),
            recommended_price_max=data.get("recommended_price_max")
        )
        db.add(market_data)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error saving market data: {e}")
