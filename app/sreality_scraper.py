import requests
from bs4 import BeautifulSoup
import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_sreality(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        property_listings = []

        for listing in soup.find_all('div', class_='property'):
            try:
                title = listing.find('div', class_='property__name').get_text(strip=True)
                price = listing.find('span', class_='property__price').get_text(strip=True)
                location = listing.find('div', class_='property__location').get_text(strip=True)

                property_listings.append({
                    'title': title,
                    'price': price,
                    'location': location,
                    'scraping_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

            except AttributeError:
                logging.error(f"Error processing listing: {listing}")
                continue

        return property_listings

    except Exception as e:
        logging.error(f"Error scraping sreality.cz: {e}")
        return []


def save_to_db(property_listings):
    try:
        conn = sqlite3.connect('/root/sreality-db/sreality_db.sqlite3')
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS properties
                          (id INTEGER PRIMARY KEY, title TEXT, price TEXT, location TEXT, scraping_timestamp TEXT)''')

        for property_listing in property_listings:
            cursor.execute("INSERT INTO properties (title, price, location, scraping_timestamp) VALUES (?, ?, ?, ?)",
                           (property_listing['title'], property_listing['price'], property_listing['location'], property_listing['scraping_timestamp']))

        conn.commit()
        conn.close()

        logging.info(f"{len(property_listings)} property listings saved to the database")

    except Exception as e:
        logging.error(f"Error saving data to the database: {e}")


def main():
    logging.info("Started scraping")
    url = "https://www.sreality.cz/search?category_type_cb=1&per_page=50&region=1&subregion=1&radius=0&price_from=0&price_to=0&years_from=0&years_to=0&building_age=0&sort=0&hideRegions=0&hideHigherPrague=0&estatetype=1&layout=0&ownership=0&building_type=0&condition=0&floor_area=0&usable_area=0&land_area=0&cellar=0&balcony=0&terrace=0&garage=0&parking=0&garden=0&pool=0&lift=0&barrier_free=0&energy_efficiency=0"
    property_listings = scrape_sreality(url)
    save_to_db(property_listings)
    logging.info("Finished scraping")


if __name__ == "__main__":
    main()
