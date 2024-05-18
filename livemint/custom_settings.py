custom_settings = {
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        'livemint.middlewares.CustomRetryMiddleware': 543,
    },
    'RETRY_TIMES': 5,  # Number of retries
    'RETRY_HTTP_CODES': [403],  # Retry only for 403 responses
    'DEFAULT_REQUEST_HEADERS': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
}
