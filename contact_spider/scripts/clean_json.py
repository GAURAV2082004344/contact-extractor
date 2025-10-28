import sys, json  # [file:98]

def clean_item(it):  # [file:98]
    out = {"url": it.get("url")}  # [file:98]
    # socials: dedupe by href and keep label  # [file:98]
    seen = set(); socials = []  # [file:98]
    for s in it.get("socials", []) or []:  # [file:98]
        if isinstance(s, dict):
            href = (s.get("href") or "").strip()
            label = s.get("label") or ""
        else:
            href, label = (s or "").strip(), ""
        if href and href not in seen:
            seen.add(href)
            socials.append({"href": href, "label": label})
    if socials:
        out["socials"] = socials
    # emails: normalize lowercase + dedupe  # [file:98]
    emails = sorted({(e or "").strip().lower() for e in (it.get("emails") or []) if e})
    if emails:
        out["emails"] = emails
    # phones: dedupe by normalized (fallback original)  # [file:98]
    seenp, phones_out = set(), []
    for p in it.get("phones") or []:
        if isinstance(p, dict):
            norm = p.get("normalized") or p.get("original")
            orig = p.get("original") or norm
            if norm and norm not in seenp:
                seenp.add(norm)
                phones_out.append({"original": orig, "normalized": norm})
        elif p and p not in seenp:
            seenp.add(p)
            phones_out.append({"original": p, "normalized": p})
    if phones_out:
        out["phones"] = phones_out
    # names: keep best by confidence, top 5  # [file:98]
    uniq = {}
    for n in it.get("name_candidates") or []:
        if isinstance(n, dict):
            nm = (n.get("name") or "").strip()
            cf = float(n.get("confidence", 0.0))
        else:
            nm, cf = str(n).strip(), 0.0
        if nm and (nm not in uniq or cf > uniq[nm]):
            uniq[nm] = cf
    if uniq:
        out["name_candidates"] = sorted(
            [{"name": k, "confidence": v} for k, v in uniq.items()],
            key=lambda x: x["confidence"], reverse=True,
        )[:5]
    return out  # [file:98]

def main(inp, outp):  # [file:98]
    with open(inp, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    cleaned = [clean_item(it) for it in data]
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":  # [file:98]
    if len(sys.argv) < 3:
        print("Usage: python contact_spider\\scripts\\clean_json.py <input.json> <output.json>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
