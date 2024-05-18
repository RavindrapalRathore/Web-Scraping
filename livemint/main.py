import scrapy
import re
import json
import csv
from scrapy.crawler import CrawlerProcess

class LivemintSpider(scrapy.Spider):
    name = 'livemint'

    def __init__(self):
        super().__init__()
        self.start_urls = self.get_start_urls_from_json()

    def get_start_urls_from_json(self):
        # Read URLs from the JSON file named 'menu'
        with open('menu.json', 'r') as f:
            urls = json.load(f)
        return list(urls.values())  # Extracting just the URLs

    def start_requests(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        article_links = response.css('div.listtostory div.thumbnail a.imgSec::attr(href)').getall()
        for article_link in article_links:
            yield scrapy.Request(response.urljoin(article_link), callback=self.parse_article)

        # Extract and follow pagination links
        next_page = response.css('link[rel="next"]::attr(href)').get()
        if next_page and self.is_valid_page(next_page):  # Check if the next page is valid
            yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        if response.css('h1.headline'):
            title = response.css('h1.headline::text').get(default="Title not found").strip()
        else:
            title = response.css('h1::text').get(default="Title not found").strip()
        author, author_url = self.extract_author_and_url(response)

        date_span = response.css('span.metaDate')
        if date_span:
            date = date_span.css('span::attr(data-expandedtime)').get(default=None)
        else:
            date = response.css('span.newTimeStamp::attr(data-expandedtime)').get(default=None)

        date = date.strip() if date else None
        main_area = response.css('div.mainArea')
        article_content = " ".join(main_area.css('p::text').getall()) if main_area else ""
        article_content = self.clean_text(article_content)
        article_url = response.url

        yield {
            "Article URL": article_url,
            "Title": title,
            "Author Name": author,
            "Author URL": author_url.strip() if author_url else "Author URL not found",
            "Article Content": article_content.strip(),
            "Published Date": date.strip() if date else None,
        }

    def extract_author_and_url(self, response):
        if response.css('span.articleInfo'):
            author = response.css('span.articleInfo.author a::text').get(default="Author not found").strip()
            author_url = response.css('span.articleInfo.author a::attr(href)').get(default=None)
        elif response.css('span.premiumarticleInfo'):
            author = response.css('span.premiumarticleInfo a::text').get(default="Author not found").strip()
            author_url = response.css('span.premiumarticleInfo a::attr(href)').get(default=None)
            if author_url:
                author_url = 'https://www.livemint.com' + author_url
        else:
            author = "Author not found"
            author_url = ""

        return author, author_url

    def clean_text(self, text):
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = re.sub(r'[\n\t\\]', ' ', clean_text)
        clean_text = re.sub(r',', ' -', clean_text)
        clean_text = re.sub(r'"', "'", clean_text)
        clean_text = re.sub(r"’", "'", clean_text)
        clean_text = re.sub(r"‘", "'", clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text

    def is_valid_page(self, url):
        return re.search(r'/page-(\d+)/?$', url) and int(re.search(r'/page-(\d+)/?$', url).group(1)) <= 5


process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'output.json',
    'DOWNLOAD_DELAY': 1,
    'RETRY_TIMES': 5,
    'RETRY_HTTP_CODES': [403],
    'DEFAULT_REQUEST_HEADERS': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
})

# Define a list to collect all items
articles = []

# Define a function to collect items
def collect_items(item, response, spider):
    articles.append(item)

# Attach the callback function to the spider's item scraped signal
crawler = process.create_crawler(LivemintSpider)
crawler.signals.connect(collect_items, signal=scrapy.signals.item_scraped)

# Start the crawler
process.crawl(crawler)
process.start()

# Write all articles to the output JSON file with newline character after each dictionary
with open('output.json', 'w', encoding='utf-8') as f:
    for article in articles:
        json.dump(article, f, ensure_ascii=False, indent=4)
        f.write('\n')

