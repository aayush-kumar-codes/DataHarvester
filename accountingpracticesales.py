import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient, errors

# Function to initialize WebDriver
def initialize_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Uncomment if you want to run Chrome in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--no-sandbox")  # Disable sandboxing (often needed in headless mode)
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36")
    chrome_driver_path = 'C:/webdrivers/chromedriver.exe'
    return webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)

# MongoDB setup
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["accounting"]

def scrape_and_store_data():
    driver = initialize_webdriver()

    # Create or select the MongoDB collection
    collection = db["listings"]
    collection.create_index("link", unique=True)
    
    url = "https://accountingpracticesales.com/apslistings/search/United-States/any/0/sort/0/0/0/0/u/u/u/u/u/u/u/u/u/any/u/u/"
    driver.get(url)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "fab_apslistingsearchresult"))
    )

    listings = driver.find_elements(By.CSS_SELECTOR, "a.apslistingitem_n")

    for listing in listings:
        title = listing.find_element(By.CSS_SELECTOR, "div.apslistingitem_nheader").text.strip()
        link = listing.get_attribute("href")

        # Extract details
        listing_number = None
        asking_price = None
        annual_revenue = None
        location = None
        description = None
        type_ = None

        details = listing.find_elements(By.CSS_SELECTOR, "div.apslistingcontainer.apslistingitem_nitem")
        
        for detail in details:
            text = detail.text
            if "Listing #" in text:
                listing_number = text.split(":")[-1].strip()
            elif "Asking Price:" in text:
                asking_price = text.split(":")[-1].strip()
            elif "Annual Revenue:" in text:
                annual_revenue = text.split(":")[-1].strip()
            elif "Location:" in text:
                location = text.split(":")[-1].strip()
            elif "Type:" in text:
                type_ = text.split(":")[-1].strip()

        job_entry = {
            "title": title,
            "link": link,
            "listing_number": listing_number,
            "asking_price": asking_price,
            "annual_revenue": annual_revenue,
            "location": location,
            "description": description,
            "type": type_
        }

        try:
            collection.insert_one(job_entry)
            print(f"Inserted job: {title} into MongoDB.")
        except errors.DuplicateKeyError:
            print(f"Duplicate job found and skipped: {title}")

    driver.quit()

# Run the function immediately upon starting the script
scrape_and_store_data()
