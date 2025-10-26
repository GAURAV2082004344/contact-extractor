🚀 About Contact Extractor
It is a Python scraper that extracts name, emails, and phone numbers from directory cards on the first results page, using Playwright to interact with filters when the page initially shows no results.

💡 How it works

Loads each target directory URL, dismisses cookie banners, selects non-empty options for sector/country, optionally clicks a Search/Apply button, and scrolls to trigger lazy loading.

Once cards are visible, it parses inline tiles under the grid and extracts h5 titles, mailto/tel anchors, and additional contacts via regex from the card text.

✨ Features

First-page card scraping with grid-scoped selectors to avoid footer/global noise.

Optional Playwright-based filter interaction for empty-state pages that require a search trigger.

Email and phone extraction with regex, plus de-duplication of candidates.

Simple CLI usage with URLs provided in a urls.txt file.​

⚙️ Installation

Create and activate a virtual environment:

python -m venv .venv​

.venv\Scripts\Activate.ps1​

Install dependencies and browser:

pip install -r requirements.txt​

python -m playwright install chromium​

📁 Project layout

contact_spider/spiders/contacts.py — the spider (if inside a Scrapy project) OR contact_spider/contact_spider/spiders/contacts.py if using runspider.​

urls.txt — one URL per line for target directories.​

results/ — outputs such as run.json.​

README.md, NOTES.md — docs and limitations.​

♨️ Usage
A. Run without a Scrapy project (single-file mode)

From the repo root:

.venv\Scripts\python -m scrapy runspider contact_spider\contact_spider\spiders\contacts.py -a url_file=urls.txt -s ROBOTSTXT_OBEY=False -s CONCURRENT_REQUESTS=2 -s PLAYWRIGHT_MAX_CONTEXTS=1 -s PLAYWRIGHT_MAX_PAGES_PER_CONTEXT=1 -O results\run.json​

B. Run inside a Scrapy project (optional)

Initialize once:

.venv\Scripts\python -m scrapy startproject contact_spider .​

Move spider to contact_spider\spiders\contacts.py, then:

Crawl:

.venv\Scripts\python -m scrapy crawl contacts -a url_file=urls.txt -s ROBOTSTXT_OBEY=False -s CONCURRENT_REQUESTS=2 -s PLAYWRIGHT_MAX_CONTEXTS=1 -s PLAYWRIGHT_MAX_PAGES_PER_CONTEXT=1 -O results\run.json​

🔎 Verifying selectors (Scrapy shell)

Launch:

scrapy shell "YOUR_RESULTS_URL"​

At >>>:

len(response.css("body > main > section > div.py-12 > div > div.mt-5 > div")) # should be > 1 when cards exist

response.css("body > main > section > div.py-12 > div > div.mt-5 ::text").re_first(r"We were not able to find the results") # should be None when populated

🧪 Example command

.venv\Scripts\python -m scrapy runspider contact_spider\contact_spider\spiders\contacts.py -a url_file=urls.txt -O results\run.json​

📦 Sample output format (JSON line)

{"url":"https://example.com/directory","profile_in_page":true,"name_candidates":["Jane Doe"],"emails":["jane@example.com"],"phones":["+1 555 123 4567"],"socials":[],"notes":{}}

⚠️ Limitations

First-page only by design; pagination and infinite scroll are not enabled.

Filter selectors for sector/country and the Search/Apply button may need to be adjusted per site.

💡 Improvements

Add pagination/infinite scroll with scrolling loops and state deduplication.

Improve precision via proximity scoring to the h5 (e.g., only capture emails/phones within each card container).

🧰 Tips

If the page shows “We were not able to find the results,” adjust the Playwright selectors in contacts.py to match the actual sector/country controls, and click the correct Search/Apply button.

To commit run outputs despite .gitignore, either use git add -f results\run.json or add a negate rule !results/run.json to .gitignore.​

📖 Resources

Scrapy shell and tutorial references for quick selector checks and project scaffolding.​

Scrapy command-line notes for runspider vs crawl usage.
