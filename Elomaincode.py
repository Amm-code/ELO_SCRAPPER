# Creat virtual environment first
# python3 -m venv .venv
# source .venv/bin/activate
# pip install selenium
# pip install pandas
# pip install webdriver-manager
# If you need guidence about automation or scraping, contact me amadansari89@gmail.com

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--window-size=1920,1080")  # Set window size
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # Mimic a real user

# Initialize the WebDriver using webdriver_manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def scrape_page(url):
    """Scrape product data from a single page."""
    driver.get(url)
    print(f"Page loaded: {url}")

    # Wait for the product grid to load
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
    product_grid = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="product-grid"]'))
    )
    print("Product grid found.")

    # Extract individual product elements
    products = product_grid.find_elements(By.XPATH, './/li')  # Find all <li> elements in the product grid
    print(f"Found {len(products)} products.")

    scraped_data = []
    
    for product in products:
        # Extract product title
        title_element = product.find_elements(By.XPATH, './/*[contains(@id, "title-template--")]')
        # Extract product price
        price_element = product.find_elements(By.XPATH, './/div/div/div[2]/div[1]/div')
        # Extract product link
        link_element = product.find_elements(By.XPATH, './/*[contains(@id, "CardLink-template--")]')
        
        data = {
            'name': title_element[0].text.strip() if title_element else 'N/A',
            'price': price_element[0].text.strip() if price_element else 'N/A',
            'url': link_element[0].get_attribute('href') if link_element else 'N/A'
        }
        scraped_data.append(data)
    
    return scraped_data

try:
    # Base URL for pagination
    base_url = "https://www.elo.shopping/collections/mens-tee-polos-shirts/page="
    
    all_products = []
    
    # Loop through pages 1 to 10
    for page in range(1, 11):
        url = base_url + str(page)
        print(f"Scraping page {page}...")
        scraped_data = scrape_page(url)
        all_products.extend(scraped_data)
        time.sleep(2)  # Add a delay to avoid overloading the server
    
    # Display results
    for idx, product in enumerate(all_products, 1):
        print(f"Product {idx}:")
        print(f"Name: {product['name']}")
        print(f"Price: {product['price']}")
        print(f"URL: {product['url']}\n")
    
    # Save results to a CSV file (optional)
    df = pd.DataFrame(all_products)
    df.to_csv("elo_products.csv", index=False)
    print("Data saved to elo_products.csv")

except Exception as e:
    print(f"Error: {e}")
    # Print the page source for debugging
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Page source saved to page_source.html for debugging.")

finally:
    # Close the browser
    driver.quit()
