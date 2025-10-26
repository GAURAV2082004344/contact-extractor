Title: Contact Extractor (Scrapy + Playwright)



Overview: Scrapes directory cards on the first page to extract name, emails, phones; uses Playwright to select basic filters when the page initially shows “We were not able to find the results.”​



Requirements:



python -m venv .venv



.venv\\Scripts\\pip install -r requirements.txt



.venv\\Scripts\\python -m playwright install chromium



Run:



Put target URLs in urls.txt (one per line).



.venv\\Scripts\\python -m scrapy crawl contacts -a url\_file=urls.txt -s ROBOTSTXT\_OBEY=False -s CONCURRENT\_REQUESTS=2 -s PLAYWRIGHT\_MAX\_CONTEXTS=1 -s PLAYWRIGHT\_MAX\_PAGES\_PER\_CONTEXT\_RIGHT=1 -O results/run.json



Verifying selectors (Scrapy shell):



scrapy shell "https://www.libf.co/directory/libf-2025"



At >>>:



len(response.css("body > main > section > div.py-12 > div > div.mt-5 > div"))



response.css("body > main > section > div.py-12 > div > div.mt-5 ::text").re\_first(r"We were not able to find the results")​



Outputs:



results/ contains JSON lines with url, name\_candidates, emails, phones, socials, notes.

