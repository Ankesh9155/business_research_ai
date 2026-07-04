class LeadScorer:


    def calculate(self, lead: dict) -> int:

        score = 0

        if lead.get("organization_name") or lead.get("company"):
            score += 20

        if lead.get("title") or lead.get("job_title"):
            score += 20

        if lead.get("linkedin_url"):
            score += 20

        if lead.get("email_verified"):
            score += 20

        if lead.get("revenue"):
            score += 20

        return score