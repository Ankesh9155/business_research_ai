from tools.linkedin_tool import LinkedInTool


class LinkedInAgent:

    def __init__(self):
        self.linkedin = LinkedInTool()
        self._logged_in = False
        self._filters_ready = False


    def execute(self, state):

        company  = state.get("company")
        criteria = state.get("criteria")

        if not company or not criteria:
            return {"linkedin_leads": []}

        leads = self._search(company, criteria)

        return {"linkedin_leads": leads}


    def _search(self, company, criteria):

        limit = criteria.max_contacts_per_domain or 5

        if not self._logged_in:
            self.linkedin.login()
            self._logged_in = True

        if not self._filters_ready:
            # Job title / industry / geography are shared across the whole
            # batch — only the Current company filter changes per company.
            self.linkedin.setup_search_filters(
                job_titles=criteria.job_titles,
                industries=criteria.industries,
                countries=criteria.countries,
            )
            self._filters_ready = True

        leads = self.linkedin.search_people(
            company=company.company_name,
            limit=limit,
        )

        for person in leads:
            person["domain"] = company.domain

        return leads


    def close(self):
        """
        Call once after all companies in a batch have been processed —
        keeps a single browser session alive across the whole batch instead
        of relaunching per company.
        """
        if self._logged_in:
            self.linkedin.close()
            self._logged_in = False
            self._filters_ready = False
