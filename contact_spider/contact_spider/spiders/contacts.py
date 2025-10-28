import re  # [file:98]
import scrapy  # [file:98]
from bs4 import BeautifulSoup, Comment  # [file:98]
from urllib.parse import urljoin  # [file:98]
from scrapy import Request  # [file:98]
from scrapy_playwright.page import PageMethod  # [file:98]

# Social domains allowed by the task document  # [file:98]
SOCIAL_DOMAINS = (
    "linkedin.com","facebook.com","instagram.com","twitter.com","x.com",
    "youtube.com","github.com","behance.net","t.me","wa.me"
)  # [file:98]

# DOM-visible regexes (no script/style)  # [file:98]
EMAIL_REGEX = r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,})"  # [file:98]
PHONE_REGEX = r"(\+?\d[\d\-\s()]{6,18}\d)"  # 7–15 digits with punctuation  # [file:98]

# Inline “hide” flags per task doc  # [file:98]
HIDE_INLINE_FLAGS = ("display:none", "visibility:hidden", "opacity:0")  # [file:98]

def normalize_phone(num: str) -> str:  # [file:98]
    digits = re.sub(r"[^\d+]", "", num or "")  # [file:98]
    if digits.startswith("+"):  # [file:98]
        return "+" + re.sub(r"[^\d]", "", digits[1:])  # [file:98]
    return re.sub(r"[^\d]", "", digits)  # [file:98]

def _visible_tag(tag):  # [file:98]
    if tag.name in ("script","style","template","noscript"):  # [file:98]
        return False  # [file:98]
    if tag.has_attr("aria-hidden") and str(tag.get("aria-hidden","")).lower() == "true":  # [file:98]
        return False  # [file:98]
    style = str(tag.get("style","")).replace(" ", "").lower()  # [file:98]
    if any(flag in style for flag in HIDE_INLINE_FLAGS):  # [file:98]
        return False  # [file:98]
    return True  # [file:98]

def _iter_visible_text(soup):  # [file:98]
    for el in soup.find_all(string=True):  # [file:98]
        if isinstance(el, Comment):  # [file:98]
            continue  # [file:98]
        parent = el.parent  # [file:98]
        if parent and _visible_tag(parent):  # [file:98]
            t = str(el).strip()  # [file:98]
            if t:  # [file:98]
                yield t  # [file:98]

def _extract_socials(soup, base_url):  # [file:98]
    socials, notes = [], []  # [file:98]
    for a in soup.find_all("a", href=True):  # [file:98]
        if not _visible_tag(a):  # [file:98]
            continue  # [file:98]
        href = a.get("href","").strip()  # [file:98]
        if any(dom in href for dom in SOCIAL_DOMAINS):  # [file:98]
            label = a.get_text(" ", strip=True)  # [file:98]
            abs_url = urljoin(base_url, href)  # [file:98]
            socials.append({"href": abs_url, "label": label})  # [file:98]
            notes.append(f"social:{abs_url}|label:{label[:50]}")  # [file:98]
    return socials, notes  # [file:98]

def _extract_emails(soup, vis_texts):  # [file:98]
    emails, notes = set(), []  # [file:98]
    for a in soup.find_all("a", href=True):  # [file:98]
        if not _visible_tag(a):  # [file:98]
            continue  # [file:98]
        href = a["href"]  # [file:98]
        m = re.search(r"mailto:" + EMAIL_REGEX, href, re.IGNORECASE)  # [file:98]
        if m:  # [file:98]
            emails.add(m.group(1).strip().lower())  # [file:98]
            notes.append(f"mailto:{href}")  # [file:98]
    for t in vis_texts:  # [file:98]
        for m in re.finditer(EMAIL_REGEX, t, re.IGNORECASE):  # [file:98]
            emails.add(m.group(1).strip().lower())  # [file:98]
    return sorted(emails), notes  # [file:98]

def _extract_phones(soup, vis_texts):  # [file:98]
    phones, notes = set(), []  # [file:98]
    for a in soup.find_all("a", href=True):  # [file:98]
        if not _visible_tag(a):  # [file:98]
            continue  # [file:98]
        href = a["href"]  # [file:98]
        m = re.search(r"tel:" + PHONE_REGEX, href)  # [file:98]
        if m:  # [file:98]
            orig = m.group(1)  # [file:98]
            phones.add((orig.strip(), normalize_phone(orig)))  # [file:98]
            notes.append(f"tel:{href}")  # [file:98]
    for t in vis_texts:  # [file:98]
        for m in re.finditer(PHONE_REGEX, t):  # [file:98]
            orig = m.group(1)  # [file:98]
            phones.add((orig.strip(), normalize_phone(orig)))  # [file:98]
    out = [{"original": o, "normalized": n} for (o, n) in sorted(phones)]  # [file:98]
    seen, dedup = set(), []  # [file:98]
    for item in out:  # [file:98]
        key = item.get("normalized") or item.get("original")  # [file:98]
        if key and key not in seen:  # [file:98]
            seen.add(key)  # [file:98]
            dedup.append(item)  # [file:98]
    return dedup, notes  # [file:98]

def _title_case_name_candidates(texts):  # [file:98]
    names = set()  # [file:98]
    for t in texts:  # [file:98]
        for n in re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b", t):  # [file:98]
            if len(n.split()) <= 3 and 3 <= len(n) <= 50:  # [file:98]
                names.add(n.strip())  # [file:98]
    return names  # [file:98]

