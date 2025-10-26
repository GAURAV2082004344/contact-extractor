import httpx, chardet, time
from typing import Tuple, Optional

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def fetch_html(url: str, timeout: float = 20.0, retries: int = 2) -> Tuple[Optional[str], str, str]:
    last_err = ""
    final_url = url
    for attempt in range(retries + 1):
        try:
            with httpx.Client(follow_redirects=True, headers={"User-Agent": UA}) as client:
                r = client.get(url, timeout=timeout)
                final_url = str(r.url)
                raw = r.content
                enc = r.encoding
                if not enc:
                    det = chardet.detect(raw)
                    enc = det.get("encoding") or "utf-8"
                text = raw.decode(enc, errors="replace")
                return text, final_url, f"status={r.status_code}, encoding={enc}"
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    return None, final_url, last_err


import re
from rapidfuzz import fuzz

TITLES = {"ceo","founder","director","co-founder","principal","owner","managing director","head"}
STOP = {"the","and","of","for","in","at","with","from","by"}

def title_case_name_candidates(texts):
    cands = []
    for t in texts:
        t = t.strip()
        if not t:
            continue
        tokens = [w for w in re.split(r"[\s\u00A0]+", t) if w]
        if 2 <= len(tokens) <= 3 and all(x[0:1].isupper() for x in tokens if x.isalpha()):
            if not any(w.lower() in STOP for w in tokens):
                cands.append(" ".join(tokens))
    return cands

def email_hint_name(email_local):
    parts = re.split(r"[._-]+", email_local)
    parts = [p for p in parts if p and p.isalpha()]
    if 2 <= len(parts) <= 3:
        return " ".join(w.capitalize() for w in parts)
    return None

def score_name(name, nearby_text):
    score = 50
    if any(t in nearby_text.lower() for t in TITLES):
        score += 15
    pieces = [p for p in re.split(r"\s+", name) if p]
    for p in pieces:
        if p and fuzz.partial_ratio(p.lower(), nearby_text.lower()) > 85:
            score += 5
    return min(score, 95)

STOP = {"the","and","of","for","in","at","with","from","by"}
WEEKDAY_TOKENS = {"monday","tuesday","wednesday","thursday","friday","saturday","sunday","mon","tue","wed","thu","fri","sat","sun"}
MONTH_TOKENS = {"jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec",
                "january","february","march","april","june","july","august","september","october","november","december"}

def _has_calendar_words(s: str) -> bool:
    low = s.lower()
    return any(w in low for w in WEEKDAY_TOKENS | MONTH_TOKENS)

def title_case_name_candidates(texts):
    cands = []
    for t in texts:
        t = t.strip()
        if not t or _has_calendar_words(t):
            continue
        tokens = [w for w in re.split(r"[\s\u00A0]+", t) if w]
        if 2 <= len(tokens) <= 3 and all(x[0:1].isupper() for x in tokens if x.isalpha()):
            if not any(w.lower() in STOP for w in tokens):
                cands.append(" ".join(tokens))
    return cands


NAV_FOOTER_LABELS = {"contact us","reach us","reach us via","other sites","quick links","working hours","about us","privacy policy","terms","faq","help","support"}
def _is_all_caps(s: str) -> bool:
    letters = [c for c in s if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)

def _has_digits(s: str) -> bool:
    return any(c.isdigit() for c in s)

def title_case_name_candidates(texts):
    cands = []
    for t in texts:
        t = t.strip()
        if not t or _has_calendar_words(t):
            continue
        low = t.lower()
        if low in NAV_FOOTER_LABELS or _is_all_caps(t) or _has_digits(t):
            continue
        tokens = [w for w in re.split(r"[\s\u00A0]+", t) if w]
        if 2 <= len(tokens) <= 3 and all(x[0:1].isupper() for x in tokens if x.isalpha()):
            if not any(w.lower() in STOP for w in tokens):
                cands.append(" ".join(tokens))
    return cands
