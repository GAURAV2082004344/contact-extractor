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
