from tools.gemini_client import GeminiClient


class GoogleSearchTool:

    def __init__(self):
        self.gemini = GeminiClient()


    def search_company_contact(
        self,
        company,
        country
    ):
        """
        Search Google for HQ information
        """

        print(
            f"Searching {company} in {country}"
        )

        contact = {
            "phone": None,
            "address": None,
            "city": None,
            "state": None,
            "postal_code": None,
            "country": country
        }

        if not company:
            return contact

        result = self.gemini.search_json(
            f"Find the headquarters contact details for the company "
            f"\"{company}\" in {country or 'its home country'}. "
            "Return a JSON object with keys: phone, address, city, state, "
            "postal_code. Use null for anything you cannot verify."
        )

        for key in ("phone", "address", "city", "state", "postal_code"):
            contact[key] = result.get(key) or None

        return contact