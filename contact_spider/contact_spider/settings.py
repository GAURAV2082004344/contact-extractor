# Scrapy settings for contact_spider (DOM-only extractor with Playwright)  [file:98]

BOT_NAME = "contact_spider"  # [file:98]

SPIDER_MODULES = ["contact_spider.spiders"]  # [file:98]
NEWSPIDER_MODULE = "contact_spider.spiders"  # [file:98]

ROBOTSTXT_OBEY = True  # [file:98]

# Enable scrapy-playwright handler for JS pages  # [file:98]
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}  # [file:98]

# Asyncio reactor for Scrapy 2.13+  # [file:98]
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"  # [file:98]

# Playwright defaults tuned for SPAs (no API usage; DOM-only extraction)  # [file:98]
PLAYWRIGHT_BROWSER_TYPE = "chromium"  # [file:98]
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}  # [file:98]
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 90000  # [file:98]
PLAYWRIGHT_PAGE_GOTO_OPTIONS = {"wait_until": "networkidle"}  # [file:98]

# Stable headers  # [file:98]
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}  # [file:98]

# 3-arg header processor (Scrapy 2.13)  # [file:98]
def process_headers(browser_type_name: str, playwright_request, scrapy_request_data: dict):
    return scrapy_request_data["headers"]  # [file:98]

PLAYWRIGHT_PROCESS_REQUEST_HEADERS = process_headers  # [file:98]

# Concurrency/timeouts  # [file:98]
CONCURRENT_REQUESTS = 8  # [file:98]
DOWNLOAD_TIMEOUT = 90  # [file:98]
RETRY_TIMES = 2  # [file:98]

FEED_EXPORT_ENCODING = "utf-8"  # [file:98]
