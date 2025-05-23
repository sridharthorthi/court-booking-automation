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
    print("Starting script...")
    booking_status = []  # List to collect all status messages
    
    url = "https://northwestbadmintonacademy.sites.zenplanner.com/login.cfm"
    username = os.environ.get('BOOKING_USERNAME')
    password = os.environ.get('PASSWORD')

    print(f"Credentials check - Username exists: {'Yes' if username else 'No'}")
    print(f"Credentials check - Password exists: {'Yes' if password else 'No'}")
    booking_status.append(f"Script started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    if not username or not password:
        error_msg = "Missing credentials"
        booking_status.append(error_msg)
        with open(os.environ.get('GITHUB_STEP_SUMMARY', 'booking_status.txt'), 'w') as f:
            f.write('\n'.join(booking_status))
        raise Exception(error_msg)

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    driver = None
    try:
        print("Initializing Chrome driver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Browser initialized")
        
        # Login
        print(f"Accessing URL: {url}")
        driver.get(url)
        username_field = driver.find_element(By.ID, "idUsername")
        username_field.send_keys(username)
        password_field = driver.find_element(By.ID, "idPassword")
        password_field.send_keys(password)
        login_button = driver.find_element(By.XPATH, "//input[@type='SUBMIT'][@value='Log In']")
        login_button.click()
        print("Logged in successfully")
        booking_status.append("Login successful")
        
        # Navigate to Reservations
        time.sleep(2)
        print("Looking for Reservations link...")
        reservations_link = driver.find_element(By.XPATH, "//a[contains(@href, 'person-calendar.cfm')]")
        reservations_link.click()
        print("Clicked Reservations")
        booking_status.append("Navigated to Reservations")
        
        # Click Reserve button
        time.sleep(2)
        print("Looking for Reserve button...")
        reserve_button = driver.find_element(By.XPATH, "//a[contains(@href, 'calendar.cfm')]")
        reserve_button.click()
        print("Clicked Reserve")
        
        # Wait for calendar to load
        time.sleep(2)
        
        # Click next twice to go to Sunday
        print("Looking for next day button...")
        next_button = driver.find_element(By.XPATH, "//i[@class='icon-chevron-right']")
        next_button.click()
        print("Moved to Saturday")
        time.sleep(1)
        next_button = driver.find_element(By.XPATH, "//i[@class='icon-chevron-right']")
        next_button.click()
        print("Moved to Sunday")
        booking_status.append("Navigated to Sunday")
        
        # Wait for page to update
        time.sleep(2)
        
        # Look for 5:00 PM slot and click Reserve
        print("Searching for 5:00 PM slot...")
        try:
            slot = driver.find_element(By.XPATH, "//div[contains(@class, 'calendar-custom-color-2bff00') and contains(text(), '5:00 PM')]")
            print("Found 5:00 PM slot!")
            slot.click()
            print("Clicked on 5:00 PM slot")
            booking_status.append("Found and clicked 5:00 PM slot")
            
            # Wait for reserve button and click it
            time.sleep(2)
            reserve_button = driver.find_element(By.XPATH, "//a[contains(@class, 'btn-primary') and contains(@id, 'reserve_')]")
            reserve_button.click()
            print("Clicked Reserve button")

            # Wait for confirmation page
            time.sleep(3)
            
            # Check for success
            try:
                success_indicator = driver.find_element(By.XPATH, "//*[contains(text(), 'is registered for this class')]")
                success_msg = "Booking Successful! " + success_indicator.text
                print(success_msg)
                booking_status.append(success_msg)
            except:
                # Check if there's an error message
                try:
                    error_message = driver.find_element(By.XPATH, "//*[contains(@class, 'error-message')]")
                    failure_msg = f"Booking Failed. Error: {error_message.text}"
                    print(failure_msg)
                    booking_status.append(failure_msg)
                except:
                    unknown_msg = "Couldn't find success or error message. Please verify manually."
                    print(unknown_msg)
                    booking_status.append(unknown_msg)
                
        except Exception as e:
            error_msg = f"5:00 PM slot not found or not available. Error: {str(e)}"
            print(error_msg)
            booking_status.append(error_msg)
                
    except Exception as e:
        error_msg = f"Error occurred: {str(e)}"
        print(error_msg)
        booking_status.append(error_msg)
    finally:
        if driver:
            driver.quit()
        
        # Create status output file for GitHub Actions
        with open(os.environ.get('GITHUB_STEP_SUMMARY', 'booking_status.txt'), 'w') as f:
            f.write('\n'.join(booking_status))

if __name__ == "__main__":
    test_access()
