import csv, pathlib

def read_urls(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def write_csv(records, path):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in records:
        socials_joined = ";".join([s.get("href","") for s in r.get("socials",[]) if s.get("href")])
        emails_joined = ";".join(r.get("emails",[]))
        phones_list = [p.get("normalized") or p.get("original") for p in r.get("phones",[])]
        phones_joined = ";".join(sorted(set(filter(None, phones_list))))
        top = (r.get("name_candidates") or [{}])[0]
        rows.append({
            "url": r.get("url",""),
            "socials": socials_joined,
            "emails": emails_joined,
            "phones": phones_joined,
            "top_name": top.get("name",""),
            "top_conf": top.get("confidence",""),
        })

    fieldnames = ["url","socials","emails","phones","top_name","top_conf"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)

import csv, pathlib

def read_urls(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def write_csv(records, path):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in records:
        socials_joined = ";".join([s.get("href","") for s in r.get("socials",[]) if s.get("href")])
        emails_joined = ";".join(r.get("emails",[]))
        phones_list = [p.get("normalized") or p.get("original") for p in r.get("phones",[])]
        phones_joined = ";".join(sorted(set(filter(None, phones_list))))
        top = (r.get("name_candidates") or [{}])[0]
        rows.append({
            "url": r.get("url",""),
            "socials": socials_joined,
            "emails": emails_joined,
            "phones": phones_joined,
            "top_name": top.get("name",""),
            "top_conf": top.get("confidence",""),
        })
    fieldnames = ["url","socials","emails","phones","top_name","top_conf"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)
