import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime

def navigate_and_book(driver, day_name, clicks_needed, booking_status):
    print(f"Navigating to {day_name}...")
    booking_status.append(f"\nAttempting booking for {day_name}:")
    
    # Navigate to the day
    for i in range(clicks_needed):
        try:
            next_button = driver.find_element(By.XPATH, "//i[@class='icon-chevron-right']")
            next_button.click()
            time.sleep(1)
            print(f"Click {i+1} of {clicks_needed}")
        except Exception as e:
            error_msg = f"Failed to navigate to {day_name}. Error: {str(e)}"
            booking_status.append(error_msg)
            return False, error_msg
    
    time.sleep(2)
    
    # Look for 5:00 PM slot
    try:
        slot = driver.find_element(By.XPATH, "//div[contains(@class, 'calendar-custom-color-2bff00') and contains(text(), '5:00 PM')]")
    except:
        error_msg = f"5:00 PM slot not found for {day_name} - Slots might not be opened yet"
        booking_status.append(error_msg)
        return False, error_msg
        
    # Try booking the slot
    try:
        slot.click()
        time.sleep(2)
        
        reserve_button = driver.find_element(By.XPATH, "//a[contains(@class, 'btn-primary') and contains(@id, 'reserve_')]")
        reserve_button.click()
        time.sleep(3)
        
        # Check for "fully booked" message
        if "All available spots for this class session are now taken" in driver.page_source:
            error_msg = f"{day_name} 5:00 PM slot is fully booked"
            booking_status.append(error_msg)
            return False, error_msg
            
        # Check for success message
        if "is registered for this class" in driver.page_source:
            success_msg = f"Successfully booked {day_name} 5:00 PM slot"
            booking_status.append(success_msg)
            return True, success_msg
            
        error_msg = f"Unexpected state after booking attempt for {day_name}"
        booking_status.append(error_msg)
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Error booking {day_name} slot: {str(e)}"
        booking_status.append(error_msg)
        return False, error_msg

def book_courts():
    print("Starting booking script...")
    booking_status = [f"Booking attempt started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
    
    url = "https://northwestbadmintonacademy.sites.zenplanner.com/login.cfm"
    username = os.environ.get('BOOKING_USERNAME')
    password = os.environ.get('PASSWORD')     

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
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Login
        driver.get(url)
        username_field = driver.find_element(By.ID, "idUsername")
        username_field.send_keys(username)
        password_field = driver.find_element(By.ID, "idPassword")
        password_field.send_keys(password)
        login_button = driver.find_element(By.XPATH, "//input[@type='SUBMIT'][@value='Log In']")
        login_button.click()
        booking_status.append("Login successful")
        
        # Navigate to Reservations
        time.sleep(2)
        reservations_link = driver.find_element(By.XPATH, "//a[contains(@href, 'person-calendar.cfm')]")
        reservations_link.click()
        
        # Click Reserve button
        time.sleep(2)
        reserve_button = driver.find_element(By.XPATH, "//a[contains(@href, 'calendar.cfm')]")
        reserve_button.click()
        
        # Book Tuesday (2 clicks)
        tuesday_success, tuesday_msg = navigate_and_book(driver, "Tuesday", 2, booking_status)
        
        # Go back to calendar and book Thursday (4 clicks)
        if tuesday_success:
            driver.get(url)  # Refresh to calendar
            time.sleep(4)
            thursday_success, thursday_msg = navigate_and_book(driver, "Thursday", 4, booking_status)
            
            if tuesday_success and thursday_success:
                final_msg = "Successfully booked both Tuesday and Thursday slots!"
            else:
                final_msg = "Partial booking success. Check details above."
        else:
            final_msg = "Failed to book Tuesday slot, didn't attempt Thursday."
            
        booking_status.append(f"\nFinal Status: {final_msg}")
                
    except Exception as e:
        error_msg = f"Error occurred: {str(e)}"
        booking_status.append(error_msg)
    finally:
        if driver:
            driver.quit()
        
        # Write status file for GitHub Actions
        with open(os.environ.get('GITHUB_STEP_SUMMARY', 'booking_status.txt'), 'w') as f:
            f.write('\n'.join(booking_status))

if __name__ == "__main__":
    book_courts()
