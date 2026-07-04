import json
import re

from google import genai
from google.genai import types

from auth.credential_manager import CredentialManager


class GeminiClient:
    """
    Thin wrapper around the free-tier Gemini API, used by agents that need
    structured data extraction from web knowledge (company/contact lookups).
    """

    MODEL = "gemini-2.5-flash"

    def __init__(self):
        credential = CredentialManager()
        self.client = genai.Client(api_key=credential.get("GOOGLE_API_KEY"))

    def search_json(self, prompt: str) -> dict:
        """
        Ask Gemini to research a query with Google Search grounding and
        return a JSON object. Returns {} if the model fails or replies
        with anything that isn't valid JSON.
        """
        # The Gemini API does not allow combining the google_search tool
        # with a forced JSON response mime type, so the JSON contract is
        # enforced via the prompt and parsed out of the free-form reply.

        try:
            response = self.client.models.generate_content(
                model=self.MODEL,
                contents=(
                    f"{prompt}\n\n"
                    "Respond with only a single JSON object, no markdown "
                    "fences and no extra commentary."
                ),
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                ),
            )

            text = response.text.strip()
            match = re.search(r"\{.*\}", text, re.DOTALL)

            return json.loads(match.group(0)) if match else {}

        except Exception as e:
            print(f"[Gemini] Request failed: {e}")
            return {}
