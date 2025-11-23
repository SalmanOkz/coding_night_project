# scrapper.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

from config import BASE_URL, IMPLICIT_WAIT_TIME, SELECTORS

def initialize_driver():
    """Initializes and returns the Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # Uncomment for headless mode (no browser window)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(IMPLICIT_WAIT_TIME)
    
    return driver

def extract_product_data(product_item, category_name):
    """
    Extracts required data fields from a single product HTML element (using BeautifulSoup).
    """
    try:
        # Use SELECTORS from config
        name_tag = product_item.select_one(SELECTORS['product_name'])
        price_tag = product_item.select_one(SELECTORS['product_price'])
        rating_tag = product_item.select_one(SELECTORS['product_rating'])
        reviews_tag = product_item.select_one(SELECTORS['product_reviews'])

        name = name_tag.text.strip() if name_tag else "N/A"
        price = price_tag.text.strip() if price_tag else "N/A"
        
        # Rating is often in a custom attribute on Banggood
        rating_str = rating_tag.get('data-rating') if rating_tag and rating_tag.get('data-rating') else "N/A"
        
        # Clean reviews count
        reviews_str = reviews_tag.text.strip().replace('(', '').replace(')', '').replace(',', '') if reviews_tag else "0"
        
        url_suffix = name_tag.get('href') if name_tag else ""
        url = urljoin(BASE_URL, url_suffix)

        return {
            'category': category_name,
            'product_name': name,
            'price': price,
            'rating': float(rating_str) if rating_str != "N/A" else None,
            'reviews_count': int(reviews_str.replace('+', '').strip()) if reviews_str.replace('N/A', '0').strip().isdigit() else 0,
            'url': url,
        }
    except Exception as e:
        # print(f"Error extracting data for an item: {e}") # Uncomment for debugging
        return None

def scrape_category_with_pagination(driver, start_url, category_name, max_pages=5):
    """
    Scrapes a category across multiple pages using Selenium for navigation.
    """
    all_products = []
    current_page = 1
    current_url = start_url
    
    while current_page <= max_pages and current_url:
        print(f"Fetching Page {current_page} for {category_name}: {current_url}")
        
        try:
            driver.get(current_url)
            
            # Wait for the main product container to load to ensure dynamic content is ready
            # NOTE: Verify this selector (SELECTORS['product_container']) on the site
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS['product_container']))
            )
            
            # Use BeautifulSoup to parse the fully loaded page source
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            product_containers = soup.select(SELECTORS['product_container']) 
            
            if not product_containers:
                print("No product containers found. Check selectors.")
                break
                
            for container in product_containers:
                product_data = extract_product_data(container, category_name)
                if product_data:
                    all_products.append(product_data)

            # --- Pagination Logic ---
            next_page_url = None
            try:
                # Find the 'Next Page' button using Selenium's element finding
                next_button = driver.find_element(By.CSS_SELECTOR, SELECTORS['next_page_button'])
                if next_button and next_button.get_attribute('href'):
                    next_page_url = next_button.get_attribute('href')
                
            except Exception:
                # This exception means the next button selector was not found (end of pagination)
                pass

            if next_page_url and current_page < max_pages:
                current_url = next_page_url
                current_page += 1
                time.sleep(2) # Be polite and wait between page loads
            else:
                current_url = None # Stop the loop
                print("Reached last page or max pages limit.")
                
        except Exception as e:
            print(f"An error occurred during scraping page {current_page}: {e}")
            break
            
    return all_products