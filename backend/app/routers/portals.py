from fastapi import APIRouter
from typing import List

router = APIRouter(prefix="/portals", tags=["portals"])

@router.get("/gem_tenders")
def get_mock_gem_tenders(category: str = "all"):
    """
    Mock integration returning Dummy Government GeM Tenders.
    """
    tenders = [
        {"id": "GEM-2026-X1", "title": "Bulk Supply of Jute Bags", "quantity": 5000, "budget": 150000, "category": "Textiles"},
        {"id": "GEM-2026-X2", "title": "Organic Pickles for Canteen", "quantity": 1000, "budget": 50000, "category": "Food Processing"},
        {"id": "GEM-2026-X3", "title": "Handmade Bamboo Baskets", "quantity": 200, "budget": 30000, "category": "Handicrafts"}
    ]
    if category != "all":
        tenders = [t for t in tenders if t["category"].lower() == category.lower()]
    return {"status": "success", "source": "GeM Mock API", "data": tenders}

@router.get("/ondc_demand")
def get_mock_ondc_demand():
    """
    Mock ONDC/eSARAS integration showing current market demand highlights.
    """
    return {
        "status": "success", 
        "source": "ONDC/eSARAS Mock API",
        "trending_categories": ["Organic Spices", "Handloom Sarees", "Millets"],
        "active_buyers": 1420
    }

@router.get("/serp_mis")
def get_serp_mis_data(district: str = "all"):
    """
    Mock SERP MIS federated data feed simulation.
    """
    return {
        "status": "success",
        "source": "SERP MIS Mock API",
        "data_points": {
            "total_shgs": 45000,
            "total_active_shgs_this_month": 12000,
            "avg_trust_score": 76.5
        }
    }

@router.post("/rtgs_alert")
def send_rtgs_alert(message: str):
    """
    Mock RTGS AWARE platform alert feed.
    """
    return {
        "status": "success",
        "recorded_alert": message,
        "message": "Alert sent to RTGS AWARE platform successfully."
    }
