import scrapy
from scrapy.crawler import CrawlerProcess
import time
import logging

class MoviesModSpider(scrapy.Spider):
    name = 'moviesmodspider'
    base_url = 'https://moviesmod.info/'

    def start_requests(self):
        # Set the number of pages you want to scrape
        num_pages = 724  # Example: Scraping first 5 pages

        for page_num in range(1, num_pages + 1):
            url = f'{self.base_url}page/{page_num}/'
            yield scrapy.Request(url=url, callback=self.parse_listing)

    def parse_listing(self, response):
        # Extract movie URLs using the provided class
        movie_urls = response.css('a.post-image::attr(href)').getall()

        # Follow each movie URL and call parse_detail for each
        for movie_url in movie_urls:
            yield scrapy.Request(url=movie_url, callback=self.parse_detail, cb_kwargs={'movie_url': movie_url})

    def parse_detail(self, response, movie_url):
        # Extracting movie title
        title = response.css('div.imdbwp__header span.imdbwp__title::text').get()
        imdb_meta = response.css('.imdbwp__meta span::text').getall()
        year = imdb_meta[-1].strip() if imdb_meta else None
        genre = imdb_meta[-2].strip() if len(imdb_meta) >= 2 else None
        # Extracting movie details
        details = {}
        for li in response.css('ul li'):
            strong_text = li.css('strong::text').get()
            if strong_text:
                key = strong_text.replace(':', '').strip()
                value = li.xpath('text()').getall()
                value = ' '.join(value).strip()
                details[key] = value

        # Log extracted data for debugging
        logging.info(f"Scraped movie: {title}, URL: {movie_url}")

        # Extracting movie rating
        rating = response.css('span.imdbwp__star::text').get()

        # Extracting movie poster URL
        poster_url = response.css('img.imdbwp__img::attr(src)').get()

        # Extracting storyline
        storyline = response.css('h2:contains("Storyline") + p::text').get()

        # Extract alternate images
        alternate_images = response.css('p img::attr(src)').getall()

        yield {
            'title': title,
            'movie_url': movie_url,
            'poster_url': response.urljoin(poster_url),
            'year': year,
            'genre': genre,
            'rating': rating,
            'full_name': details.get('Full Name', ''),
            'released': details.get('Released', ''),
            'duration': details.get('Duration', ''),
            'language': details.get('Language', ''),
            'subtitle': details.get('Subtitle', ''),
            'size': details.get('Size', ''),
            'quality': details.get('Quality', ''),
            'format': details.get('Format', ''),
            'storyline': storyline,
            'alternate_images': alternate_images,
        }

# Configure CSV feed with 'overwrite' set to True
process = CrawlerProcess(settings={
    'FEEDS': {
        'moviesmod_output.csv': {
            'format': 'csv',
            'overwrite': True,
        },
    },
    'LOG_LEVEL': 'DEBUG',  # Add debug logging
})

# Add your spider to the process
process.crawl(MoviesModSpider)

# Start the crawling process
process.start()

# Wait for 5 seconds to allow the file to be written completely
time.sleep(5)
