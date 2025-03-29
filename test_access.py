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
    url = "https://northwestbadmintonacademy.sites.zenplanner.com/login.cfm"
    username = os.environ.get('BOOKING_USERNAME')
    password = os.environ.get('BOOKING_PASSWORD')

    print("Starting test...")
    print(f"Username available: {'Yes' if username else 'No'}")
    print(f"Password available: {'Yes' if password else 'No'}")

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("\nBrowser initialized")
        
        # Access login page
        driver.get(url)
        print(f"Accessed login page: {driver.title}")
        
        # Find and fill email field
        email_field = driver.find_element(By.NAME, "email address")
        email_field.send_keys(username)
        
        # Find and fill password field
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(password)
        
        # Click login button
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Log In')]")
        login_button.click()
        
        # Wait for login to complete
        time.sleep(3)
        
        # Check if login was successful
        print(f"Current URL after login attempt: {driver.current_url}")
        print("Checking if login was successful...")
        
        if "login.cfm" not in driver.current_url:
            print("Login successful!")
        else:
            print("Login may have failed - still on login page")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_access()
