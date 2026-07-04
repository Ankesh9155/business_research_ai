from tools.apollo_tool import ApolloTool


class ApolloAgent:

    def __init__(self):
        self.apollo = ApolloTool()


    def execute(self, state):

        company  = state.get("company")
        criteria = state.get("criteria")

        if not company or not criteria:
            return {"apollo_leads": []}

        leads   = []
        country = criteria.countries[0] if criteria.countries else ""

        for title in criteria.job_titles:

            result = self.apollo.search_people(
                company=company.company_name,
                title=title,
                country=country
            )

            people = result.get("people", [])

            leads.extend(people)

        return {"apollo_leads": leads}
