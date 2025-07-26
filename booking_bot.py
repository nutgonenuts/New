import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

EMAIL = os.getenv("PARKALOT_EMAIL")
PASSWORD = os.getenv("PARKALOT_PASSWORD")

def log_debug(msg):
    print(f"[DEBUG] {msg}")

def take_screenshot(driver, name):
    os.makedirs("screenshots", exist_ok=True)
    path = os.path.join("screenshots", f"{name}.png")
    driver.save_screenshot(path)
    log_debug(f"Screenshot saved: {path}")

def main():
    log_debug("Starting Parkalot Booking Bot...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_window_size(1920, 1080)

    try:
        # Open website
        driver.get("https://app.parkalot.io/login")
        log_debug("Opened Parkalot website.")
        take_screenshot(driver, "step1_home")

        # Login
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'LOG IN')]")

        email_field.send_keys(EMAIL)
        password_field.send_keys(PASSWORD)
        login_button.click()

        time.sleep(5)
        take_screenshot(driver, "step2_after_login")

        # Check if login was successful
        if "login" in driver.current_url.lower():
            log_debug("Login failed - still on login page.")
            raise Exception("Login failed.")

        log_debug("Login successful.")

        # Find Reserve button
        reserve_button = None
        try:
            reserve_button = driver.find_element(By.XPATH, "//button[contains(@class, 'reserve')]")
            reserve_button.click()
            log_debug("Clicked Reserve button.")
            take_screenshot(driver, "step3_reserved")
        except Exception:
            log_debug("No Reserve buttons found.")
            take_screenshot(driver, "step_error_no_reserve")
            raise

    finally:
        driver.quit()
        log_debug("Browser closed.")

if __name__ == "__main__":
    main()
