from pydantic import BaseModel
from typing import Optional


class Contact(BaseModel):
    phone: Optional[str] = None

    address_1: Optional[str] = None

    city: Optional[str] = None

    state: Optional[str] = None

    postal_code: Optional[str] = None

    country: Optional[str] = None

    phone_source_url: Optional[str] = None