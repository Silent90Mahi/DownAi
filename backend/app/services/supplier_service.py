"""
Agent Samagri (सामग्री) - Raw Material Procurement Service
Helps SHGs find and purchase raw materials from suppliers
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

# Mock suppliers database
MOCK_SUPPLIERS = [
    {
        "id": 1,
        "business_name": "Guntur Agro Traders",
        "district": "Guntur",
        "rating": 4.5,
        "trust_score": 78.0,
        "is_verified": True,
        "categories": ["Agriculture", "Food Processing"],
        "service_areas": ["Guntur", "Krishna", "Prakasam"]
    },
    {
        "id": 2,
        "business_name": "Cooperative Mills Ltd",
        "district": "Rajahmundry",
        "rating": 4.3,
        "trust_score": 75.0,
        "is_verified": True,
        "categories": ["Textile", "Agriculture"],
        "service_areas": ["East Godavari", "West Godavari", "Krishna"]
    },
    {
        "id": 3,
        "business_name": "Hyderabad Raw Material Depot",
        "district": "Hyderabad",
        "rating": 4.1,
        "trust_score": 70.0,
        "is_verified": False,
        "categories": ["Handicrafts", "Textile", "Food Processing"],
        "service_areas": ["Hyderabad", "Medak", "Rangareddy"]
    },
    {
        "id": 4,
        "business_name": "Kurnool Farmers Cooperative",
        "district": "Kurnool",
        "rating": 4.6,
        "trust_score": 82.0,
        "is_verified": True,
        "categories": ["Agriculture", "Food Processing"],
        "service_areas": ["Kurnool", "Anantapur", "Kadapa"]
    },
    {
        "id": 5,
        "business_name": "Visakhapatnam Marine Products",
        "district": "Visakhapatnam",
        "rating": 4.4,
        "trust_score": 76.0,
        "is_verified": True,
        "categories": ["Food Processing"],
        "service_areas": ["Visakhapatnam", "Vizianagaram", "Srikakulam"]
    }
]

# Mock materials catalog
MOCK_MATERIALS = [
    {
        "id": 1,
        "supplier_id": 1,
        "name": "Premium Cotton Yarn",
        "category": "Textile",
        "subcategory": "Raw Material",
        "price_per_unit": 450.0,
        "unit": "kg",
        "min_order_quantity": 10,
        "bulk_discount_available": True,
        "bulk_discount_percentage": 15.0,
        "stock_available": 500,
        "is_available": True,
        "quality_grade": "Premium",
        "is_organic": True,
        "certifications": ["Organic India", "Textile Ministry"],
        "district": "Guntur",
        "supplier_rating": 4.5
    },
    {
        "id": 2,
        "supplier_id": 1,
        "name": "Food Grade Preservatives",
        "category": "Food Processing",
        "subcategory": "Ingredients",
        "price_per_unit": 850.0,
        "unit": "kg",
        "min_order_quantity": 5,
        "bulk_discount_available": True,
        "bulk_discount_percentage": 10.0,
        "stock_available": 200,
        "is_available": True,
        "quality_grade": "Standard",
        "is_organic": False,
        "certifications": ["FSSAI"],
        "district": "Guntur",
        "supplier_rating": 4.5
    },
    {
        "id": 3,
        "supplier_id": 2,
        "name": "Bamboo Raw Material",
        "category": "Handicrafts",
        "subcategory": "Raw Material",
        "price_per_unit": 150.0,
        "unit": "bundle",
        "min_order_quantity": 20,
        "bulk_discount_available": True,
        "bulk_discount_percentage": 20.0,
        "stock_available": 1000,
        "is_available": True,
        "quality_grade": "Standard",
        "is_organic": True,
        "certifications": [],
        "district": "Rajahmundry",
        "supplier_rating": 4.3
    },
    {
        "id": 4,
        "supplier_id": 4,
        "name": "Organic Spices Mix",
        "category": "Food Processing",
        "subcategory": "Ingredients",
        "price_per_unit": 600.0,
        "unit": "kg",
        "min_order_quantity": 10,
        "bulk_discount_available": True,
        "bulk_discount_percentage": 12.0,
        "stock_available": 300,
        "is_available": True,
        "quality_grade": "Premium",
        "is_organic": True,
        "certifications": ["Organic India", "FSSAI"],
        "district": "Kurnool",
        "supplier_rating": 4.6
    },
    {
        "id": 5,
        "supplier_id": 3,
        "name": "Packaging Materials",
        "category": "Food Processing",
        "subcategory": "Packaging",
        "price_per_unit": 50.0,
        "unit": "piece",
        "min_order_quantity": 100,
        "bulk_discount_available": True,
        "bulk_discount_percentage": 8.0,
        "stock_available": 5000,
        "is_available": True,
        "quality_grade": "Standard",
        "is_organic": False,
        "certifications": ["FSSAI"],
        "district": "Hyderabad",
        "supplier_rating": 4.1
    }
]

async def search_materials(query: str, category: Optional[str] = None,
                          district: Optional[str] = None,
                          min_price: Optional[float] = None,
                          max_price: Optional[float] = None,
                          is_organic: Optional[bool] = None,
                          db: Session = None) -> List[Dict]:
    """
    Search for raw materials from suppliers

    Args:
        query: Search query
        category: Filter by category
        district: Filter by district
        min_price: Minimum price
        max_price: Maximum price
        is_organic: Filter for organic only
        db: Database session

    Returns:
        List of matching materials with supplier info
    """
    results = []

    for material in MOCK_MATERIALS:
        # Text search
        if query and query.lower() not in material["name"].lower():
            continue

        # Category filter
        if category and material["category"] != category:
            continue

        # District filter
        if district and material["district"] != district:
            # Check if supplier serves this district
            supplier = next((s for s in MOCK_SUPPLIERS if s["id"] == material["supplier_id"]), None)
            if supplier and district not in supplier["service_areas"]:
                continue

        # Price filter
        price = material["price_per_unit"]
        if min_price and price < min_price:
            continue
        if max_price and price > max_price:
            continue

        # Organic filter
        if is_organic and not material["is_organic"]:
            continue

        # Get supplier info
        supplier = next((s for s in MOCK_SUPPLIERS if s["id"] == material["supplier_id"]), None)

        # Calculate distance score
        distance_score = 100 if not district or material["district"] == district else 70

        results.append({
            "id": material["id"],
            "name": material["name"],
            "description": f"High quality {material['name'].lower()} for {material['category'].lower()}",
            "category": material["category"],
            "subcategory": material["subcategory"],
            "price_per_unit": material["price_per_unit"],
            "unit": material["unit"],
            "min_order_quantity": material["min_order_quantity"],
            "bulk_discount_available": material["bulk_discount_available"],
            "bulk_discount_percentage": material["bulk_discount_percentage"],
            "stock_available": material["stock_available"],
            "is_available": material["is_available"],
            "quality_grade": material["quality_grade"],
            "is_organic": material["is_organic"],
            "certifications": material["certifications"],
            "district": material["district"],
            "images": [],
            "supplier": {
                "id": supplier["id"] if supplier else material["supplier_id"],
                "business_name": supplier["business_name"] if supplier else "Unknown",
                "district": material["district"],
                "rating": material["supplier_rating"],
                "trust_score": supplier["trust_score"] if supplier else 70.0,
                "total_reviews": random.randint(20, 100),
                "is_verified": supplier["is_verified"] if supplier else False,
                "categories_supplied": supplier["categories"] if supplier else [],
                "service_areas": supplier["service_areas"] if supplier else []
            },
            "match_score": distance_score
        })

    # Sort by match score
    results.sort(key=lambda x: x["match_score"], reverse=True)

    return results

async def get_supplier_by_id(supplier_id: int, db: Session) -> Optional[Dict]:
    """
    Get supplier details

    Args:
        supplier_id: Supplier ID
        db: Database session

    Returns:
        Supplier details
    """
    supplier = next((s for s in MOCK_SUPPLIERS if s["id"] == supplier_id), None)
    if not supplier:
        return None

    # Get materials from this supplier
    materials = [m for m in MOCK_MATERIALS if m["supplier_id"] == supplier_id]

    return {
        "id": supplier["id"],
        "business_name": supplier["business_name"],
        "district": supplier["district"],
        "rating": supplier["rating"],
        "trust_score": supplier["trust_score"],
        "total_reviews": random.randint(20, 150),
        "is_verified": supplier["is_verified"],
        "categories_supplied": supplier["categories"],
        "service_areas": supplier["service_areas"],
        "total_materials": len(materials)
    }

async def create_bulk_request(creator_id: int, title: str, description: str,
                            materials: List[Dict], target_quantity: int,
                            district: str, serving_districts: List[str],
                            expires_in_days: int = 30,
                            db: Session = None) -> Dict:
    """
    Create a bulk purchase request for group buying

    Args:
        creator_id: User ID of creator
        title: Request title
        description: Description
        materials: List of materials with quantities
        target_quantity: Target total quantity
        district: Primary district
        serving_districts: Districts being served
        expires_in_days: Days until expiration
        db: Database session

    Returns:
        Created bulk request
    """
    request_number = f"BULK{datetime.now().strftime('%Y%m%d%H%M%S')}"
    expires_at = datetime.now() + timedelta(days=expires_in_days)

    bulk_request = models.BulkRequest(
        request_number=request_number,
        creator_id=creator_id,
        title=title,
        description=description,
        target_quantity=target_quantity,
        district=district,
        serving_districts=serving_districts,
        expected_savings_percentage=random.uniform(15, 25),
        expires_at=expires_at
    )

    db.add(bulk_request)
    db.commit()
    db.refresh(bulk_request)

    # Add items
    for material in materials:
        item = models.BulkRequestItem(
            bulk_request_id=bulk_request.id,
            material_id=material.get("material_id"),
            material_name=material.get("material_name"),
            quantity=material.get("quantity"),
            target_price=material.get("target_price")
        )
        db.add(item)

    db.commit()

    return {
        "id": bulk_request.id,
        "request_number": request_number,
        "title": title,
        "status": "Open",
        "target_quantity": target_quantity,
        "current_quantity": 0,
        "current_participants": 1,
        "minimum_participants": 2,
        "expected_savings": round(bulk_request.expected_savings_percentage, 1),
        "expires_at": expires_at.strftime("%Y-%m-%d")
    }

async def join_bulk_request(bulk_request_id: int, user_id: int,
                          quantity: int, db: Session) -> Dict:
    """
    Join an existing bulk request

    Args:
        bulk_request_id: Bulk request ID
        user_id: User ID
        quantity: Quantity to commit
        db: Database session

    Returns:
        Updated bulk request info
    """
    bulk_request = db.query(models.BulkRequest).filter(
        models.BulkRequest.id == bulk_request_id
    ).first()

    if not bulk_request:
        raise ValueError("Bulk request not found")

    # Check if already joined
    existing = db.query(models.BulkRequestParticipant).filter(
        and_(
            models.BulkRequestParticipant.bulk_request_id == bulk_request_id,
            models.BulkRequestParticipant.user_id == user_id
        )
    ).first()

    if existing:
        # Update existing
        existing.quantity = quantity
        existing.status = "Committed"
    else:
        # Add new participant
        participant = models.BulkRequestParticipant(
            bulk_request_id=bulk_request_id,
            user_id=user_id,
            quantity=quantity
        )
        db.add(participant)

    # Update bulk request totals
    bulk_request.current_participants = db.query(models.BulkRequestParticipant).filter(
        models.BulkRequestParticipant.bulk_request_id == bulk_request_id,
        models.BulkRequestParticipant.status == "Committed"
    ).count()

    bulk_request.current_quantity = db.query(
        models.BulkRequestParticipant
    ).filter(
        models.BulkRequestParticipant.bulk_request_id == bulk_request_id,
        models.BulkRequestParticipant.status == "Committed"
    ).with_entities(
        models.BulkRequestParticipant.quantity
    ).all()

    bulk_request.current_quantity = sum([q[0] for q in bulk_request.current_quantity])

    db.commit()

    return {
        "request_number": bulk_request.request_number,
        "current_quantity": bulk_request.current_quantity,
        "target_quantity": bulk_request.target_quantity,
        "current_participants": bulk_request.current_participants,
        "status": bulk_request.status,
        "completion_percentage": round(
            (bulk_request.current_quantity / bulk_request.target_quantity) * 100, 1
        )
    }

async def get_price_trends(material_name: str, district: str,
                          months: int = 6) -> Dict:
    """
    Get price trends for a material

    Args:
        material_name: Material name
        district: District
        months: Number of months of history

    Returns:
        Price trend data
    """
    # Generate mock trend data
    trend_data = []
    base_price = random.uniform(200, 1000)

    for i in range(months):
        month_date = datetime.now() - timedelta(days=30 * (months - i))
        variation = random.uniform(-0.1, 0.15)
        price = base_price * (1 + variation)

        trend_data.append({
            "month": month_date.strftime("%b %Y"),
            "price": round(price, 2),
            "trend": "up" if variation > 0 else "down"
        })
        base_price = price

    # Calculate statistics
    prices = [d["price"] for d in trend_data]
    avg_price = sum(prices) / len(prices)
    min_price = min(prices)
    max_price = max(prices)

    # Predict next month
    last_trend = trend_data[-1]["price"] - trend_data[-2]["price"]
    predicted_price = trend_data[-1]["price"] + last_trend

    return {
        "material_name": material_name,
        "district": district,
        "current_price": trend_data[-1]["price"],
        "average_price": round(avg_price, 2),
        "min_price": round(min_price, 2),
        "max_price": round(max_price, 2),
        "predicted_price": round(predicted_price, 2),
        "trend_direction": "up" if predicted_price > trend_data[-1]["price"] else "down",
        "price_volatility": round(((max_price - min_price) / avg_price) * 100, 1),
        "history": trend_data
    }

async def get_bulk_requests_list(district: Optional[str] = None,
                                 status: str = "Open",
                                 db: Session = None) -> List[Dict]:
    """
    Get list of active bulk requests

    Args:
        district: Filter by district
        status: Filter by status
        db: Database session

    Returns:
        List of bulk requests
    """
    query = db.query(models.BulkRequest).filter(models.BulkRequest.status == status)

    if district:
        query = query.filter(
            or_(
                models.BulkRequest.district == district,
                models.BulkRequest.serving_districts.contains([district])
            )
        )

    requests = query.order_by(models.BulkRequest.created_at.desc()).limit(20).all()

    result = []
    for req in requests:
        completion = (req.current_quantity / req.target_quantity * 100) if req.target_quantity > 0 else 0

        result.append({
            "id": req.id,
            "request_number": req.request_number,
            "title": req.title,
            "district": req.district,
            "target_quantity": req.target_quantity,
            "current_quantity": req.current_quantity,
            "current_participants": req.current_participants,
            "minimum_participants": req.minimum_participants,
            "expected_savings": round(req.expected_savings_percentage, 1),
            "completion_percentage": round(completion, 1),
            "expires_at": req.expires_at.strftime("%Y-%m-%d") if req.expires_at else None,
            "created_at": req.created_at.strftime("%Y-%m-%d")
        })

    return result
