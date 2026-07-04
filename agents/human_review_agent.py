class HumanReviewAgent:

    def execute(self, state):

        leads = state.get("final_leads", [])

        print(f"Waiting for human approval... ({len(leads)} leads)")

        return {
            "approved_leads": leads,
            "status": "WAITING_FOR_REVIEW",
        }
