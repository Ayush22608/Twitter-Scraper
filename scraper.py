import time
import random
import pymongo
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import itertools
from datetime import datetime
import tqdm
from concurrent.futures import ThreadPoolExecutor

# MongoDB setup
CONNECTION_STRING = "mongodb+srv://ayush22608:Ayushsingh1@cluster0.dlgzd.mongodb.net/twitter_trends?retryWrites=true&w=majority"

# Replace <password> with your actual password
client = pymongo.MongoClient(CONNECTION_STRING)

# Access the database and collection
db = client["twitter_trends"]
collection = db["trends"]

# Proxy validation function
def validate_proxy(proxy):
    test_url = "http://api.ipify.org?format=json"
    try:
        response = requests.get(test_url, proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"}, timeout=5)
        if response.status_code == 200:
            return proxy
    except Exception:
        return None

def validate_proxies(proxy_list):
    valid_proxies = []
    with ThreadPoolExecutor(max_workers=300) as executor:
        results = list(tqdm.tqdm(executor.map(validate_proxy, proxy_list), total=len(proxy_list)))
    valid_proxies = [proxy for proxy in results if proxy]
    return valid_proxies

# Load and validate proxies
def load_proxies(file_path):
    try:
        with open(file_path, 'r') as file:
            proxies = file.readlines()
            # Remove any unwanted spaces, newlines, or empty lines
            proxies = [proxy.strip() for proxy in proxies if proxy.strip()]
        return proxies
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return []

# Path to your proxy.txt file
file_path = 'proxy_list.txt'

# Load proxies from the file
proxies = load_proxies(file_path)
proxy_list=proxies


# valid_proxies = validate_proxies(proxy_list)
# if not valid_proxies:
#     print("No valid proxies available. Exiting.")
#     exit()

# # Proxy rotation setup
# proxy_pool = itertools.cycle(valid_proxies)

# Function to set proxy in Selenium
def set_proxy(chrome_options, proxy):
    chrome_options.add_argument(f"--proxy-server={proxy}")
    
    # proxy_config = Proxy()
    # proxy_config.proxy_type = ProxyType.MANUAL
    # proxy_config.http_proxy = proxy
    # proxy_config.ssl_proxy = proxy
    # proxy_config.add_to_capabilities(webdriver.DesiredCapabilities.CHROME)
    # chrome_options.add_argument(f"--proxy-server={proxy}")

# Scraper function
def scrape_twitter():
    # Rotate proxy
    # proxy = next(proxy_pool)
    # print(f"Using proxy: {proxy}")
    
    
    # Set up Selenium with Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage") 
    chrome_options.add_argument("--window-size=1920,1080")  # Set the browser window size

    # set_proxy(chrome_options, proxy)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    result = {}

    try:
        # Log in to Twitter
        print("logging into twitter")
        driver.get("https://twitter.com/login")
        time.sleep(10)
        
        username = driver.find_element(By.NAME, "text")
        print("username")
        username.send_keys("AyushSingh78779")
        driver.find_element(By.XPATH, '//span[text()="Next"]').click()
        time.sleep(5)

        password = driver.find_element(By.NAME, "password")
        print("password")
        password.send_keys("demo1234")
        driver.find_element(By.XPATH, '//span[text()="Log in"]').click()
        time.sleep(10)

        # Scrape trending topics
        print("find topics")
        trends_section = driver.find_element(By.XPATH, '//div[@aria-label="Timeline: Trending now"]').text.split("\n")
        trends_text = []
        
        to_add = False
        for trend in trends_section:
            if to_add:
                trends_text.append(trend)
                to_add = False
                continue
            
            if "Trending" in trend:
                to_add = True
                
        # trends = trends_section.find_elements(By.XPATH, './/span')[:5]  # Get top 5 trends
        # trends_text = [trend.text for trend in trends]
        print("Trends:", trends_text)
        
        driver.get("https://ifconfig.me/ip")
        ip_address = driver.find_element(By.TAG_NAME, "pre").text

        # Record result in MongoDB
        result = {
            # "unique_id": random.randint(1000, 9999),  # Replace with UUID if needed
            "nameoftrend1": trends_text[0] if len(trends_text) > 0 else None,
            "nameoftrend2": trends_text[1] if len(trends_text) > 1 else None,
            "nameoftrend3": trends_text[2] if len(trends_text) > 2 else None,
            "nameoftrend4": trends_text[3] if len(trends_text) > 3 else None,
            "nameoftrend5": trends_text[4] if len(trends_text) > 4 else None,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip_address": ip_address
            # "proxy_used": proxy,
        }
        collection.insert_one(result)
        result["_id"] = str(result["_id"])
        print("Result saved to MongoDB:", result)

    except Exception as e:
        print("Error during scraping:", e)
    finally:
        driver.quit()
        
    return result

# Run the scraper
if __name__ == "__main__":
    scrape_twitter()
