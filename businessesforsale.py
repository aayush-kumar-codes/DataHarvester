import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Function to initialize WebDriver
def initialize_webdriver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment if you want to run Chrome in headless mode
    chrome_driver_path = 'C:/webdrivers/chromedriver.exe'
    return webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)

# MongoDB setup
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["businessesforsale"]

def wait_random_time():
    """Wait for a random time to mimic human behavior."""
    time.sleep(random.uniform(2, 5))

def scrape_and_store_data(location, base_url, max_pages=5):
    """Scrape data postings from multiple pages of a specific location and store them in MongoDB."""
    print(f"Processing location: {location}")

    # Initialize WebDriver for the given location
    driver = initialize_webdriver()
    
    # Create or select the MongoDB collection for the current location
    collection = db[location]
    
    # Ensure the "link" field is unique by creating an index
    collection.create_index("link", unique=True)

    try:
        for page in range(1, max_pages + 1):
            # Handle the first page separately (no page number in URL)
            if page == 1:
                url = base_url
            else:
                url = f"{base_url}-{page}"

            print(f"Scraping page {page}: {url}")
            
            # Navigate to the Business for Sale page for the current location
            driver.get(url)

            # Wait for the page to load and elements to be present
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result-table"))  # Adjust as needed
            )

            # Mimic human behavior
            wait_random_time()

            # Scrape data
            titles = driver.find_elements(By.CSS_SELECTOR, "h2.with-label-1 a")
            locations = driver.find_elements(By.CSS_SELECTOR, "tr.t-loc td")
            descriptions = driver.find_elements(By.CSS_SELECTOR, "tr.t-desc p")
            prices = driver.find_elements(By.CSS_SELECTOR, "tr.t-finance td:nth-child(2)")
            revenues = driver.find_elements(By.CSS_SELECTOR, "tr.t-finance td:nth-child(2)")
            cash_flows = driver.find_elements(By.CSS_SELECTOR, "tr.t-finance td:nth-child(2)")
            data_links = driver.find_elements(By.CSS_SELECTOR, "h2.with-label-1 a")

            # Process and structure the data
            for i in range(len(titles)):
                data_entry = {
                    "title": titles[i].text.strip() if i < len(titles) else "",
                    "location": locations[i].text.strip() if i < len(locations) else "",
                    "description": descriptions[i].text.strip() if i < len(descriptions) else "",
                    "asking_price": prices[i].text.strip() if i < len(prices) else "",
                    "revenue": revenues[i].text.strip() if i < len(revenues) else "",
                    "cash_flow": cash_flows[i].text.strip() if i < len(cash_flows) else "",
                    "link": data_links[i].get_attribute("href") if i < len(data_links) else ""
                }

                try:
                    collection.insert_one(data_entry)
                    print(f"Inserted data: {data_entry['title']} into MongoDB.")
                except DuplicateKeyError:
                    print(f"Duplicate data found and skipped: {data_entry['title']}")

            # Check if there is a next page and if it should stop at max_pages
            next_button = driver.find_elements(By.CSS_SELECTOR, "a.pagination-next")
            if not next_button or page == max_pages:
                break

    except Exception as e:
        print(f"An error occurred for location {location}: {e}")

    finally:
        # Close the browser session
        driver.quit()

    print(f"Data for location {location} successfully processed and stored in MongoDB.")

# List of URLs to scrape
urls = [
    ("guest_houses_and_bed_and_breakfast_businesses", "https://www.businessesforsale.com/search/guest-houses-and-bed-and-breakfast-businesses-for-sale"),
    ("cafes_for_sale", "https://www.businessesforsale.com/search/cafes-for-sale"),
    ("camping_and_recreational_vehicle_parks", "https://www.businessesforsale.com/search/camping-and-recreational-vehicle-parks-for-sale"),
    ("farms_for_sale", "https://www.businessesforsale.com/search/farms-for-sale"),
    ("bars_for_sale", "https://www.businessesforsale.com/search/bars-for-sale"),
    ("websites_for_sale", "https://www.businessesforsale.com/search/websites-for-sale"),
    ("liquor_stores_and_off_licences_for_sale", "https://www.businessesforsale.com/search/liquor-stores-and-off-licences-for-sale")
]

# Scrape each URL
for location, url in urls:
    scrape_and_store_data(location, url)
