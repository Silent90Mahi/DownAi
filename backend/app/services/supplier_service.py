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
from .. import models, schemas

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy"))

MOCK_SUPPLIERS = [
    {
        "id": 1,
        "business_name": "Guntur Agro Traders",
        "district": "Guntur",
        "state": "Andhra Pradesh",
        "address": "123 Market Road, Guntur",
        "rating": 4.5,
        "trust_score": 78.0,
        "is_verified": True,
        "categories": ["Agriculture", "Food Processing"],
        "service_areas": ["Guntur", "Krishna", "Prakasam"],
        "total_reviews": 47,
        "total_connections": 23
    },
    {
        "id": 2,
        "business_name": "Cooperative Mills Ltd",
        "district": "Rajahmundry",
        "state": "Andhra Pradesh",
        "address": "45 Industrial Area, Rajahmundry",
        "rating": 4.3,
        "trust_score": 75.0,
        "is_verified": True,
        "categories": ["Textile", "Agriculture"],
        "service_areas": ["East Godavari", "West Godavari", "Krishna"],
        "total_reviews": 35,
        "total_connections": 18
    },
    {
        "id": 3,
        "business_name": "Hyderabad Raw Material Depot",
        "district": "Hyderabad",
        "state": "Telangana",
        "address": "78 Supply Chain Hub, Hyderabad",
        "rating": 4.1,
        "trust_score": 70.0,
        "is_verified": False,
        "categories": ["Handicrafts", "Textile", "Food Processing"],
        "service_areas": ["Hyderabad", "Medak", "Rangareddy"],
        "total_reviews": 28,
        "total_connections": 15
    },
    {
        "id": 4,
        "business_name": "Kurnool Farmers Cooperative",
        "district": "Kurnool",
        "state": "Andhra Pradesh",
        "address": "12 Cooperative Society, Kurnool",
        "rating": 4.6,
        "trust_score": 82.0,
        "is_verified": True,
        "categories": ["Agriculture", "Food Processing"],
        "service_areas": ["Kurnool", "Anantapur", "Kadapa"],
        "total_reviews": 56,
        "total_connections": 31
    },
    {
        "id": 5,
        "business_name": "Visakhapatnam Marine Products",
        "district": "Visakhapatnam",
        "state": "Andhra Pradesh",
        "address": "56 Port Area, Visakhapatnam",
        "rating": 4.4,
        "trust_score": 76.0,
        "is_verified": True,
        "categories": ["Food Processing"],
        "service_areas": ["Visakhapatnam", "Vizianagaram", "Srikakulam"],
        "total_reviews": 42,
        "total_connections": 27
    }
]

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

MOCK_REVIEWS = [
    {"id": 1, "supplier_id": 1, "reviewer_name": "Rajesh Kumar", "rating": 5, "title": "Excellent quality materials", "content": "The cotton yarn quality exceeded our expectations. Delivery was on time.", "quality_rating": 5, "delivery_rating": 5, "communication_rating": 4, "value_rating": 5, "is_verified_purchase": True, "helpful_count": 12, "created_at": datetime.now() - timedelta(days=5)},
    {"id": 2, "supplier_id": 1, "reviewer_name": "Lakshmi Devi", "rating": 4, "title": "Good service", "content": "Reliable supplier with consistent quality. Minor delays in last order.", "quality_rating": 5, "delivery_rating": 3, "communication_rating": 4, "value_rating": 4, "is_verified_purchase": True, "helpful_count": 8, "created_at": datetime.now() - timedelta(days=15)},
    {"id": 3, "supplier_id": 2, "reviewer_name": "Suresh Reddy", "rating": 5, "title": "Best bamboo supplier", "content": "High quality bamboo at competitive prices. Will order again.", "quality_rating": 5, "delivery_rating": 5, "communication_rating": 5, "value_rating": 5, "is_verified_purchase": True, "helpful_count": 15, "created_at": datetime.now() - timedelta(days=10)},
    {"id": 4, "supplier_id": 4, "reviewer_name": "Padmavathi SHG", "rating": 5, "title": "Organic spices are authentic", "content": "Certified organic spices with great aroma. Our products sell better now.", "quality_rating": 5, "delivery_rating": 4, "communication_rating": 5, "value_rating": 4, "is_verified_purchase": True, "helpful_count": 20, "created_at": datetime.now() - timedelta(days=7)},
]


