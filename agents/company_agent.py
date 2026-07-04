from tools.gemini_client import GeminiClient


class CompanyAgent:

    def __init__(self):
        self.gemini = GeminiClient()


    def execute(self, state):

        company = state.get("company")
        leads   = state.get("contact_leads", [])

        company_data = {
            "industry":          None,
            "employee_size":     None,
            "industry_url":      None,
            "employee_size_url": None,
        }

        if company:
            result = self.gemini.search_json(
                f"Look up the company \"{company.company_name}\" "
                f"(domain: {company.domain or 'unknown'}). "
                "Return a JSON object with keys: industry, employee_size, "
                "industry_url, employee_size_url. The *_url fields should "
                "be the source URL you found the fact on, or null if "
                "unknown."
            )

            for key in company_data:
                company_data[key] = result.get(key) or None

        # One Gemini lookup per company — attach the same result to every
        # lead so downstream stages (revenue, quality, DB save) see it.
        for lead in leads:
            lead["company_data"] = company_data

        return {"contact_leads": leads, "company_data": company_data}
