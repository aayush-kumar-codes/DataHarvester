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
    #chrome_options.add_argument("--headless")  # Uncomment if you want to run Chrome in headless mode
    chrome_driver_path = 'C:/webdrivers/chromedriver.exe'
    return webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)


mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["bbms_data"]

def wait_random_time():
    """Wait for a random time to mimic human behavior."""
    time.sleep(random.uniform(2, 5))

def scrape_and_store_data():
    """Scrape data from the website and store it in MongoDB."""
  
    driver = initialize_webdriver()
    
   
    collection = db["business_listings"]
    
   
    collection.create_index("listing_number", unique=True)

    try:
        # Navigate to the website
        url = "https://bbms.biz/cgi-bin/a-bus2ff.asp?forsale=go"
        driver.get(url)

        # Wait for the page to load and elements to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//table"))
        )

        # Mimic human behavior
        wait_random_time()

        # Locate the data elements
        rows = driver.find_elements(By.XPATH, "//table//tr")[1:]  # Skip the header row

        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")

            if len(columns) >= 7:
                data_entry = {
                    "accounting": columns[0].text.strip(),
                    "location": columns[1].text.strip(),
                    "listing_number": columns[2].text.strip(),
                    "price": columns[3].text.strip(),
                    "down_payment": columns[4].text.strip(),
                    "disc_earnings": columns[5].text.strip(),
                    "sales_revenue": columns[6].text.strip(),
                    "description": columns[7].text.strip() if len(columns) > 7 else ""
                }

                try:
                    collection.insert_one(data_entry)
                    print(f"Inserted data: {data_entry['listing_number']} into MongoDB.")
                except DuplicateKeyError:
                    print(f"Duplicate listing found and skipped: {data_entry['listing_number']}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        
        driver.quit()

# Run the function immediately upon starting the script
scrape_and_store_data()
