from playwright.sync_api import sync_playwright


class BrowserTool:

    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None


    def start(self):
        """
        Start browser
        """
        self.playwright = sync_playwright().start()

        # Try system browsers first — bundled Chromium often fails DNS on Windows.
        # Edge ships with every Windows 11 machine; Chrome is a common fallback.
        for channel in ("msedge", "chrome", None):
            try:
                launch_kwargs = {"headless": self.headless}
                if channel:
                    launch_kwargs["channel"] = channel
                self.browser = self.playwright.chromium.launch(**launch_kwargs)
                break
            except Exception:
                if channel is None:
                    raise

        self.context = self.browser.new_context()

        self.page = self.context.new_page()

        return self.page


    def load_cookies(self, cookies):
        """
        Load saved session cookies
        """
        self.context.add_cookies(cookies)


    def save_cookies(self):
        """
        Save browser cookies
        """
        return self.context.cookies()


    def close(self):
        """
        Close browser
        """
        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()
