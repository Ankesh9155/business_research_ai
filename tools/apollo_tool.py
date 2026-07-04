import requests

from auth.apollo_auth import ApolloAuth


class ApolloTool:

    BASE_URL = "https://api.apollo.io/api/v1"


    def __init__(self):
        self.auth = ApolloAuth()

        self.headers = {
            "X-Api-Key": self.auth.get_api_key(),
            "Content-Type": "application/json"
        }


    def search_people(self, company, title, country):
        """
        Search leads from Apollo.
        Returns list of people dicts or [] on error.
        """

        payload = {
            "organization_names": [company],
            "person_titles":      [title],
            "person_locations":   [country],
            "per_page":           10,
        }

        try:
            response = requests.post(
                f"{self.BASE_URL}/mixed_people/search",
                json=payload,
                headers=self.headers,
                timeout=30
            )

            data = response.json()

            if response.status_code != 200:
                print(
                    f"[Apollo] ERROR {response.status_code} "
                    f"for {company} / {title}: {data}"
                )
                return {"people": []}

            people = data.get("people", [])
            print(
                f"[Apollo] {company} / {title} → {len(people)} people found"
            )
            return data

        except Exception as e:
            print(f"[Apollo] Request failed for {company} / {title}: {e}")
            return {"people": []}
