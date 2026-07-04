from pydantic import BaseModel
from typing import Optional


class Company(BaseModel):
    name: Optional[str] = None

    domain: Optional[str] = None

    industry: Optional[str] = None

    employee_size: Optional[str] = None

    revenue: Optional[str] = None

    website: Optional[str] = None

    industry_url: Optional[str] = None

    employee_size_url: Optional[str] = None

    revenue_url: Optional[str] = None