async def search_materials(query: str, category: Optional[str] = None,
                          district: Optional[str] = None,
                          min_price: Optional[float] = None,
                          max_price: Optional[float] = None,
                          is_organic: Optional[bool] = None,
                          db: Session = None) -> List[Dict]:
    results = []

    for material in MOCK_MATERIALS:
        if query and query.lower() not in material["name"].lower():
            continue
        if category and material["category"] != category:
            continue
        if district and material["district"] != district:
            supplier = next((s for s in MOCK_SUPPLIERS if s["id"] == material["supplier_id"]), None)
            if supplier and district not in supplier["service_areas"]:
                continue
        price = material["price_per_unit"]
        if min_price and price < min_price:
            continue
        if max_price and price > max_price:
            continue
        if is_organic and not material["is_organic"]:
            continue

        supplier = next((s for s in MOCK_SUPPLIERS if s["id"] == material["supplier_id"]), None)
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
                "total_reviews": supplier["total_reviews"] if supplier else 0,
                "is_verified": supplier["is_verified"] if supplier else False,
                "categories_supplied": supplier["categories"] if supplier else [],
                "service_areas": supplier["service_areas"] if supplier else []
            },
            "match_score": distance_score
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results


async def get_supplier_by_id(supplier_id: int, db: Session) -> Optional[Dict]:
    supplier = next((s for s in MOCK_SUPPLIERS if s["id"] == supplier_id), None)
    if not supplier:
        return None
    materials = [m for m in MOCK_MATERIALS if m["supplier_id"] == supplier_id]
    return {
        "id": supplier["id"],
        "business_name": supplier["business_name"],
        "district": supplier["district"],
        "rating": supplier["rating"],
        "trust_score": supplier["trust_score"],
        "total_reviews": supplier["total_reviews"],
        "is_verified": supplier["is_verified"],
        "categories_supplied": supplier["categories"],
        "service_areas": supplier["service_areas"],
        "total_materials": len(materials)
    }


async def get_supplier_profile(supplier_id: int, user_id: int, db: Session) -> Optional[Dict]:
    supplier = next((s for s in MOCK_SUPPLIERS if s["id"] == supplier_id), None)
    if not supplier:
        return None
    
    materials = [m for m in MOCK_MATERIALS if m["supplier_id"] == supplier_id]
    reviews = [r for r in MOCK_REVIEWS if r["supplier_id"] == supplier_id]
    
    return {
        "id": supplier["id"],
        "business_name": supplier["business_name"],
        "district": supplier["district"],
        "state": supplier["state"],
        "address": supplier["address"],
        "rating": supplier["rating"],
        "total_reviews": supplier["total_reviews"],
        "trust_score": supplier["trust_score"],
        "is_verified": supplier["is_verified"],
        "categories_supplied": supplier["categories"],
        "service_areas": supplier["service_areas"],
        "total_materials": len(materials),
        "total_connections": supplier["total_connections"],
        "recent_reviews": [
            schemas.SupplierReviewResponse(
                id=r["id"],
                supplier_id=r["supplier_id"],
                reviewer_id=random.randint(1, 100),
                reviewer_name=r["reviewer_name"],
                rating=r["rating"],
                title=r["title"],
                content=r["content"],
                quality_rating=r["quality_rating"],
                delivery_rating=r["delivery_rating"],
                communication_rating=r["communication_rating"],
                value_rating=r["value_rating"],
                is_verified_purchase=r["is_verified_purchase"],
                helpful_count=r["helpful_count"],
                created_at=r["created_at"]
            )
            for r in reviews[:5]
        ],
        "materials": [
            {
                "id": m["id"],
                "name": m["name"],
                "category": m["category"],
                "price_per_unit": m["price_per_unit"],
                "unit": m["unit"],
                "stock_available": m["stock_available"],
                "is_organic": m["is_organic"]
            }
            for m in materials
        ]
    }


async def list_suppliers(district: str = None, category: str = None,
                         min_rating: float = None, verified_only: bool = False,
                         db: Session = None) -> List[Dict]:
    results = []
    for supplier in MOCK_SUPPLIERS:
        if district and district not in supplier["service_areas"]:
            continue
        if category and category not in supplier["categories"]:
            continue
        if min_rating and supplier["rating"] < min_rating:
            continue
        if verified_only and not supplier["is_verified"]:
            continue
        
        results.append({
            "id": supplier["id"],
            "business_name": supplier["business_name"],
            "district": supplier["district"],
            "rating": supplier["rating"],
            "trust_score": supplier["trust_score"],
            "total_reviews": supplier["total_reviews"],
            "is_verified": supplier["is_verified"],
            "categories_supplied": supplier["categories"],
            "service_areas": supplier["service_areas"]
        })
    
    return results


