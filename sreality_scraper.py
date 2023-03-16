import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
import sqlite3
from datetime import datetime

BASE_URL = "https://www.sreality.cz"
SEARCH_URL = "/hledani/prodej/byty/praha?strana="

def get_property_links(page_number):
    url = f"{BASE_URL}{SEARCH_URL}{page_number}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    property_links = [a['href'] for a in soup.select('.property a')]
    return property_links

def get_property_details(link):
    response = requests.get(f"{BASE_URL}{link}")
    soup = BeautifulSoup(response.text, "html.parser")
    
    price = soup.select_one('.norm-price').text.strip()
    title = soup.select_one('h1').text.strip()
    address = soup.select_one('.locality').text.strip()
    
    details = soup.select_one('.params-list').find_all('li')
    detail_dict = {}
    for detail in details:
        key, value = [item.strip() for item in detail.text.split(':', 1)]
        detail_dict[key] = value

    detail_dict['title'] = title
    detail_dict['price'] = price
    detail_dict['address'] = address
    detail_dict['link'] = f"{BASE_URL}{link}"
    detail_dict['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return detail_dict

def main():
    # Scrape property listings
    all_properties = []
    for i in range(1, 3):  # Change the range as needed (e.g., `range(1, 101)` for 100 pages)
        property_links = get_property_links(i)
        for link in property_links:
            property_details = get_property_details(link)
            all_properties.append(property_details)
            print(f"Scraped: {property_details['title']}")

    # Save data to a SQLite database
    df = pd.DataFrame(all_properties)
    engine = create_engine('sqlite:///data/property_listings.db')
    df.to_sql('property_listings', engine, if_exists='append', index=False)

if __name__ == "__main__":
    main()
