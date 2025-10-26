import argparse, json, pathlib
from extractor.fetch import fetch_html
from extractor.parse import extract_all
from extractor.io_utils import read_urls, write_csv

def process(urls, json_out, csv_out):
    results = []
    for url in urls:
        html, final_url, notes_fetch = fetch_html(url)
        if not html:
            results.append({
                "url": url,
                "socials": [],
                "emails": [],
                "phones": [],
                "name_candidates": [],
                "notes": {"fetch": notes_fetch or "failed"}
            })
            continue
        record = extract_all(html, final_url)
        record["url"] = final_url or url
        results.append(record)

    if json_out:
        pathlib.Path(json_out).parent.mkdir(parents=True, exist_ok=True)
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    if csv_out:
        write_csv(results, csv_out)

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--url", type=str)
    g.add_argument("--url-file", type=str)
    ap.add_argument("--out", type=str, help="JSON output path")
    ap.add_argument("--csv", type=str, help="CSV output path")
    args = ap.parse_args()

    urls = [args.url] if args.url else read_urls(args.url_file)
    process(urls, args.out, args.csv)

if __name__ == "__main__":
    main()
