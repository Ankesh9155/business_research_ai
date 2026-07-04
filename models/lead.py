from pydantic import BaseModel
from typing import Optional

from models.contact import Contact
from models.company import Company


class Lead(BaseModel):

    first_name: Optional[str] = None

    last_name: Optional[str] = None

    job_title: Optional[str] = None

    linkedin_url: Optional[str] = None

    email: Optional[str] = None

    email_verified: bool = False

    company: Company

    contact: Contact

    confidence_score: int = 0

    status: str = "Pending"

    notes: Optional[str] = None