import re
from urllib.parse import urljoin

import scrapy
from scrapy import Request
from scrapy_playwright.page import PageMethod


def uniq(seq):
    seen = set()
    for x in seq:
        if x and x not in seen:
            seen.add(x)
            yield x

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")

GRID = "body > main > section > div.py-12 > div > div.mt-5"  # list/grid wrapper under <main>


class ContactsSpider(scrapy.Spider):
    name = "contacts"
    custom_settings = {
        "CONCURRENT_REQUESTS": 2,
        "PLAYWRIGHT_MAX_CONTEXTS": 1,
        "PLAYWRIGHT_MAX_PAGES_PER_CONTEXT": 1,
        "ROBOTSTXT_OBEY": False,
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 120_000,
    }

    # ---------- Playwright ----------
    def add_pw(self, url, referer=None):
        return {
            "playwright": True,
            "playwright_include_page": True,
            "errback": self.errback,
            "playwright_page_methods": [
                PageMethod("goto", url, wait_until="domcontentloaded", timeout=120_000),
                PageMethod("wait_for_timeout", 700),

                # Dismiss consent banners via common selectors
                PageMethod("evaluate", """
                  () => {
                    for (const s of [
                      'button[aria-label="Accept"]',
                      '#onetrust-accept-btn-handler',
                      'button.cookie-accept',
                      '.ot-sdk-container #onetrust-accept-btn-handler',
                      'button#acceptAllButton',
                      'button#accept-recommended-btn-handler'
                    ]) {
                      const el = document.querySelector(s);
                      if (el) { try { el.click(); } catch(e) {} }
                    }
                  }
                """),
                PageMethod("wait_for_timeout", 300),

                # Bring filter controls into view
                PageMethod("evaluate", "window.scrollTo(0, 200)"),
                PageMethod("wait_for_timeout", 200),

                # Select a non-empty Sector option, if a sector control exists
                PageMethod("evaluate", """
                  () => {
                    const sel = document.querySelector("select[name='sector'], select#sector, [data-testid='sector']");
                    if (sel && sel.options && sel.options.length > 1) {
                      try { sel.value = sel.options[1].value; sel.dispatchEvent(new Event('change', {bubbles:true})) } catch(e){}
                    }
                  }
                """),
                PageMethod("wait_for_timeout", 300),

                # Select a non-empty Country option, if a country control exists
                PageMethod("evaluate", """
                  () => {
                    const sel = document.querySelector("select[name='country'], select#country, [data-testid='country']");
                    if (sel && sel.options && sel.options.length > 1) {
                      try { sel.value = sel.options[1].value; sel.dispatchEvent(new Event('change', {bubbles:true})) } catch(e){}
                    }
                  }
                """),
                PageMethod("wait_for_timeout", 400),

                # Click Search/Apply/Filter if present
                PageMethod("evaluate", """
                  () => {
                    const btn = [...document.querySelectorAll('button')].find(b =>
                      /search|apply|filter|submit/i.test(b.textContent||'')
                    );
                    if (btn) { try { btn.click(); } catch(e){} }
                  }
                """),
                PageMethod("wait_for_timeout", 900),

                # Try to mount lazy content
                PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                PageMethod("wait_for_timeout", 800),

                # Ensure the grid wrapper exists
                PageMethod("wait_for_selector", GRID, timeout=30_000),
            ],
            "headers": {"Referer": referer} if referer else None,
        }

    def start_requests(self):
        seeds = []
        u = getattr(self, "url", None)
        uf = getattr(self, "url_file", None)
        if u:
            seeds.append(u.strip())
        if uf:
            with open(uf, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("http"):
                        seeds.append(line)
        for s in uniq(seeds):
            yield Request(s, meta=self.add_pw(s), callback=self.parse_directory)

    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page:
            try:
                await page.close()
            except Exception:
                pass
        self.logger.error("Playwright error on %s: %s", failure.request.url, failure.value)

    # ---------- Helpers ----------
    def extract_contacts(self, text):
        t = re.sub(r"\s+", " ", text or "")
        emails = list(uniq(m.group(0) for m in EMAIL_RE.finditer(t)))
        phones = list(uniq(m.group(0) for m in PHONE_RE.finditer(t)))
        return emails, phones

    # ---------- Parse the first page ----------
    def parse_directory(self, response):
        # If the empty-state message is present, filters weren’t sufficient yet
        empty = response.css(f"{GRID} ::text").re_first(r"We were not able to find the results")
        if empty:
            self.logger.warning("Directory shows empty state on %s (no cards yet).", response.url)

        # Iterate direct children under the grid; treat those with a title h5 as cards
        cards = [card for card in response.css(f"{GRID} > div") if card.css("h5")]
        self.logger.info("Matched %d candidate cards", len(cards))

        for card in cards:
            name = card.css("h5::text").get()

            # Inline anchors
            mail_href = card.css("a[href^='mailto:']::attr(href)").get()
            tel_href  = card.css("a[href^='tel:']::attr(href)").get()

            # Full text for regex sweep
            text_blob = " ".join(t.strip() for t in card.css("::text").getall() if t and t.strip())
            emails, phones = self.extract_contacts(text_blob)

            if mail_href and mail_href.startswith("mailto:"):
                emails.append(mail_href[7:])
            if tel_href and tel_href.startswith("tel:"):
                phones.append(tel_href[4:])

            emails = list(uniq(emails))
            phones = list(uniq(phones))

            if any([name, emails, phones]):
                yield {
                    "url": response.url,
                    "profile_in_page": True,
                    "name_candidates": [name] if name else [],
                    "emails": emails,
                    "phones": phones,
                    "socials": [],
                    "notes": {},
                }
