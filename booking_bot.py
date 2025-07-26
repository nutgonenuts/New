import os
import time
from dotenv import load_dotenv
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Load environment variables from .env file
load_dotenv()

# --- Setup Chrome/Driver ---
def init_driver():
    print("[DEBUG] Installing matching ChromeDriver...")
    chromedriver_autoinstaller.install()
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("[DEBUG] Chrome started successfully.")
        return driver
    except Exception as e:
        print(f"[ERROR] ChromeDriver launch failed: {e}")
        raise

# --- Validate secrets ---
def get_credentials():
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    print(f"[DEBUG] EMAIL set? {'YES' if email else 'NO'}")
    print(f"[DEBUG] PASSWORD set? {'YES' if password else 'NO'}")
    if not email or not password:
        raise ValueError("EMAIL or PASSWORD not set in .env file!")
    return email, password

# --- Safe element finder ---
def safe_find(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        print(f"[ERROR] Element not found: {value}")
        return None

# --- Login attempt ---
def try_login(driver, email, password):
    driver.get("https://app.parkalot.io/login")
    print("[DEBUG] Opened Parkalot website.")
    driver.save_screenshot("screenshots/step_home.png")

    email_field = safe_find(driver, By.NAME, "email")
    pass_field = safe_find(driver, By.NAME, "password")
    login_button = safe_find(driver, By.XPATH, "//button[contains(text(), 'LOG IN')]")

    if not email_field or not pass_field or not login_button:
        print("[ERROR] Login fields not found.")
        driver.save_screenshot("screenshots/step_error_no_fields.png")
        return False

    email_field.send_keys(email)
    pass_field.send_keys(password)
    login_button.click()

    try:
        WebDriverWait(driver, 10).until(EC.url_contains("dashboard"))
        print("[DEBUG] Login successful!")
        driver.save_screenshot("screenshots/step_logged_in.png")
        return True
    except TimeoutException:
        print("[ERROR] Login failed.")
        driver.save_screenshot("screenshots/step_login_failed.png")
        return False

# --- Book parking space ---
def book_parking(driver, booking_date):
    try:
        # Navigate to booking section (update selector based on dashboard)
        book_button = safe_find(driver, By.XPATH, "//a[contains(text(), 'Book Parking')] | //button[contains(text(), 'Book Now')]")
        if not book_button:
            print("[ERROR] Booking section not found.")
            driver.save_screenshot("screenshots/step_booking_not_found.png")
            return False

        book_button.click()
        print("[DEBUG] Navigated to booking page.")
        driver.save_screenshot("screenshots/step_booking_page.png")

        # Select date (update selector and format based on date picker)
        date_picker = safe_find(driver, By.ID, "datePicker") or safe_find(driver, By.CLASS_NAME, "date-input")
        if not date_picker:
            print("[ERROR] Date picker not found.")
            driver.save_screenshot("screenshots/step_date_picker_not_found.png")
            return False

        date_picker.clear()
        date_picker.send_keys(booking_date)  # e.g., "2025-07-27" for YYYY-MM-DD
        print(f"[DEBUG] Selected date: {booking_date}")
        driver.save_screenshot("screenshots/step_date_selected.png")

        # Find and book the first available space (update selector)
        book_space_button = safe_find(driver, By.XPATH, "//button[contains(text(), 'Book') or contains(text(), 'Reserve')]")
        if not book_space_button:
            print("[ERROR] No available spaces or book button found.")
            driver.save_screenshot("screenshots/step_no_spaces.png")
            return False

        book_space_button.click()
        WebDriverWait(driver, 10).until(EC.alert_is_present() or EC.url_contains("confirmation"))
        print("[DEBUG] Parking space booked!")
        driver.save_screenshot("screenshots/step_booking_confirmed.png")
        return True

    except Exception as e:
        print(f"[ERROR] Booking failed: {e}")
        driver.save_screenshot("screenshots/step_booking_failed.png")
        return False

# --- Main ---
def main():
    driver = None
    try:
        driver = init_driver()
        email, password = get_credentials()
        if try_login(driver, email, password):
            # Book for tomorrow (Sunday, July 27, 2025)
            booking_date = "2025-07-27"  # Adjusted to YYYY-MM-DD, common for date inputs
            if book_parking(driver, booking_date):
                print("[SUCCESS] Booking completed for", booking_date)
            else:
                print("[FAIL] Booking attempt failed.")
        else:
            print("[FAIL] Login failed, booking aborted.")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
