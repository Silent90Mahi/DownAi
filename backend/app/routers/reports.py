from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import schemas
from ..routers.auth import get_current_user
from .. import models
from ..services import analytics_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# REPORT ENDPOINTS
# ============================================================================

@router.post("/generate")
async def generate_report(
    request: schemas.ReportGenerateRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate analytics report"""
    # Only admins can generate reports
    if current_user.role.value not in ["Admin", "DPD"]:
        raise Exception("Access denied")

    report = await analytics_service.generate_report(
        request.report_type,
        request.filters,
        request.date_range,
        db
    )

    return {
        "report_id": report["report_id"],
        "report_type": report["report_type"],
        "status": report["status"],
        "generated_at": report["generated_at"],
        "data": report["data"],
        "download_url": f"/api/reports/download/{report['report_id']}"
    }

@router.get("/download/{report_id}")
async def download_report(
    report_id: str,
    current_user: models.User = Depends(get_current_user)
):
    """Download generated report (mock)"""
    # In production, generate actual PDF/CSV file
    return {
        "message": "Report download (mock endpoint)",
        "report_id": report_id,
        "note": "In production, this would return the actual file"
    }
