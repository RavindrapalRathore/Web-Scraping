
import scrapy
from scrapy.crawler import CrawlerProcess

class ListingSpider(scrapy.Spider):
    name = 'listingspider'
    start_urls = ['http://books.toscrape.com/']

    def parse(self, response):
        # Extract product URLs from the listing page using XPath
        product_urls = response.xpath('//h3/a/@href').extract()

        # Follow each product URL to gather detailed information
        for product_url in product_urls:
            yield scrapy.Request(url=response.urljoin(product_url), callback=self.parse_product)

        # Follow pagination links
        next_page = response.xpath('//li[@class="next"]/a/@href').extract_first()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)

    def parse_product(self, response):
        # Extract detailed information from the product page using XPath
        name = response.xpath('//h1/text()').get()
        price = response.xpath('//p[@class="price_color"]/text()').get()
        warning_text = response.xpath('//div[@class="alert alert-warning"]/text()').get()
        img_src = response.xpath('//div[@class="carousel-inner"]/div[@class="item active"]/img/@src').get()
        yield {
            'name': name,
            'price': price,
            'url': response.url,
            'warning_text': warning_text,
            'img_src': img_src,
        }

# Configure the CSV feed and set 'overwrite' to True
process = CrawlerProcess(settings={
    'FEEDS': {
        'output.csv': {
            'format': 'csv',
            'overwrite': True,  # Set to True to overwrite the file if it exists
        },
    },
    'LOG_LEVEL': 'DEBUG',  # Add debug logging
})

# Add your spiders to the process
process.crawl(ListingSpider)

# Start the crawling process
process.start()

