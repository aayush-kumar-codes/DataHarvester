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
db = mongo_client["bizbuysell"]

def wait_random_time():
    """Wait for a random time to mimic human behavior."""
    time.sleep(random.uniform(2, 5))

# Mapping of locations to their corresponding link classes
link_classes = {
    "california": ".diamond",
    "australia": ".showcase"
}

def scrape_and_store_jobs(location, url):
    """Scrape job postings from a specific location and store them in MongoDB."""
    print(f"Processing location: {location}")

    # Initialize WebDriver for the given location
    driver = initialize_webdriver()
    
    # Create or select the MongoDB collection for the current location
    collection = db[location]
    
    # Ensure the "link" field is unique by creating an index
    collection.create_index("link", unique=True)
    
    # Get the appropriate class for the location
    link_class = link_classes.get(location, ".diamond")  # Default to ".diamond" if location is not in the mapping
    
    try:
        # Navigate to the BizBuySell page for the current location
        driver.get(url)

        # Wait for the page to load and elements to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "listing-container"))
        )

        # Mimic human behavior
        wait_random_time()

        # Scrape data
        titles = driver.find_elements(By.CSS_SELECTOR, ".title")
        locations = driver.find_elements(By.CSS_SELECTOR, ".location")
        prices = driver.find_elements(By.CSS_SELECTOR, ".asking-price")
        descriptions = driver.find_elements(By.CSS_SELECTOR, ".description")
        job_links = driver.find_elements(By.CSS_SELECTOR, link_class)  # Use the correct class for links

        # Debugging information
        print(f"Found {len(titles)} titles, {len(job_links)} job links")

        # Process and structure the data
        for i in range(len(job_links)):
            title = titles[i].text.strip() if i < len(titles) else ""
            loc = locations[i].text.strip() if i < len(locations) else ""
            price = prices[i].text.strip() if i < len(prices) else ""
            description = descriptions[i].text.strip() if i < len(descriptions) else ""
            link_element = job_links[i]
            link = link_element.get_attribute("href").strip() if i < len(job_links) else ""

            job_entry = {
                "title": title,
                "location": loc,
                "price": price,
                "description": description,
                "link": link
            }

            if job_entry["link"]:
                try:
                    collection.insert_one(job_entry)
                    print(f"Inserted job: {job_entry['title']} into MongoDB.")
                except DuplicateKeyError:
                    print(f"Duplicate job found and skipped: {job_entry['title']}")
                    duplicate = collection.find_one({"link": job_entry["link"]})
                    print(f"Conflicting Entry in MongoDB: {duplicate}")
            else:
                print(f"Skipped entry with empty link: {job_entry['title']}")

    except Exception as e:
        print(f"An error occurred for location {location}: {e}")

    finally:
        # Close the browser session
        driver.quit()

    print(f"Data for location {location} successfully processed and stored in MongoDB.")

# Example 
scrape_and_store_jobs("california", "https://www.bizbuysell.com/california-businesses-for-sale/?q=bHQ9MzAsNDAsODA%3D")
scrape_and_store_jobs("australia", "https://www.bizbuysell.com/australia-businesses-for-sale/?q=bHQ9MzAsNDAsODA%3D")
