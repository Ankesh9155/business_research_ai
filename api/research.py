from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

import asyncio
import tempfile
import traceback

from sqlalchemy.orm import Session

from database import get_db, DatabaseService
from services.excel_reader import ExcelReader
from graphs import build_graph


router = APIRouter(
    prefix="/research",
    tags=["Research"]
)

db_service = DatabaseService()


def _lead_to_db_record(lead: dict, company_domain: str) -> dict:
    """Map an Apollo lead dict to LeadRecord column names."""

    # Apollo uses "title" for job title
    job_title = lead.get("title") or lead.get("job_title", "")

    # Domain can come from organization or be passed in from TAL
    org = lead.get("organization") or {}
    domain = (
        lead.get("domain")
        or org.get("website_url", "").replace("https://", "").replace("http://", "").rstrip("/")
        or company_domain
    )

    # Revenue from the revenue enrichment we added
    revenue_data = lead.get("revenue") or {}
    revenue = str(revenue_data.get("revenue") or "") or None

    # Contact info from contact enrichment we added
    contact = lead.get("contact") or {}

    # Industry/employee size from the Gemini company lookup, falling back
    # to whatever Apollo's own organization data already had
    company_info = lead.get("company_data") or {}

    return {
        "first_name":       lead.get("first_name"),
        "last_name":        lead.get("last_name"),
        "job_title":        job_title or None,
        "linkedin_url":     lead.get("linkedin_url"),
        "email":            lead.get("email"),
        "email_verified":   bool(lead.get("email_verified", False)),
        "company_name":     lead.get("organization_name") or lead.get("company"),
        "domain":           domain or None,
        "industry":         company_info.get("industry") or org.get("industry"),
        "employee_size":    company_info.get("employee_size") or str(org.get("estimated_num_employees") or ""),
        "revenue":          revenue,
        "phone":            contact.get("phone") or lead.get("phone_numbers", [None])[0],
        "address":          contact.get("address"),
        "city":             contact.get("city") or lead.get("city"),
        "state":            contact.get("state") or lead.get("state"),
        "postal_code":      contact.get("postal_code"),
        "country":          contact.get("country") or lead.get("country"),
        "confidence_score": lead.get("score") or 0,
        "review_status":    "PENDING",
    }


@router.post("/start")
async def start_research(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Start AI research for every company in the TAL sheet.
    Saves all found leads to the database with status PENDING.
    """

    # Save uploaded file temporarily
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    content = await file.read()
    temp.write(content)
    temp.close()

    # Parse Excel
    try:
        reader = ExcelReader()
        research_input = reader.read(temp.name)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error":  "Failed to read Excel file",
                "reason": str(e),
                "hint": (
                    "Make sure the file has two sheets named exactly "
                    "'Info' and 'TAL' with the correct column headers."
                ),
            }
        )

    companies = research_input.companies

    if not companies:
        return {
            "message":         "No companies found in TAL sheet",
            "total_companies": 0,
            "total_leads":     0,
            "results":         []
        }

    # Create a research job record
    job = db_service.create_job(db)

    graph, linkedin_agent = build_graph()
    all_results = []
    errors      = []
    total_saved = 0

    for company in companies:

        try:
            result = await asyncio.to_thread(
                graph.invoke,
                {
                    "input":   research_input,
                    "company": company,
                }
            )

            final_leads = result.get("final_leads", [])
            saved_ids   = []

            for lead in final_leads:
                try:
                    record = db_service.save_lead(
                        db,
                        _lead_to_db_record(lead, company.domain)
                    )
                    saved_ids.append(record.id)
                    total_saved += 1
                except Exception as save_err:
                    print(f"[DB] Failed to save lead: {save_err}")

            all_results.append(
                {
                    "company":     company.company_name,
                    "domain":      company.domain,
                    "leads_found": len(final_leads),
                    "saved_ids":   saved_ids,
                    "status":      result.get("status", "COMPLETED"),
                }
            )

        except Exception as e:
            errors.append(
                {
                    "company": company.company_name,
                    "error":   str(e),
                    "trace":   traceback.format_exc(),
                }
            )

    # One browser session was kept alive across the whole batch — close it now
    await asyncio.to_thread(linkedin_agent.close)

    # Mark job as done
    job.status = "COMPLETED"
    db.commit()

    return {
        "message":         "Research completed",
        "job_id":          job.id,
        "total_companies": len(companies),
        "total_leads":     total_saved,
        "results":         all_results,
        "errors":          errors,
        "next_step": (
            "Go to GET /leads/ to see all pending leads, "
            "then PUT /review/{lead_id}?status=APPROVED or REJECTED to review each one."
        ),
    }