async def get_supplier_reviews(supplier_id: int, limit: int, offset: int,
                               db: Session) -> List[schemas.SupplierReviewResponse]:
    reviews = [r for r in MOCK_REVIEWS if r["supplier_id"] == supplier_id]
    return [
        schemas.SupplierReviewResponse(
            id=r["id"],
            supplier_id=r["supplier_id"],
            reviewer_id=random.randint(1, 100),
            reviewer_name=r["reviewer_name"],
            rating=r["rating"],
            title=r["title"],
            content=r["content"],
            quality_rating=r["quality_rating"],
            delivery_rating=r["delivery_rating"],
            communication_rating=r["communication_rating"],
            value_rating=r["value_rating"],
            is_verified_purchase=r["is_verified_purchase"],
            helpful_count=r["helpful_count"],
            created_at=r["created_at"]
        )
        for r in reviews[offset:offset+limit]
    ]


async def create_supplier_review(user_id: int, review: schemas.SupplierReviewCreate,
                                 db: Session) -> Optional[schemas.SupplierReviewResponse]:
    supplier = next((s for s in MOCK_SUPPLIERS if s["id"] == review.supplier_id), None)
    if not supplier:
        return None
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    reviewer_name = user.name if user else "Anonymous"
    
    new_review_id = len(MOCK_REVIEWS) + 1
    new_review = {
        "id": new_review_id,
        "supplier_id": review.supplier_id,
        "reviewer_name": reviewer_name,
        "rating": review.rating,
        "title": review.title,
        "content": review.content,
        "quality_rating": review.quality_rating,
        "delivery_rating": review.delivery_rating,
        "communication_rating": review.communication_rating,
        "value_rating": review.value_rating,
        "is_verified_purchase": True,
        "helpful_count": 0,
        "created_at": datetime.now()
    }
    MOCK_REVIEWS.append(new_review)
    
    return schemas.SupplierReviewResponse(
        id=new_review_id,
        supplier_id=review.supplier_id,
        reviewer_id=user_id,
        reviewer_name=reviewer_name,
        rating=review.rating,
        title=review.title,
        content=review.content,
        quality_rating=review.quality_rating,
        delivery_rating=review.delivery_rating,
        communication_rating=review.communication_rating,
        value_rating=review.value_rating,
        is_verified_purchase=True,
        helpful_count=0,
        created_at=datetime.now()
    )


async def mark_review_helpful(review_id: int, db: Session) -> bool:
    for review in MOCK_REVIEWS:
        if review["id"] == review_id:
            review["helpful_count"] += 1
            return True
    return False


