import re


class EmailTool:

    def generate_patterns(
        self,
        first_name,
        last_name,
        domain
    ):

        first = first_name.lower()
        last = last_name.lower()

        return [
            f"{first}.{last}@{domain}",
            f"{first}@{domain}",
            f"{first[0]}{last}@{domain}",
            f"{first}{last}@{domain}"
        ]


    def verify_domain(
        self,
        email,
        domain
    ):
        """
        Verify email domain
        """

        return email.endswith(
            f"@{domain}"
        )