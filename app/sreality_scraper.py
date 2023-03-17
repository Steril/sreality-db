import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sqlite3
import datetime
import logging

logging.basicConfig(filename='/root/sreality-db/app/scraper.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

chrome_options = Options()
chrome_options.binary_location = "/usr/bin/chromium-browser"
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--remote-debugging-port=9222')

def insert_property_listing(listing_data):
    conn = sqlite3.connect('/root/sreality-db/sreality_db.sqlite3')
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO property_listings (title, price, location, size, description, url, date_scraped)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, listing_data)

    conn.commit()
    conn.close()

def scrape_sreality(url):
    listings_saved = 0
    logging.info(f"Started scraping {url}")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, 'lxml')
        driver.quit()

        property_listings = soup.find_all('div', class_='tile')

        for listing in property_listings:
            title = listing.find('div', class_='tile-title').text.strip()
            price = listing.find('span', class_='price').text.strip()
            location = listing.find('div', class_='tile-address').text.strip()
            size = listing.find('div', class_='tile-desc').text.strip()
            description = listing.find('div', class_='tile-text').text.strip()
            url = "https://www.sreality.cz" + listing.find('a')['href']
            date_scraped = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            listing_data = (title, price, location, size, description, url, date_scraped)
            insert_property_listing(listing_data)
            listings_saved += 1

        logging.info(f"{listings_saved} property listings saved to the database")
        logging.info(f"Finished scraping {url}")

    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")

if __name__ == "__main__":
    urls_to_scrape = [
        "https://www.sreality.cz/hledani/prodej/domy",
        "https://www.sreality.cz/hledani/prodej/byty"
    ]

    for url in urls_to_scrape:
        scrape_sreality(url)