async def create_connection_request(user_id: int, supplier_id: int, message: str,
                                    db: Session) -> Optional[schemas.SupplierConnectionResponse]:
    supplier = next((s for s in MOCK_SUPPLIERS if s["id"] == supplier_id), None)
    if not supplier:
        return None
    
    existing = db.query(models.SupplierConnection).filter(
        and_(
            models.SupplierConnection.supplier_id == supplier_id,
            models.SupplierConnection.requester_id == user_id
        )
    ).first()
    
    if existing:
        return None
    
    connection = models.SupplierConnection(
        supplier_id=supplier_id,
        requester_id=user_id,
        message=message,
        status="pending"
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    
    return schemas.SupplierConnectionResponse(
        id=connection.id,
        supplier_id=supplier_id,
        supplier_name=supplier["business_name"],
        requester_id=user_id,
        status="pending",
        message=message,
        response_message=None,
        created_at=connection.created_at,
        responded_at=None
    )


async def get_user_connections(user_id: int, status: str, db: Session) -> List[schemas.SupplierConnectionResponse]:
    query = db.query(models.SupplierConnection).filter(
        models.SupplierConnection.requester_id == user_id
    )
    if status:
        query = query.filter(models.SupplierConnection.status == status)
    
    connections = query.all()
    results = []
    for conn in connections:
        supplier = next((s for s in MOCK_SUPPLIERS if s["id"] == conn.supplier_id), None)
        results.append(schemas.SupplierConnectionResponse(
            id=conn.id,
            supplier_id=conn.supplier_id,
            supplier_name=supplier["business_name"] if supplier else "Unknown",
            requester_id=conn.requester_id,
            status=conn.status,
            message=conn.message,
            response_message=conn.response_message,
            created_at=conn.created_at,
            responded_at=conn.responded_at
        ))
    
    return results


async def respond_to_connection(connection_id: int, status: str, db: Session) -> bool:
    connection = db.query(models.SupplierConnection).filter(
        models.SupplierConnection.id == connection_id
    ).first()
    
    if not connection:
        return False
    
    connection.status = status
    connection.responded_at = datetime.now()
    db.commit()
    return True


async def create_quote_request(user_id: int, quote: schemas.QuoteRequestCreate,
                               db: Session) -> Optional[schemas.QuoteRequestResponse]:
    supplier = next((s for s in MOCK_SUPPLIERS if s["id"] == quote.supplier_id), None)
    if not supplier:
        return None
    
    quote_number = f"QT{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    quote_request = models.QuoteRequest(
        quote_number=quote_number,
        supplier_id=quote.supplier_id,
        requester_id=user_id,
        material_id=quote.material_id,
        material_name=quote.material_name,
        quantity=quote.quantity,
        unit=quote.unit,
        description=quote.description,
        required_by=quote.required_by,
        delivery_district=quote.delivery_district,
        status="pending"
    )
    db.add(quote_request)
    db.commit()
    db.refresh(quote_request)
    
    return schemas.QuoteRequestResponse(
        id=quote_request.id,
        quote_number=quote_number,
        supplier_id=quote.supplier_id,
        supplier_name=supplier["business_name"],
        requester_id=user_id,
        material_name=quote.material_name,
        quantity=quote.quantity,
        unit=quote.unit,
        description=quote.description,
        required_by=quote.required_by,
        delivery_district=quote.delivery_district,
        quoted_price=None,
        quoted_total=None,
        valid_until=None,
        notes=None,
        status="pending",
        created_at=quote_request.created_at,
        responded_at=None
    )


async def get_user_quotes(user_id: int, status: str, db: Session) -> List[schemas.QuoteRequestResponse]:
    query = db.query(models.QuoteRequest).filter(
        models.QuoteRequest.requester_id == user_id
    )
    if status:
        query = query.filter(models.QuoteRequest.status == status)
    
    quotes = query.all()
    results = []
    for q in quotes:
        supplier = next((s for s in MOCK_SUPPLIERS if s["id"] == q.supplier_id), None)
        results.append(schemas.QuoteRequestResponse(
            id=q.id,
            quote_number=q.quote_number,
            supplier_id=q.supplier_id,
            supplier_name=supplier["business_name"] if supplier else "Unknown",
            requester_id=q.requester_id,
            material_name=q.material_name,
            quantity=q.quantity,
            unit=q.unit,
            description=q.description,
            required_by=q.required_by,
            delivery_district=q.delivery_district,
            quoted_price=q.quoted_price,
            quoted_total=q.quoted_total,
            valid_until=q.valid_until,
            notes=q.notes,
            status=q.status,
            created_at=q.created_at,
            responded_at=q.responded_at
        ))
    
    return results


async def respond_to_quote(quote_id: int, status: str, db: Session) -> bool:
    quote = db.query(models.QuoteRequest).filter(
        models.QuoteRequest.id == quote_id
    ).first()
    
    if not quote:
        return False
    
    quote.status = status
    quote.responded_at = datetime.now()
    db.commit()
    return True


async def create_bulk_request(creator_id: int, title: str, description: str,
                            materials: List[Dict], target_quantity: int,
                            district: str, serving_districts: List[str],
                            expires_in_days: int = 30,
                            db: Session = None) -> Dict:
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
    bulk_request = db.query(models.BulkRequest).filter(
        models.BulkRequest.id == bulk_request_id
    ).first()

    if not bulk_request:
        raise ValueError("Bulk request not found")

    existing = db.query(models.BulkRequestParticipant).filter(
        and_(
            models.BulkRequestParticipant.bulk_request_id == bulk_request_id,
            models.BulkRequestParticipant.user_id == user_id
        )
    ).first()

    if existing:
        existing.quantity = quantity
        existing.status = "Committed"
    else:
        participant = models.BulkRequestParticipant(
            bulk_request_id=bulk_request_id,
            user_id=user_id,
            quantity=quantity
        )
        db.add(participant)

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

    prices = [d["price"] for d in trend_data]
    avg_price = sum(prices) / len(prices)
    min_price = min(prices)
    max_price = max(prices)

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
