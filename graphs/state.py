from typing import TypedDict, Optional, List, Dict, Any

from models.sheet import (
    InfoCriteria,
    TALCompany,
    ResearchInput
)


class LeadResearchState(TypedDict, total=False):

    # ── Input ────────────────────────────────────────────
    input: ResearchInput            # required; always injected by API
    company: TALCompany             # required; injected per-company by API loop

    # ── RequirementAgent ─────────────────────────────────
    criteria: InfoCriteria
    companies: List[TALCompany]

    # ── ApolloAgent ──────────────────────────────────────
    apollo_leads: List[Dict[str, Any]]

    # ── LinkedInAgent ────────────────────────────────────
    linkedin_leads: List[Dict[str, Any]]

    # ── ValidationAgent ──────────────────────────────────
    validated_leads: List[Dict[str, Any]]

    # ── EmailAgent ───────────────────────────────────────
    email_leads: List[Dict[str, Any]]

    # ── ContactAgent ─────────────────────────────────────
    contact_leads: List[Dict[str, Any]]

    # ── CompanyAgent ─────────────────────────────────────
    company_data: Dict[str, Any]

    # ── RevenueAgent ─────────────────────────────────────
    revenue_leads: List[Dict[str, Any]]

    # ── QualityAgent ─────────────────────────────────────
    final_leads: List[Dict[str, Any]]

    # ── HumanReviewAgent ─────────────────────────────────
    approved_leads: List[Dict[str, Any]]
    status: str

    # ── Logging ──────────────────────────────────────────
    messages: List[str]
