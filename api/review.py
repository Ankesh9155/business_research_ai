from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from database import (
    get_db,
    DatabaseService
)


router = APIRouter(
    prefix="/review",
    tags=["Review"]
)


db_service = DatabaseService()


@router.put("/{lead_id}")
def review_lead(
    lead_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """
    Approve or reject lead.
    """

    lead = (
        db_service.update_review_status(
            db,
            lead_id,
            status
        )
    )


    if not lead:
        return {
            "error": "Lead not found"
        }

    pending = db_service.get_leads(db, status="PENDING")

    return {
        "message": "Review updated",
        "lead_id": lead.id,
        "status": lead.review_status,
        "pending_count": len(pending),
        "pending_leads": [
            {
                "id":             p.id,
                "first_name":     p.first_name,
                "last_name":      p.last_name,
                "job_title":      p.job_title,
                "email":          p.email,
                "linkedin_url":   p.linkedin_url,
                "company_name":   p.company_name,
                "domain":         p.domain,
                "city":           p.city,
                "country":        p.country,
                "confidence_score": p.confidence_score,
            }
            for p in pending
        ],
    }