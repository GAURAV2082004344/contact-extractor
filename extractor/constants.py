import httpx, chardet, time
from typing import Tuple, Optional

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

SOCIAL_DOMAINS = [
    "linkedin.com", "facebook.com", "instagram.com",
    "twitter.com", "x.com", "youtube.com", "github.com",
    "behance.net", "t.me", "wa.me"
]
EMAIL_REGEX = r"(?:mailto:)?([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
PHONE_REGEX = r"(?:tel:)?(\+?\d[\d\s().-]{6,}\d)"
HIDE_INLINE_FLAGS = ["display:none"]


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
