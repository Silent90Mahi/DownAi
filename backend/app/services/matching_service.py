"""
Agent Jodi (जोड़ी) - Buyer Matching Service
Matches SHG products with potential buyers and government procurement
"""
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from .. import models

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy"))

# Mock buyer database
MOCK_BUYERS = [
    {
        "id": 1,
        "business_name": "Andhra Pradesh Handicrafts Corporation",
        "buyer_type": "Government",
        "district": "Hyderabad",
        "rating": 4.8,
        "trust_score": 85.0,
        "gem_registered": True,
        "ondc_registered": True,
        "preferred_categories": ["Handicrafts", "Textiles"],
        "buying_capacity": "Large"
    },
    {
        "id": 2,
        "business_name": "Rajahmundry Wholesale Traders",
        "buyer_type": "Wholesaler",
        "district": "Rajahmundry",
        "rating": 4.2,
        "trust_score": 72.0,
        "gem_registered": False,
        "ondc_registered": True,
        "preferred_categories": ["Food Products", "Pickles", "Spices"],
        "buying_capacity": "Medium"
    },
    {
        "id": 3,
        "business_name": "Visakhapatnam Export House",
        "buyer_type": "Institutional",
        "district": "Visakhapatnam",
        "rating": 4.5,
        "trust_score": 78.0,
        "gem_registered": True,
        "ondc_registered": True,
        "preferred_categories": ["Handicrafts", "Handmade Baskets"],
        "buying_capacity": "Large"
    },
    {
        "id": 4,
        "business_name": "Tirupati Temple Prasadam Supplier",
        "buyer_type": "Institutional",
        "district": "Tirupati",
        "rating": 4.7,
        "trust_score": 82.0,
        "gem_registered": True,
        "ondc_registered": False,
        "preferred_categories": ["Food Products", "Pickles", "Spices"],
        "buying_capacity": "Large"
    },
    {
        "id": 5,
        "business_name": "Vijayawada Retail Chain",
        "buyer_type": "Retailer",
        "district": "Vijayawada",
        "rating": 3.9,
        "trust_score": 65.0,
        "gem_registered": False,
        "ondc_registered": True,
        "preferred_categories": ["Food Products", "Textiles"],
        "buying_capacity": "Medium"
    }
]

# Government procurement opportunities
MOCK_GEM_TENDERS = [
    {
        "id": "GEM/2024/001",
        "title": "Supply of Handicraft Items for State Function",
        "organization": "Andhra Pradesh Tourism",
        "category": "Handicrafts",
        "quantity": 500,
        "unit": "pieces",
        "budget_range": [500, 800],
        "required_by": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "district": "Amaravati"
    },
    {
        "id": "GEM/2024/002",
        "title": "Procurement of Pickles for Mid-Day Meal Scheme",
        "organization": "Education Department",
        "category": "Food Products",
        "quantity": 1000,
        "unit": "kg",
        "budget_range": [300, 450],
        "required_by": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
        "district": "Hyderabad"
    },
    {
        "id": "GEM/2024/003",
        "title": "Supply of Traditional Textiles for Government Staff",
        "organization": "MA&UD Department",
        "category": "Textiles",
        "quantity": 200,
        "unit": "pieces",
        "budget_range": [800, 1200],
        "required_by": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
        "district": "Hyderabad"
    }
]

