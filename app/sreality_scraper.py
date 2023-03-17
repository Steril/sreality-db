import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sqlite3
import datetime
import logging

logging.basicConfig(filename='/root/sreality-db/app/scraper.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

chrome_options = Options()
chrome_options.binary_location = "/usr/bin/chromium-browser"
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--remote-debugging-port=9222')

def create_property_listings_table():
    conn = sqlite3.connect('/root/sreality-db/sreality_db.sqlite3')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS property_listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price TEXT,
            location TEXT,
            size TEXT,
            description TEXT,
            url TEXT,
            date_scraped TEXT
        )
    """)

    conn.commit()
    conn.close()

def insert_property_listing(listing_data):
    conn = sqlite3.connect('/root/sreality-db/sreality_db.sqlite3')
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO property_listings (title, price, location, size, description, url, date_scraped)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, listing_data)

    conn.commit()
    conn.close()

def scrape_sreality(base_url):
    current_page = 1
    while True:
        logging.info(f"Scraping page {current_page}")
        url = f"{base_url}?strana={current_page}"
        
        response = send_get_request(url)
        if response is None:
            logging.error(f"Error scraping {url}: request failed")
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        property_listings = soup.find_all('div', class_='property')
        if not property_listings:
            logging.error(f"Error scraping {url}: no property listings found")
            break
        
        for property_div in property_listings:
            property_url = "https://www.sreality.cz" + property_div.find('a')['href']
            property_details = scrape_property_details(property_url)
            if property_details is not None:
                save_property_listing(property_details)
        
        next_page = soup.find('a', class_='next')
        if next_page is None:
            break
        
        current_page += 1


if __name__ == "__main__":
    logging.info("Starting scraper")
    create_property_listings_table()

    urls_to_scrape = [
        "https://www.sreality.cz/hledani/prodej/domy",
        "https://www.sreality.cz/hledani/prodej/byty"
    ]

    for url in urls_to_scrape:
        scrape_sreality(url)
    logging.info("Scraper finished")
