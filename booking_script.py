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

def get_clicks_needed(target_day):
    current_day = datetime.now().strftime('%A')
    
    # Map days to numbers (0-6)
    days = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2,
        'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
    }
    
    current_num = days[current_day]
    target_num = days[target_day]
    
    # Calculate clicks needed considering week wrap-around
    clicks = (target_num - current_num) % 7
    
    print(f"Running on {current_day}, targeting {target_day}, needs {clicks} clicks")
    return clicks

def navigate_and_book(driver, day_name, clicks_needed, booking_status):
    print(f"Navigating to {day_name}...")
    booking_status.append(f"\nAttempting booking for {day_name}:")
    
    # Navigate to the day
    for i in range(clicks_needed):
        try:
            print(f"Looking for next button...")
            next_button = driver.find_element(By.XPATH, "//i[@class='icon-chevron-right']")
            print(f"Found next button, clicking...")
            next_button.click()
            print(f"Click {i+1} of {clicks_needed} completed")
            time.sleep(1)
        except Exception as e:
            error_msg = f"Failed to navigate to {day_name} at click {i+1}. Error: {str(e)}"
            print(error_msg)
            booking_status.append(error_msg)
            return False, error_msg
    
    time.sleep(2)
    print(f"Navigation completed, looking for 5:00 PM slot...")
    
    # Look for 5:00 PM slot
    try:
        slot = driver.find_element(By.XPATH, "//div[contains(@class, 'calendar-custom-color-2bff00') and contains(text(), '5:00 PM')]")
        print("Found 5:00 PM slot")
    except Exception as e:
        error_msg = f"5:00 PM slot not found for {day_name} - Slots might not be opened yet. Error: {str(e)}"
        print(error_msg)
        booking_status.append(error_msg)
        return False, error_msg
        
    # Try booking the slot
    try:
        print("Clicking on 5:00 PM slot...")
        slot.click()
        time.sleep(2)
        
        print("Looking for reserve button...")
        reserve_button = driver.find_element(By.XPATH, "//a[contains(@class, 'btn-primary') and contains(@id, 'reserve_')]")
        print("Clicking reserve button...")
        reserve_button.click()
        time.sleep(3)
        
        print("Checking booking status...")
        # Check for "fully booked" message
        if "All available spots for this class session are now taken" in driver.page_source:
            error_msg = f"{day_name} 5:00 PM slot is fully booked"
            print(error_msg)
            booking_status.append(error_msg)
            return False, error_msg
            
        # Check for success message
        if "is registered for this class" in driver.page_source:
            success_msg = f"Successfully booked {day_name} 5:00 PM slot"
            print(success_msg)
            booking_status.append(success_msg)
            return True, success_msg
            
        error_msg = f"Unexpected state after booking attempt for {day_name}"
        print(error_msg)
        booking_status.append(error_msg)
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Error booking {day_name} slot: {str(e)}"
        print(error_msg)
        booking_status.append(error_msg)
        return False, error_msg

def book_courts():
    print("Starting booking script...")
    booking_status = [f"Booking attempt started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
    
    url = "https://northwestbadmintonacademy.sites.zenplanner.com/login.cfm"
    username = os.environ.get('BOOKING_USERNAME')
    password = os.environ.get('PASSWORD')

    print("Checking credentials...")
    if not username or not password:
        error_msg = "Missing credentials"
        print(error_msg)
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
        print("Setting up Chrome driver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Chrome driver initialized")
        
        # Login
        print(f"Accessing login URL...")
        driver.get(url)
        print("Page loaded, looking for username field...")
        username_field = driver.find_element(By.ID, "idUsername")
        username_field.send_keys(username)
        print("Username entered")
        password_field = driver.find_element(By.ID, "idPassword")
        password_field.send_keys(password)
        print("Password entered")
        login_button = driver.find_element(By.XPATH, "//input[@type='SUBMIT'][@value='Log In']")
        login_button.click()
        print("Login button clicked")
        booking_status.append("Login successful")
        
        # Navigate to Reservations
        time.sleep(2)
        print("Looking for Reservations link...")
        reservations_link = driver.find_element(By.XPATH, "//a[contains(@href, 'person-calendar.cfm')]")
        reservations_link.click()
        print("Clicked Reservations link")
        
        # Click Reserve button
        time.sleep(2)
        print("Looking for Reserve button...")
        reserve_button = driver.find_element(By.XPATH, "//a[contains(@href, 'calendar.cfm')]")
        reserve_button.click()
        print("Clicked Reserve button")
        
        # Calculate clicks needed for each day
        tuesday_clicks = get_clicks_needed('Tuesday')
        thursday_clicks = get_clicks_needed('Thursday')
        
        # Book Tuesday
        tuesday_success, tuesday_msg = navigate_and_book(driver, "Tuesday", tuesday_clicks, booking_status)
        
        # Go back to calendar and book Thursday
        if tuesday_success:
            print("Navigating back to calendar for Thursday booking...")
            driver.get(url)  # Refresh to calendar
            time.sleep(2)
            thursday_success, thursday_msg = navigate_and_book(driver, "Thursday", thursday_clicks, booking_status)
            
            if tuesday_success and thursday_success:
                final_msg = "Successfully booked both Tuesday and Thursday slots!"
            else:
                final_msg = "Partial booking success. Check details above."
        else:
            final_msg = "Failed to book Tuesday slot, didn't attempt Thursday."
            
        print(final_msg)
        booking_status.append(f"\nFinal Status: {final_msg}")
                
    except Exception as e:
        error_msg = f"Error occurred: {str(e)}"
        print(error_msg)
        booking_status.append(error_msg)
    finally:
        if driver:
            driver.quit()
        
        # Write status file for GitHub Actions
        with open(os.environ.get('GITHUB_STEP_SUMMARY', 'booking_status.txt'), 'w') as f:
            f.write('\n'.join(booking_status))

if __name__ == "__main__":
    book_courts()
