from tools.gemini_client import GeminiClient


class ZoomInfoTool:

    def __init__(self):
        self.gemini = GeminiClient()


    def get_company_revenue(
        self,
        company_name
    ):
        """
        Search company revenue
        """

        print(
            f"Searching revenue for {company_name}"
        )

        revenue = {
            "revenue": None,
            "source_url": None
        }

        if not company_name:
            return revenue

        result = self.gemini.search_json(
            f"Look up the annual revenue for the company \"{company_name}\". "
            "Return a JSON object with keys: revenue (a human-readable "
            "figure such as '$1.2B' or a documented range), and source_url "
            "(the URL you found the figure on). Use null for anything you "
            "cannot verify."
        )

        revenue["revenue"]     = result.get("revenue") or None
        revenue["source_url"]  = result.get("source_url") or None

        return revenue