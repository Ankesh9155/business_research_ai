from pydantic import BaseModel
from typing import List


class InfoCriteria(BaseModel):

    countries: List[str]

    industries: List[str]

    job_titles: List[str]

    employee_size: str

    max_contacts_per_domain: int

class TALCompany(BaseModel):

    company_name: str

    domain: str

class ResearchInput(BaseModel):

    info: InfoCriteria

    companies: list[TALCompany]