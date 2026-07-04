class ValidationAgent:

    def execute(self, state):

        # LinkedIn is the primary source; Apollo results fill in anything
        # LinkedIn missed. Leads are merged with LinkedIn taking priority
        # on duplicates.
        linkedin_leads = state.get("linkedin_leads", [])
        apollo_leads   = state.get("apollo_leads", [])

        seen        = set()
        valid_leads = []

        for lead in linkedin_leads + apollo_leads:

            key = lead.get("linkedin_url") or (
                (lead.get("first_name") or "").strip().lower(),
                (lead.get("last_name") or "").strip().lower(),
                (lead.get("company") or lead.get("organization_name") or "").strip().lower(),
            )

            if key in seen:
                continue

            seen.add(key)
            valid_leads.append(lead)

        return {"validated_leads": valid_leads}
