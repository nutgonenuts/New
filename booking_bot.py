import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# === USER CREDENTIALS ===
EMAIL = os.getenv("PARKALOT_EMAIL", "your_email_here")
PASSWORD = os.getenv("PARKALOT_PASSWORD", "your_password_here")

def debug_screenshot(driver, step_name):
    os.makedirs("screenshots", exist_ok=True)
    filename = f"screenshots/{step_name}.png"
    driver.save_screenshot(filename)
    print(f"[DEBUG] Screenshot saved: {filename}")

def login(driver):
    print("[DEBUG] Opening Parkalot website...")
    driver.get("https://parkalot.io/login")  # <-- Update URL if needed
    time.sleep(3)
    debug_screenshot(driver, "step1_home")

    # Find email and password fields
    email_field = driver.find_element(By.XPATH, "//input[@type='email']")
    password_field = driver.find_element(By.XPATH, "//input[@type='password']")

    email_field.send_keys(EMAIL)
    password_field.send_keys(PASSWORD)
    debug_screenshot(driver, "step2_filled")

    # Click login
    login_button = driver.find_element(By.XPATH, "//button[contains(.,'LOG IN')]")
    login_button.click()
    print("[DEBUG] Login button clicked.")
    time.sleep(5)
    debug_screenshot(driver, "step3_after_login")

    # Check if login successful
    if "login" in driver.current_url.lower():
        print("[ERROR] Login failed! Check your credentials.")
        return False

    print("[DEBUG] Successfully logged in!")
    return True

def main():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-dev-shm-usage")

    print("[DEBUG] Starting Parkalot Booking Bot...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        logged_in = login(driver)
        if not logged_in:
            return

        print("[DEBUG] Attempting to find Reserve button...")
        time.sleep(3)

        try:
            reserve_button = driver.find_element(By.XPATH, "//button[contains(.,'Reserve')]")
            reserve_button.click()
            print("[DEBUG] Reservation successful!")
            debug_screenshot(driver, "step4_reserve_clicked")
        except:
            print("Error: No Reserve buttons found.")
            debug_screenshot(driver, "step_error_no_reserve")

    finally:
        driver.quit()
        print("[DEBUG] Browser closed.")

if __name__ == "__main__":
    main()
