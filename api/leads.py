from fastapi import APIRouter, Depends, Query

from sqlalchemy.orm import Session

from database import get_db, DatabaseService


router = APIRouter(
    prefix="/leads",
    tags=["Leads"]
)

db_service = DatabaseService()


@router.get("/")
def get_all_leads(
    status: str = Query(None, description="Filter by review_status: PENDING, APPROVED, REJECTED"),
    db: Session = Depends(get_db)
):
    """
    Get all saved leads.
    Optionally filter by review status: PENDING, APPROVED, REJECTED.
    """

    leads = db_service.get_leads(db, status=status)

    return {
        "count": len(leads),
        "filter": status or "ALL",
        "data": [
            {
                "id":             lead.id,
                "review_status":  lead.review_status,
                "first_name":     lead.first_name,
                "last_name":      lead.last_name,
                "job_title":      lead.job_title,
                "email":          lead.email,
                "linkedin_url":   lead.linkedin_url,
                "company_name":   lead.company_name,
                "domain":         lead.domain,
                "city":           lead.city,
                "country":        lead.country,
                "confidence_score": lead.confidence_score,
            }
            for lead in leads
        ]
    }
