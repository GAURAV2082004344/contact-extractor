Limitations:



First-page only; no pagination implemented by design.​



Filter control selectors may need adjustment per site; interaction relies on select\[name='sector'] and select\[name='country'] plus a Search/Apply button.​



Assumptions:



Each card has an h5 title and mailto/tel anchors; regex over card text is used to catch additional contacts.​



Improvements:



Add pagination and infinite-scroll handling; dedupe items by canonical URL.​



Add precision rules to suppress footer/boilerplate contacts using proximity to the title or container scoping.​



Repro:



Use Scrapy shell checks to ensure the page isn’t in the empty state (count > 1 and no empty-state text) before long runs.​



Step 5 — Optional: add sample results



Copy your working item(s) into results/sample\_libf\_2025.json. Keep only public-contact fields that appear in-page.

