from tools.zoominfo_tool import ZoomInfoTool


class RevenueAgent:

    def __init__(self):
        self.zoom = ZoomInfoTool()


    def execute(self, state):

        company = state.get("company")
        leads   = state.get("contact_leads", [])

        # Revenue is a company-level fact — one lookup per company, reused
        # across every lead, instead of repeating an identical search for
        # each lead at that company.
        revenue = self.zoom.get_company_revenue(
            company.company_name if company else ""
        )

        for lead in leads:
            lead["revenue"] = revenue

        return {"revenue_leads": leads}
