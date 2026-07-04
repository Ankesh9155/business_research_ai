import pandas as pd

from models.lead import Lead


class ExcelWriter:


    def write(
        self,
        leads: list[Lead],
        file_path: str
    ):
        rows = []

        for lead in leads:

            rows.append({
                "First Name": lead.first_name,
                "Last Name": lead.last_name,
                "Job Title": lead.job_title,

                "Company":
                    lead.company.name,

                "Domain":
                    lead.company.domain,

                "Email":
                    lead.email,

                "Phone":
                    lead.contact.phone,

                "City":
                    lead.contact.city,

                "Country":
                    lead.contact.country,

                "LinkedIn":
                    lead.linkedin_url,

                "Industry":
                    lead.company.industry,

                "Employee Size":
                    lead.company.employee_size,

                "Revenue":
                    lead.company.revenue,

                "Score":
                    lead.confidence_score,

                "Status":
                    lead.status
            })


        df = pd.DataFrame(rows)

        df.to_excel(
            file_path,
            index=False
        )