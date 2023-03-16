import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
from time import sleep
from datetime import datetime

# Define the URL you want to scrape
base_url = 'https://www.sreality.cz'

# Replace these with the appropriate search parameters
search_url = f'{base_url}/search?category_main_cb=1&category_type_cb=1&region=nazev'

# Define the function to scrape property listings from a single page
def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    properties = soup.find_all('div', class_='property')

    property_list = []

    for prop in properties:
        title = prop.find('span', class_='title').text.strip()
        link = base_url + prop.find('a')['href']
        price = prop.find('span', class_='cena').text.strip()

        property_list.append({
            'title': title,
            'link': link,
            'price': price
        })

    return property_list

# Define the function to scrape multiple pages of property listings
def scrape_sreality(search_url):
    property_data = []
    current_page = 1

    while True:
        print(f'Scraping page {current_page}...')
        url = f'{search_url}&strana={current_page}'
        properties = scrape_page(url)
        if not properties:
            break

        property_data.extend(properties)
        current_page += 1
        sleep(1)

    return property_data

# Define the function to save data into a database
def save_to_database(data, db_name):
    df = pd.DataFrame(data)
    engine = create_engine(f'sqlite:///{db_name}.db')
    df.to_sql('properties', engine, if_exists='append', index=False)

# Scrape property listings and save them to a database
property_data = scrape_sreality(search_url)
db_name = f'sreality_{datetime.now().strftime("%Y%m%d")}'
save_to_database(property_data, db_name)