def _email_hint_name(local_part: str):  # [file:98]
    tokens = re.split(r"[._\-]+", local_part)  # [file:98]
    tokens = [t for t in tokens if t and not t.isdigit() and len(t) >= 2]  # [file:98]
    if not tokens or len(tokens) > 3:  # [file:98]
        return None  # [file:98]
    return " ".join(w.capitalize() for w in tokens)  # [file:98]

def _score_name(name: str, context: str):  # [file:98]
    score = 0.5  # [file:98]
    low = context.lower()  # [file:98]
    for k in ("contact", "founder", "director", "owner", "ceo", "principal"):  # [file:98]
        if k in low:  # [file:98]
            score += 0.1  # [file:98]
    if len(name.split()) == 2:  # [file:98]
        score += 0.05  # [file:98]
    return min(score, 0.95)  # [file:98]

def _extract_name_candidates(soup, vis_texts, emails):  # [file:98]
    likely_blocks = []  # [file:98]
    for sel in ["h1","h2","h3",".author",".person",".profile",".about",".contact"]:  # [file:98]
        likely_blocks += soup.select(sel)  # [file:98]
    texts = [x.get_text(" ", strip=True) for x in likely_blocks if _visible_tag(x)]  # [file:98]
    texts += list(vis_texts)  # [file:98]
    title_case = set(_title_case_name_candidates(texts))  # [file:98]
    for e in emails:  # [file:98]
        local = e.split("@",1)[0]  # [file:98]
        hint = _email_hint_name(local)  # [file:98]
        if hint:  # [file:98]
            title_case.add(hint)  # [file:98]
    nearby = " ".join(texts[:200])[:2000]  # [file:98]
    scored = [{"name": n, "confidence": _score_name(n, nearby)} for n in title_case]  # [file:98]
    scored.sort(key=lambda x: x["confidence"], reverse=True)  # [file:98]
    seen, out = set(), []  # [file:98]
    for s in scored:  # [file:98]
        k = s["name"].lower()  # [file:98]
        if k in seen:  # [file:98]
            continue  # [file:98]
        seen.add(k)  # [file:98]
        out.append(s)  # [file:98]
        if len(out) >= 5:  # [file:98]
            break  # [file:98]
    return out  # [file:98]

class ContactsSpider(scrapy.Spider):  # [file:98]
    name = "contacts"  # [file:98]

    def __init__(self, url=None, *args, **kwargs):  # [file:98]
        super().__init__(*args, **kwargs)  # [file:98]
        if not url:  # [file:98]
            raise ValueError("Pass -a url=<start_url>")  # [file:98]
        self.start_url = url  # [file:98]

    async def start(self):  # [file:98]
        yield Request(
            self.start_url,
            callback=self.parse_page,
            errback=self.errback,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_goto_options": {"wait_until": "networkidle", "timeout": 90000},
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "body", state="attached", timeout=90000),
                    PageMethod("wait_for_load_state", "networkidle"),
                ],
            },
        )  # [file:98]

    async def parse_page(self, response):  # [file:98]
        page = response.meta.get("playwright_page")  # [file:98]
        try:
            soup = BeautifulSoup(response.text, "lxml")  # [file:98]
            vis_texts = list(_iter_visible_text(soup))  # [file:98]
            socials, s_notes = _extract_socials(soup, response.url)  # [file:98]
            emails, e_notes = _extract_emails(soup, vis_texts)  # [file:98]
            phones, p_notes = _extract_phones(soup, vis_texts)  # [file:98]
            name_cands = _extract_name_candidates(soup, vis_texts, emails)  # [file:98]

            notes = {
                "social_notes": s_notes[:50],
                "email_notes": e_notes[:50],
                "phone_notes": p_notes[:50],
                "visibility_filter": "ignored script/style/template/noscript/comments/aria-hidden/display:none inline",
                "url": response.url,
                "render_mode": "dom-only",
            }  # [file:98]

            yield {
                "url": response.url,
                "socials": socials,
                "emails": emails,
                "phones": phones,
                "name_candidates": name_cands,
                "notes": notes,
            }  # [file:98]

            # Follow member/profile links (adjust pattern to site’s real structure)
            for a in soup.select("a[href]"):  # [file:98]
                href = a.get("href", "")  # [file:98]
                # Example heuristic; refine after Inspect → Copy selector
                if "/directory/" in href and ("profile" in href or "/member/" in href):
                    url_next = urljoin(response.url, href)  # [file:98]
                    yield Request(
                        url_next,
                        callback=self.parse_page,
                        errback=self.errback,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_goto_options": {"wait_until": "networkidle", "timeout": 90000},
                            "playwright_page_methods": [
                                PageMethod("wait_for_selector", "body", state="attached", timeout=90000),
                                PageMethod("wait_for_load_state", "networkidle"),
                            ],
                        },
                    )  # [file:98]

            # Follow pagination (adjust selector to the site)
            next_a = soup.select_one('a[rel="next"], a.pagination-next, a[aria-label="Next"]')  # [file:98]
            if next_a and next_a.get("href"):  # [file:98]
                next_url = urljoin(response.url, next_a["href"])  # [file:98]
                yield Request(
                    next_url,
                    callback=self.parse_page,
                    errback=self.errback,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_goto_options": {"wait_until": "networkidle", "timeout": 90000},
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "body", state="attached", timeout=90000),
                            PageMethod("wait_for_load_state", "networkidle"),
                        ],
                    },
                )  # [file:98]
        finally:
            if page:  # [file:98]
                await page.close()  # [file:98]

    async def errback(self, failure):  # [file:98]
        request = failure.request  # [file:98]
        self.logger.error(f"Failed: {request.url} -> {repr(failure)}")  # [file:98]