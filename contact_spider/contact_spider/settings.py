# Scrapy settings for contact_spider

BOT_NAME = "contact_spider"

SPIDER_MODULES = ["contact_spider.spiders"]
NEWSPIDER_MODULE = "contact_spider.spiders"

# Respect robots.txt (set False if you need to ignore for testing)
ROBOTSTXT_OBEY = True

# Your installed scrapy-playwright package provides a download handler (handler.py),
# not a downloader middleware. Enable it for http/https.
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# Reactor recommended by Scrapy 2.13 for asyncio
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Playwright configuration
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
}

# Optional: stable headers
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# New 3-arg signature for header processing; keep headers unchanged
def process_headers(browser_type_name: str, playwright_request, scrapy_request_data: dict):
    return scrapy_request_data["headers"]

PLAYWRIGHT_PROCESS_REQUEST_HEADERS = process_headers

# Concurrency and timeouts
CONCURRENT_REQUESTS = 8
DOWNLOAD_TIMEOUT = 30
RETRY_TIMES = 2

# Minimal extensions and encoding
EXTENSIONS = {"scrapy.extensions.corestats.CoreStats": 0}
FEED_EXPORT_ENCODING = "utf-8"
