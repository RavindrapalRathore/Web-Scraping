import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv

def scroll_to_element(driver, class_name):
    target_element = WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

    driver.execute_script("arguments[0].scrollIntoView();", target_element)

def scrape_product_page(product_url):
    # Initialize Chrome WebDriver
    driver = webdriver.Chrome()
    driver.get(product_url)

    try:
        scroll_to_element(driver, 'pdp-productDescriptorsContainer')
        time.sleep(1)

    except Exception as e:
        print("Error:", e)
        driver.quit()
        return None


    soup = BeautifulSoup(driver.page_source, 'html.parser')

    product_data = {}

    brand_tag = soup.find('h1', class_="pdp-title")
    product_data['Brand'] = brand_tag.text if brand_tag else None
    product_name_tag = soup.find('h1', class_='pdp-name')
    product_data['Product Title'] = product_name_tag.text if product_name_tag else None

    product_link = soup.find('a', {'data-refreshpage': 'true', 'target': '_blank'})
    product_data['Product Link'] = 'http://myntra.com/' + product_link['href'] if product_link else None

    MRP_tag = soup.find('span', class_="pdp-mrp")
    MRP_text = MRP_tag.text.strip('Rs. ') if MRP_tag else None
    MRP_value = None
    if MRP_text:
        MRP_digits = ''.join(filter(str.isdigit, MRP_text))
        if MRP_digits:
            MRP_value = int(MRP_digits)
    product_data['MRP'] = MRP_value

    selling_price_tag = soup.find('span', class_='pdp-price')
    selling_price_text = selling_price_tag.text.strip('₹') if selling_price_tag else None
    selling_price_value = int(''.join(filter(str.isdigit, selling_price_text))) if selling_price_text else None
    product_data['Selling Price'] = selling_price_value

    ratings_count_tag = soup.find('div', class_='index-ratingsCount')
    ratings_count_text = ratings_count_tag.text if ratings_count_tag else None
    ratings_count = int(''.join(filter(str.isdigit, ratings_count_text))) if ratings_count_text else None
    product_data['Number of Rating'] = ratings_count

    stars_tag = soup.find('div', class_='index-overallRating')
    stars_text = stars_tag.find('div').text if stars_tag else None
    stars = float(stars_text) if stars_text else None
    product_data['Star Rating'] = stars

    description_tag = soup.find('div', class_='pdp-productDescriptorsContainer')
    description_text = description_tag.get_text(separator=' ') if description_tag else None

    description_cleaned = description_text.replace('"', '')
    product_data['description'] = description_cleaned

    image_containers = soup.find_all('div', class_='image-grid-image')
    image_urls = [container['style'].split('"')[1] for container in image_containers]
    product_data['Link of the Images'] = image_urls
    product_data['Number of Images'] = len(image_urls)

    comment_tags = soup.find_all('div', class_='user-review-reviewTextWrapper')
    comments = [tag.text.strip() for tag in comment_tags] if comment_tags else None
    product_data['List of comments'] = comments

    seller_tag = soup.find('span', class_='supplier-productSellerName')
    product_data['Seller Name'] = seller_tag.text if seller_tag else None

    driver.quit()

    return product_data

def scrape_single_myntra_product(product_url):
    product_data = scrape_product_page(product_url)
    return product_data


def save_to_csv(data_list, filename):
    keys = data_list[0].keys() if data_list else []
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for data in data_list:
            writer.writerow(data)

if __name__ == "__main__":
    base_url = "https://www.myntra.com/kids?f=Categories%3AShorts%3A%3AGender%3Aboys%2Cboys%20girls&p="
    num_pages = 11
    product_urls = []


    driver = webdriver.Chrome()

    for page_num in range(1, num_pages + 1):
        page_url = base_url + str(page_num)
        driver.get(page_url)

        # Scroll to the bottom to load more products
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        li_elements = soup.find_all('li', class_="product-base")
        for li in li_elements:
            a_elements = li.find_all('a', {'data-refreshpage': 'true', 'target': '_blank'})
            for a in a_elements:
                href = 'http://myntra.com/' + a['href']
                product_urls.append(href)

    driver.quit()

    scraped_data = []
    for url in product_urls:
        data = scrape_single_myntra_product(url)
        if data:
            scraped_data.append(data)
            print(data)

    save_to_csv(scraped_data, 'myntra_products.csv')
    print("Scraped data saved to myntra_products.csv")
