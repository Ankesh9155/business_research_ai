class RequirementAgent:

    def execute(self, state):

        research_input = state["input"]

        companies = research_input.companies

        return {
            "criteria": research_input.info,
            "companies": companies,
            # "company" is NOT set here; the API loop injects it per-company
        }
