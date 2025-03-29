import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_access():
    # Get secrets from environment variables
    url = os.environ.get('BOOKING_URL')
    username = os.environ.get('BOOKING_USERNAME')
    password = os.environ.get('BOOKING_PASSWORD')

    print("Starting test...")
    print(f"URL available: {'Yes' if url else 'No'}")
    print(f"Username available: {'Yes' if username else 'No'}")
    print(f"Password available: {'Yes' if password else 'No'}")

    # Setup Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    driver = None
    try:
        # Initialize Chrome driver with service
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("\nBrowser initialized")
        
        # Try accessing the URL
        print(f"\nTrying to access: {url}")
        driver.get(url)
        print(f"Page Title: {driver.title}")
        
        # Wait a moment to see the page
        time.sleep(3)
        
        print("\nTest completed successfully")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_access()
