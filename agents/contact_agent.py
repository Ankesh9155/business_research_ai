from tools.google_search_tool import GoogleSearchTool


class ContactAgent:

    def __init__(self):
        self.search = GoogleSearchTool()


    def execute(self, state):

        company  = state.get("company")
        criteria = state.get("criteria")
        leads    = state.get("email_leads", [])

        country = criteria.countries[0] if criteria and criteria.countries else ""

        # HQ contact info is a company-level fact — one lookup per company,
        # reused across every lead, instead of repeating an identical
        # search for each lead at that company.
        contact = self.search.search_company_contact(
            company.company_name if company else "", country
        )

        for lead in leads:
            lead["contact"] = contact

        return {"contact_leads": leads}
