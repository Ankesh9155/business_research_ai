from services.scorer import LeadScorer


class QualityAgent:

    def __init__(self):
        self.scorer = LeadScorer()


    def execute(self, state):

        leads = state.get("revenue_leads", [])

        for lead in leads:
            lead["score"] = self.scorer.calculate(lead)

        return {"final_leads": leads}
