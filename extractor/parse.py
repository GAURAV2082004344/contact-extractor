import re
from bs4 import BeautifulSoup, Comment
from extractor.constants import SOCIAL_DOMAINS, EMAIL_REGEX, PHONE_REGEX, HIDE_INLINE_FLAGS
from extractor.normalize import clean_email, normalize_phone
from extractor.heuristics import title_case_name_candidates, email_hint_name, score_name

def _visible(el):
    if el.name in ("script","style","template"):
        return False
    if el.has_attr("aria-hidden") and str(el.get("aria-hidden","")).lower() == "true":
        return False
    if el.has_attr("style"):
        style = str(el.get("style","")).replace(" ", "").lower()
        if any(flag in style for flag in HIDE_INLINE_FLAGS):
            return False
    return True

def _iter_visible_text(soup):
    for el in soup.find_all(string=True):
        if isinstance(el, Comment):
            continue
        parent = el.parent
        if parent and _visible(parent):
            t = str(el).strip()
            if t:
                yield t

def _extract_socials(soup):
    socials, notes = [], []
    for a in soup.find_all("a", href=True):
        if not _visible(a):
            continue
        href = a.get("href","").strip()
        if any(dom in href for dom in SOCIAL_DOMAINS):
            label = a.get_text(" ", strip=True)
            socials.append({"href": href, "label": label})
            notes.append(f"social:{href}|label:{label[:50]}")
    return socials, notes

def _extract_emails(soup, vis_texts):
    emails, notes = set(), []
    for a in soup.find_all("a", href=True):
        if not _visible(a):
            continue
        href = a["href"]
        m = re.search(EMAIL_REGEX, href, re.IGNORECASE)
        if m:
            emails.add(clean_email(m.group(1)))
            notes.append(f"mailto:{href}")
    for t in vis_texts:
        for m in re.finditer(EMAIL_REGEX, t, re.IGNORECASE):
            emails.add(clean_email(m.group(1)))
    return sorted(emails), notes

def _extract_phones(soup, vis_texts):
    phones, notes = set(), []
    for a in soup.find_all("a", href=True):
        if not _visible(a):
            continue
        href = a["href"]
        m = re.search(PHONE_REGEX, href)
        if m:
            orig = m.group(1)
            phones.add((orig.strip(), normalize_phone(orig)))
            notes.append(f"tel:{href}")
    for t in vis_texts:
        for m in re.finditer(PHONE_REGEX, t):
            orig = m.group(1)
            phones.add((orig.strip(), normalize_phone(orig)))

    # Build list and deduplicate by normalized (fallback to original)
    out = [{"original": o, "normalized": n} for (o, n) in sorted(phones)]
    seen = set()
    dedup = []
    for item in out:
        key = item.get("normalized") or item.get("original")
        if key and key not in seen:
            seen.add(key)
            dedup.append(item)
    return dedup, notes

def _extract_name_candidates(soup, vis_texts, emails):
    cands = []
    likely_blocks = []
    for sel in ["h1","h2","h3",".author",".person",".profile",".about",".contact"]:
        likely_blocks += soup.select(sel)
    texts = [x.get_text(" ", strip=True) for x in likely_blocks if _visible(x)]
    texts += list(vis_texts)
    title_case = set(title_case_name_candidates(texts))
    for e in emails:
        local = e.split("@",1)[0]
        hint = email_hint_name(local)
        if hint:
            title_case.add(hint)
    nearby = " ".join(texts[:200])[:2000]
    scored = [{"name": n, "confidence": score_name(n, nearby)} for n in title_case]
    scored.sort(key=lambda x: x["confidence"], reverse=True)
    return scored[:5]

def extract_all(html: str, final_url: str):
    soup = BeautifulSoup(html, "lxml")
    vis_texts = list(_iter_visible_text(soup))
    socials, s_notes = _extract_socials(soup)
    emails, e_notes = _extract_emails(soup, vis_texts)
    phones, p_notes = _extract_phones(soup, vis_texts)
    name_cands = _extract_name_candidates(soup, vis_texts, emails)
    notes = {
        "social_notes": s_notes[:50],
        "email_notes": e_notes[:50],
        "phone_notes": p_notes[:50],
        "visibility_filter": "ignored script/style/template/comments/aria-hidden/display:none inline",
        "url": final_url
    }
    return {
        "url": final_url,
        "socials": socials,
        "emails": emails,
        "phones": phones,
        "name_candidates": name_cands,
        "notes": notes
    }
