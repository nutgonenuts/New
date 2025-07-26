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
def safe_find(driver, by, value, timeout=20):
    try:
        return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))
    except TimeoutException:
        print(f"[ERROR] Element not visible: {value}")
        return None

# --- Login attempt ---
def try_login(driver, email, password):
    driver.get("https://app.parkalot.io/login")
    print("[DEBUG] Opened Parkalot website.")
    time.sleep(5)  # Wait for JS to load
    driver.save_screenshot("screenshots/step_home.png")

    email_field = safe_find(driver, By.XPATH, "//input[@type='email' and @label='email']")
    pass_field = safe_find(driver, By.XPATH, "//input[@type='password' and @label='password']")
    login_button = safe_find(driver, By.XPATH, "//button[contains(text(), 'LOG IN')]")

    if not email_field or not pass_field or not login_button:
        print("[ERROR] Login fields not found.")
        driver.save_screenshot("screenshots/step_error_no_fields.png")
        return False

    email_field.send_keys(email)
    pass_field.send_keys(password)
    login_button.click()

    try:
        WebDriverWait(driver, 20).until(EC.url_contains("dashboard"))
        print("[DEBUG] Login successful!")
        driver.save_screenshot("screenshots/step_logged_in.png")
        return True
    except TimeoutException:
        print("[ERROR] Login failed.")
        driver.save_screenshot("screenshots/step_login_failed.png")
        return False

# --- Book parking space for Sunday ---
def book_parking(driver):
    try:
        # Wait for dashboard to load
        time.sleep(5)
        driver.save_screenshot("screenshots/step_dashboard.png")

        # Find the "RESERVE" button for Sunday
        reserve_button = safe_find(driver, By.XPATH, "//div[contains(@class, 'row') and contains(., 'Sunday')]//button[contains(@class, 'btn') and contains(text(), 'RESERVE')]")
        if not reserve_button:
            print("[ERROR] Reserve button for Sunday not found.")
            driver.save_screenshot("screenshots/step_reserve_not_found.png")
            return False

        reserve_button.click()
        print("[DEBUG] Clicked Reserve for Sunday.")
        driver.save_screenshot("screenshots/step_reserve_clicked.png")

        # Wait for confirmation
        WebDriverWait(driver, 20).until(EC.alert_is_present() or EC.url_contains("confirmation") or EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Booking Confirmed')]")))
        print("[DEBUG] Booking confirmed!")
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
            if book_parking(driver):
                print("[SUCCESS] Booking completed for Sunday")
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
