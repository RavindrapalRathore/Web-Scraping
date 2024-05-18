import scrapy
import json
from scrapy.crawler import CrawlerProcess

class MenuSpider(scrapy.Spider):
    name = 'menu_spider'
    start_urls = ['https://www.livemint.com']

    def start_requests(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        # Find the main menu bar
        main_menu = response.css('nav.nav_NewNav__lab3q')

        # Initialize a dictionary to store menu items
        menu_dict = {}

        # Find all menu items
        menu_items = main_menu.css('a')

        # Extract URLs and names and populate the menu dictionary
        explore_mint_found = False
        for item in menu_items:
            href = item.attrib.get('href', '').strip()
            text = item.css('::text').get().strip()
            if href != "#" and text != "e-paper":
                if not explore_mint_found:
                    menu_dict[text] = href
                    if text == "Explore Mint":
                        explore_mint_found = True
                else:
                    # Stop adding items after "Explore Mint"
                    break

        # Remove menu items without URLs
        menu_dict = {k: v for k, v in menu_dict.items() if v}

        # Write the menu dictionary to a JSON file
        with open('menu.json', 'w') as f:
            json.dump(menu_dict, f, indent=4)  # indent=4 adds indentation for better readability
            f.write('\n')  # Add a line break after writing the JSON data

        yield {
            'menu': menu_dict
        }


process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'output.json',
    'DOWNLOAD_DELAY': 2,
    'RETRY_TIMES': 5,
    'RETRY_HTTP_CODES': [403],
    'DEFAULT_REQUEST_HEADERS': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
})

crawler = process.create_crawler(MenuSpider)

# Start the crawler
process.crawl(crawler)
process.start()
