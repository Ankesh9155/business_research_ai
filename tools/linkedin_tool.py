import re
from pathlib import Path

from tools.browser_tool import BrowserTool
from auth.linkedin_auth import LinkedInAuth


DEBUG_DIR = Path("debug_linkedin")


class LinkedInTool:

    LINKEDIN_FEED     = "https://www.linkedin.com/feed/"
    LOGIN_URL         = "https://www.linkedin.com/login"
    SALES_NAV_SEARCH  = "https://www.linkedin.com/sales/search/people"

    def __init__(self):
        self.browser = BrowserTool()
        self.auth = LinkedInAuth()
        self._filters_ready = False


    def open(self):
        self.page = self.browser.start()


    def login(self, force_manual: bool = False):
        """
        Resume saved session if available, otherwise open a visible browser
        for the user to log in manually (passkey, 2FA, etc.) and save cookies.

        Pass force_manual=True to skip the saved-session check entirely and
        always show the login page for a fresh manual login.
        """
        if not force_manual:
            self.page = self.browser.start()

            saved = self.auth.load_session()

            if saved:
                self.browser.load_cookies(saved)
                self.page.goto(self.LINKEDIN_FEED)

                if "/feed" in self.page.url:
                    print("LinkedIn: session restored from cookies.")
                    return

                print("LinkedIn: saved session expired, need to log in again.")
                self.auth.logout()
                self.browser.close()

        # No valid session (or force_manual requested) — open login page and wait for the user
        self.browser = BrowserTool(headless=False)
        self.page = self.browser.start()
        self.page.goto(self.LOGIN_URL)

        print("LinkedIn: browser opened. Please log in (passkey / password / 2FA).")
        print("Waiting until you reach the LinkedIn feed...")

        self.page.wait_for_url("**/feed/**", timeout=180_000)

        cookies = self.browser.save_cookies()
        self.auth.save_session(cookies)
        print("LinkedIn: session saved. Future runs will log in automatically.")


    def _debug_dump(self, label):
        """
        Save a screenshot + a chunk of live HTML so selectors below can be
        corrected against what LinkedIn is actually rendering, since the
        Sales Navigator DOM isn't publicly documented and changes often.
        """
        DEBUG_DIR.mkdir(exist_ok=True)
        safe = re.sub(r"[^a-zA-Z0-9_-]", "_", label)[:100]

        try:
            self.page.screenshot(path=str(DEBUG_DIR / f"{safe}.png"), full_page=True)
            print(f"[LinkedIn] DEBUG screenshot saved: {DEBUG_DIR / (safe + '.png')}")
        except Exception:
            pass

        try:
            print(f"[LinkedIn] DEBUG ({label}) HTML:\n{self.page.content()[:3000]}")
        except Exception:
            pass


    def setup_search_filters(self, job_titles, industries, countries):
        """
        Open Sales Navigator search once per batch and apply the Current job
        title / Industry / Geography filters. Only the Current company
        filter needs to change per company afterwards (see set_company_filter).
        """
        self.page.goto(self.SALES_NAV_SEARCH)

        # LinkedIn sometimes routes through an account/contract-chooser
        # interstitial before landing on search, which delays when the
        # filter panel actually exists — wait for a stable panel element
        # instead of a fixed delay, or every filter silently fails to open.
        self.page.wait_for_selector("text=Geography", timeout=30_000)

        self._add_filter_values("Current job title", job_titles)
        self._add_filter_values("Industry", industries)
        self._add_filter_values("Geography", countries)

        self._filters_ready = True


    def _toggle_filter_panel(self, filter_label):
        """
        Filter section headers collapse/expand via a button whose accessible
        name is "Expand {label} filter" when closed and "Collapse {label}
        filter" when open (confirmed via live inspection for the Expand
        state). Note there is a SEPARATE "Show tooltip for {label} filter"
        info-icon button with a similar name that must NOT be matched here,
        or it opens a help tooltip that blocks the rest of the panel.
        """
        toggle = self.page.get_by_role(
            "button",
            name=re.compile(rf"^(Expand|Collapse) {re.escape(filter_label)} filter$", re.I),
        ).first
        toggle.click(timeout=5_000)


    def _select_filter_value(self, value):
        """
        Assumes exactly one filter panel is open. The input is an
        autocomplete combobox identified by its placeholder (not
        aria-label). Typing a value shows a suggestion dropdown of
        [role=option] rows, each with separate "Include" / "Exclude" text
        actions.

        Grabbing "the first option" right after typing is a race: the
        dropdown can still be showing a stale suggestion from a previous
        value when read, which silently selects the wrong entity (e.g. a
        leftover "Daraz" suggestion when typing "Stripe"). Job title
        suggestions are also semantic (typing "CEO" surfaces "Chief
        Executive Officer", not a literal-text match), so we can't just
        wait for an option containing the typed value either — instead,
        give the debounced autocomplete request a moment to settle before
        reading the (now-fresh) first option.
        """
        box = self.page.locator(
            "input[role=combobox]:not([placeholder='Search keywords'])"
        ).first
        box.click(timeout=3_000)
        box.fill("", timeout=3_000)
        box.type(value, delay=50)

        self.page.wait_for_timeout(1_200)

        option = self.page.get_by_role("option").first
        option.wait_for(timeout=5_000)
        option.get_by_text("Include", exact=True).click(timeout=3_000)


    def _add_filter_values(self, filter_label, values):
        if not values:
            return

        try:
            self._toggle_filter_panel(filter_label)
        except Exception as e:
            print(f"[LinkedIn] Could not open '{filter_label}' filter: {e}")
            self._debug_dump(f"filter_open_{filter_label}")
            return

        for value in values:
            try:
                self._select_filter_value(value)
                print(f"[LinkedIn] Added '{value}' to '{filter_label}' filter")
            except Exception as e:
                print(f"[LinkedIn] Could not add '{value}' to '{filter_label}' filter: {e}")
                self._debug_dump(f"filter_value_{filter_label}_{value}")

        # Collapse again so later filter panels aren't ambiguous when
        # locating "the" open combobox by placeholder.
        try:
            self._toggle_filter_panel(filter_label)
        except Exception:
            pass


    def set_company_filter(self, company_name):
        """
        Replace the Current company filter with a single company and let the
        results list refresh. Called once per company in the batch.
        """
        try:
            self._toggle_filter_panel("Current company")

            # A chip from the previous company (if any) is only removable
            # while this panel is expanded.
            remove_buttons = self.page.get_by_role(
                "button", name=re.compile(r"^Remove Current company filter", re.I)
            )
            while remove_buttons.count() > 0:
                try:
                    remove_buttons.first.click(timeout=2_000)
                except Exception:
                    break

            self._select_filter_value(company_name)
            self._toggle_filter_panel("Current company")

            print(f"[LinkedIn] Set company filter to '{company_name}'")
        except Exception as e:
            print(f"[LinkedIn] Could not set company filter to '{company_name}': {e}")
            self._debug_dump(f"company_filter_{company_name}")


    def search_people(self, company, limit=5):
        """
        Requires setup_search_filters() to have been called once already for
        this batch. Sets the Current company filter to `company`, then reads
        name / title directly off each result card in the list.

        NOTE: linkedin_url here is the Sales Navigator lead deep-link
        (/sales/lead/...), not a public linkedin.com/in/... profile URL —
        opening it requires Sales Navigator access.
        """
        if not self._filters_ready:
            raise RuntimeError("Call setup_search_filters() before search_people().")

        self.set_company_filter(company)

        try:
            # Wait for at least one row's real content (not just the
            # skeleton placeholder <li>) to actually render.
            self.page.wait_for_selector('[data-x-search-result="LEAD"]', timeout=15_000)
        except Exception:
            print(f"[LinkedIn] No results for company: {company}")
            self._debug_dump(f"no_results_{company}")
            return []

        # li.artdeco-list__item is a generic design-system class reused
        # elsewhere on the page; data-x-search-result="LEAD" uniquely marks
        # an actual rendered lead result row. Rows below the fold start as
        # skeleton placeholders and only gain this attribute once scrolled
        # near, so nudge the page a few times if we don't have enough yet.
        cards = self.page.locator('[data-x-search-result="LEAD"]')
        for _ in range(5):
            if cards.count() >= limit:
                break
            self.page.mouse.wheel(0, 1200)
            self.page.wait_for_timeout(800)

        count = min(cards.count(), limit)

        people = []

        for i in range(count):
            person = self._extract_lead_from_card(cards.nth(i), company)
            if person:
                people.append(person)

        print(f"[LinkedIn] {company} -> {len(people)} people found")

        return people


    def _extract_lead_from_card(self, card, company):
        try:
            # Sales Navigator lazy-renders cards below the fold as empty
            # skeleton placeholders until scrolled into view — without this,
            # every field read below times out even though the selectors
            # are correct.
            card.scroll_into_view_if_needed(timeout=5_000)

            full_name = card.locator('[data-anonymize="person-name"]').first.inner_text(
                timeout=5_000
            ).strip()
            job_title = card.locator('[data-anonymize="title"]').first.inner_text(
                timeout=5_000
            ).strip()
            href = card.locator(
                'a[data-lead-search-result^="profile-link"]'
            ).first.get_attribute("href", timeout=5_000)

            first_name, *rest = full_name.split(" ", 1)
            last_name = rest[0] if rest else ""

            sales_nav_url = f"https://www.linkedin.com{href}" if href else None
            public_url = self._get_public_profile_url(sales_nav_url) if sales_nav_url else None

            return {
                "first_name":   first_name,
                "last_name":    last_name,
                "job_title":    job_title,
                "company":      company,
                "linkedin_url": public_url or sales_nav_url,
                "source":       "linkedin",
            }

        except Exception as e:
            print(f"[LinkedIn] Skipped a result card: {e}")
            self._debug_dump(f"card_{company}")
            return None


    def _get_public_profile_url(self, sales_nav_url):
        """
        Open the lead's Sales Navigator profile in a new tab, click the
        "..." button next to Message (accessible name "Open actions
        overflow menu" — note there's a second, unrelated "More" button
        elsewhere on the page that must not be matched instead), and read
        the href off "View LinkedIn profile". That href is already the
        real public linkedin.com/in/... URL — no need to click through it.
        """
        lead_page = self.browser.context.new_page()

        try:
            lead_page.goto(sales_nav_url)
            lead_page.wait_for_selector("text=Message", timeout=15_000)

            more_btn = lead_page.get_by_role(
                "button", name="Open actions overflow menu"
            ).first
            more_btn.click(timeout=5_000)

            # get_by_text would match the inner <span> instead of the <a>
            # itself, which has no href — get_by_role("link", ...) targets
            # the anchor directly.
            view_profile = lead_page.get_by_role(
                "link", name="View LinkedIn profile", exact=True
            ).first
            view_profile.wait_for(timeout=5_000)

            return view_profile.get_attribute("href", timeout=3_000)

        except Exception as e:
            print(f"[LinkedIn] Could not get public profile URL for {sales_nav_url}: {e}")
            return None

        finally:
            lead_page.close()


    def close(self):
        self.browser.close()
