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
    url = "https://northwestbadmintonacademy.sites.zenplanner.com/login.cfm"
    username = os.environ.getBOOKING_USERNAME')
    password = os.environ.getPASSWORD')

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Browser initialized")
        
        # Login
        driver.get(url)
        username_field = driver.find_element(By.ID, "idUsername")
        username_field.send_keys(username)
        password_field = driver.find_element(By.ID, "idPassword")
        password_field.send_keys(password)
        login_button = driver.find_element(By.XPATH, "//input[@type='SUBMIT'][@value='Log In']")
        login_button.click()
        print("Logged in successfully")
        
        # Navigate to Reservations
        time.sleep(2)
        reservations_link = driver.find_element(By.XPATH, "//a[contains(@href, 'person-calendar.cfm')]")
        reservations_link.click()
        print("Clicked Reservations")
        
        # Click Reserve button
        time.sleep(2)
        reserve_button = driver.find_element(By.XPATH, "//a[contains(@href, 'calendar.cfm')]")
        reserve_button.click()
        print("Clicked Reserve")
        
        # Wait for calendar to load
        time.sleep(2)
        
        # Click next to go to Saturday
        next_button = driver.find_element(By.XPATH, "//i[@class='icon-chevron-right']")
        next_button.click()
        print("Moved to next day")
        
        # Wait for page to update
        time.sleep(2)
        
        # Look for 5:00 PM slot
        try:
            slot = driver.find_element(By.XPATH, "//div[contains(@class, 'calendar-custom-color-2bff00') and contains(text(), '5:00 PM')]")
            print("Found 5:00 PM slot!")
            print("Slot text:", slot.text)
            print("Slot class:", slot.get_attribute('class'))
        except Exception as e:
            print("5:00 PM slot not found or not available")
            
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_access()
