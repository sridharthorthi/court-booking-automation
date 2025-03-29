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
    # Hardcoded URL since it's fixed
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
        
        driver.get(url)
        print(f"Accessed login page: {driver.title}")
        
        username_field = driver.find_element(By.ID, "idUsername")
        username_field.send_keys(username)
        print("Username entered")
        
        password_field = driver.find_element(By.ID, "idPassword")
        password_field.send_keys(password)
        print("Password entered")
        
        login_button = driver.find_element(By.XPATH, "//input[@type='SUBMIT'][@value='Log In']")
        login_button.click()
        print("Login button clicked")
        
        time.sleep(3)
        print(f"Current URL after login attempt: {driver.current_url}")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_access()
