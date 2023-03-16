import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

# Constants
BASE_URL = "https://www.sreality.cz"
SEARCH_URL = "/hledani/prodej/byty"

# Connect to the SQLite database file
conn = sqlite3.connect('/root/sreality-db/sreality_db.sqlite3')
cursor = conn.cursor()

# Create the properties table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    link TEXT,
    price INTEGER,
    price_per_sqm INTEGER,
    location TEXT,
    size TEXT,
    rooms INTEGER,
    floor INTEGER,
    building_type TEXT,
    ownership TEXT,
    property_age TEXT,
    property_condition TEXT,
    listing_date TEXT,
    agency_name TEXT,
    timestamp DATETIME
)''')

# Scrape the properties
response = requests.get(BASE_URL + SEARCH_URL)
soup = BeautifulSoup(response.text, 'html.parser')
properties = soup.select('.property')

for property in properties:
    title = property.select_one('.property__title').text.strip()
    link = BASE_URL + property.select_one('.property__title a')['href']
    price = int(property.select_one('.property__price').text.strip().replace('Kč', '').replace(' ', ''))
    location = property.select_one('.property__location').text.strip()
    size = property.select_one('.property__info').text.strip()
    price_per_sqm = int(price / float(size.split(' ')[0]))

    # Additional parameters
    rooms = int(property.select_one('.property__rooms').text.strip().split(' ')[0])
    floor_info = property.select_one('.property__floor').text.strip().split('/')
    floor = int(floor_info[0].strip().split(' ')[0])
    building_type = floor_info[1].strip()
    ownership = property.select_one('.property__ownership').text.strip()

    # Scrape additional details from the property page
    property_response = requests.get(link)
    property_soup = BeautifulSoup(property_response.text, 'html.parser')

    property_age = property_soup.select_one('.property__info .property__age')
    property_age = property_age.text.strip() if property_age else None

    property_condition = property_soup.select_one('.property__info .property__condition')
    property_condition = property_condition.text.strip() if property_condition else None

    listing_date = property_soup.select_one('.property__listing-date time')
    listing_date = listing_date['datetime'] if listing_date else None

    agency_name = property_soup.select_one('.property__seller .seller__name')
    agency_name = agency_name.text.strip() if agency_name else None

    timestamp = datetime.now()

    # Insert property details into the database
    cursor.execute('''
        INSERT INTO properties (title, link, price, price_per_sqm, location, size, rooms, floor, building_type, ownership, property_age, property_condition, listing_date, agency_name, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, link, price, price_per_sqm, location, size, rooms, floor, building_type, ownership, property_age, property_condition, listing_date, agency_name, timestamp))

# Commit the changes and close the connection
conn.commit()
conn.close()
