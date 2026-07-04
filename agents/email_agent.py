from tools.email_tool import EmailTool


class EmailAgent:

    def __init__(self):
        self.email_tool = EmailTool()


    def execute(self, state):

        leads = state.get("validated_leads", [])

        for lead in leads:

            first_name = lead.get("first_name", "")
            last_name  = lead.get("last_name", "")

            # Derive domain from the organization URL or existing email
            domain = lead.get("domain", "")
            if not domain:
                email = lead.get("email", "")
                if "@" in email:
                    domain = email.split("@")[-1]

            if first_name and last_name and domain:
                lead["possible_emails"] = self.email_tool.generate_patterns(
                    first_name, last_name, domain
                )
            else:
                lead["possible_emails"] = []

        return {"email_leads": leads}
