from pydantic import BaseModel
from typing import List

from models.lead import Lead


class ResearchResponse(BaseModel):

    job_id: str

    status: str

    leads: List[Lead]