async def find_buyers_for_product(product_id: int, quantity: int, price: float,
                                district: str, category: str,
                                seller_trust_score: float,
                                db: Session) -> List[Dict]:
    """
    Find matching buyers for a product

    Args:
        product_id: Product ID
        quantity: Quantity available
        price: Seller's price
        district: Product location
        category: Product category
        seller_trust_score: Seller's trust score
        db: Database session

    Returns:
        List of matched buyers with match scores
    """
    matches = []

    # Check against mock buyers
    for buyer in MOCK_BUYERS:
        # Category match
        category_match = category in buyer["preferred_categories"]

        # Calculate proximity score (same district = higher score)
        proximity_score = 100 if buyer["district"] == district else 70

        # Trust compatibility
        trust_diff = abs(buyer["trust_score"] - seller_trust_score)
        trust_compatibility = max(0, 100 - trust_diff)

        # Calculate overall match score
        match_score = 0
        if category_match:
            match_score += 40
        match_score += (proximity_score * 0.3)
        match_score += (trust_compatibility * 0.3)

        # Add buyer rating bonus
        match_score += (buyer["rating"] * 5)

        match_score = min(100, match_score)

        if match_score >= 50:  # Minimum threshold
            # Calculate offer price
            price_adjustment = 1.0 + (random.uniform(-0.1, 0.15))
            offer_price = round(price * price_adjustment, 2)

            matches.append({
                "buyer_id": buyer["id"],
                "business_name": buyer["business_name"],
                "buyer_type": buyer["buyer_type"],
                "district": buyer["district"],
                "rating": buyer["rating"],
                "trust_score": buyer["trust_score"],
                "offer_price": offer_price,
                "quantity_requested": min(quantity, random.randint(quantity // 2, quantity * 2)),
                "requirements": f"Looking for {category.lower()} from verified SHGs",
                "gem_registered": buyer["gem_registered"],
                "ondc_registered": buyer["ondc_registered"],
                "match_score": round(match_score, 1),
                "contact_allowed": seller_trust_score >= 60
            })

    # Sort by match score
    matches.sort(key=lambda x: x["match_score"], reverse=True)

    return matches[:5]  # Return top 5 matches

async def get_buyer_requirements(category: Optional[str] = None,
                               district: Optional[str] = None,
                               db: Session = None) -> List[Dict]:
    """
    Get active buyer requirements

    Args:
        category: Filter by category
        district: Filter by district
        db: Database session

    Returns:
        List of buyer requirements
    """
    requirements = []

    # Add mock GeM tenders
    for tender in MOCK_GEM_TENDERS:
        if category and tender["category"] != category:
            continue
        if district and tender["district"] != district:
            continue

        requirements.append({
            "id": tender["id"],
            "title": tender["title"],
            "organization": tender["organization"],
            "description": f"Government tender for {tender['category'].lower()}",
            "category": tender["category"],
            "quantity": tender["quantity"],
            "unit": tender["unit"],
            "budget_range_min": tender["budget_range"][0],
            "budget_range_max": tender["budget_range"][1],
            "required_by": tender["required_by"],
            "district": tender["district"],
            "status": "Open",
            "is_gem": True,
            "posted_date": (datetime.now() - timedelta(days=random.randint(1, 15))).strftime("%Y-%m-%d")
        })

    return requirements

async def create_buyer_requirement(buyer_id: int, title: str, description: str,
                                  category: str, quantity: int, unit: str,
                                  budget_min: Optional[float], budget_max: Optional[float],
                                  required_by: datetime, district: str,
                                  db: Session) -> Dict:
    """
    Create a new buyer requirement

    Args:
        buyer_id: Buyer user ID
        title: Requirement title
        description: Description
        category: Product category
        quantity: Quantity needed
        unit: Unit of measurement
        budget_min: Minimum budget
        budget_max: Maximum budget
        required_by: Required by date
        district: District
        db: Database session

    Returns:
        Created requirement
    """
    # Get buyer profile
    buyer = db.query(models.Buyer).filter(models.Buyer.user_id == buyer_id).first()
    if not buyer:
        # Create buyer profile
        buyer = models.Buyer(
            user_id=buyer_id,
            business_name=f"Buyer {buyer_id}",
            buyer_type="Institutional"
        )
        db.add(buyer)
        db.commit()
        db.refresh(buyer)

    # Create requirement
    requirement = models.BuyerRequirement(
        buyer_id=buyer.id,
        title=title,
        description=description,
        category=category,
        quantity=quantity,
        unit=unit,
        budget_range_min=budget_min,
        budget_range_max=budget_max,
        required_by=required_by,
        status="Open"
    )

    db.add(requirement)
    db.commit()
    db.refresh(requirement)

    return {
        "id": requirement.id,
        "title": requirement.title,
        "status": requirement.status,
        "created_at": requirement.created_at
    }

async def simulate_negotiation(buyer_id: int, seller_id: int, product_id: int,
                             initial_price: float, quantity: int,
                             db: Session) -> Dict:
    """
    Simulate price negotiation between buyer and seller

    Args:
        buyer_id: Buyer ID
        seller_id: Seller ID
        product_id: Product ID
        initial_price: Initial asking price
        quantity: Quantity
        db: Database session

    Returns:
        Negotiation result with counter-offer
    """
    # Get trust scores
    seller = db.query(models.User).filter(models.User.id == seller_id).first()
    buyer = db.query(models.Buyer).filter(models.Buyer.user_id == buyer_id).first()

    seller_trust = seller.trust_score if seller else 50.0
    buyer_trust = buyer.trust_score if buyer else 50.0

    # Simulate negotiation rounds
    rounds = []

    # Round 1: Buyer counter-offer
    buyer_discount = random.uniform(0.05, 0.15)
    buyer_offer = round(initial_price * (1 - buyer_discount), 2)
    rounds.append({
        "round": 1,
        "party": "Buyer",
        "offer": buyer_offer,
        "message": f"We can offer ₹{buyer_offer} per unit for this quantity."
    })

    # Round 2: Seller counter-offer (if trust is high)
    if seller_trust >= 70:
        seller_discount = buyer_discount * 0.5
        seller_offer = round(initial_price * (1 - seller_discount), 2)
        rounds.append({
            "round": 2,
            "party": "Seller",
            "offer": seller_offer,
            "message": f"Considering your order size, we can offer ₹{seller_offer}."
        })
    else:
        seller_offer = buyer_offer

    # Final agreement
    final_price = seller_offer if seller_trust >= 60 else buyer_offer

    return {
        "initial_price": initial_price,
        "final_price": final_price,
        "discount_percent": round(((initial_price - final_price) / initial_price) * 100, 1),
        "negotiation_rounds": rounds,
        "total_value": round(final_price * quantity, 2),
        "status": "Agreed" if seller_trust >= 60 else "Pending"
    }

async def get_gem_opportunities(category: Optional[str] = None,
                               district: Optional[str] = None) -> List[Dict]:
    """
    Get GeM (Government e-Marketplace) opportunities

    Args:
        category: Filter by category
        district: Filter by district

    Returns:
        List of GeM opportunities
    """
    opportunities = []

    for tender in MOCK_GEM_TENDERS:
        if category and tender["category"] != category:
            continue

        opportunities.append({
            **tender,
            "portal": "GeM",
            "eligibility": "Open to all SHGs with trust score >= 60",
            "documents_required": ["SHG Registration Certificate", "Bank Account", "GST Certificate"],
            "application_link": f"https://gem.gov.in/tender/{tender['id']}"
        })

    return opportunities

async def get_ondc_catalog_sync(category: Optional[str] = None) -> Dict:
    """
    Get ONDC catalog sync status (stub)

    Args:
        category: Category filter

    Returns:
        ONDC sync status
    """
    return {
        "status": "Active",
        "last_sync": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
        "products_listed": random.randint(50, 200),
        "total_orders": random.randint(10, 50),
        "categories": ["Handicrafts", "Food Products", "Textiles", "Pickles"]
    }
