import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def debug_log(msg):
    print(f"[DEBUG] {msg}")

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def login(driver):
    driver.get("https://app.parkalot.io/login")
    debug_log("Opened Parkalot website.")

    try:
        # Wait for login form to appear
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email']"))
        )
    except TimeoutException:
        raise Exception("Login form not found.")

    email_input = driver.find_element(By.CSS_SELECTOR, "input[name='email']")
    password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    email_input.clear()
    email_input.send_keys(EMAIL)
    password_input.clear()
    password_input.send_keys(PASSWORD)
    password_input.send_keys(Keys.RETURN)
    debug_log("Submitted login form.")

    # Confirm login success
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button | //a | //div[contains(text(), 'Reserve')]"))
        )
        debug_log("Successfully logged in.")
    except TimeoutException:
        driver.save_screenshot("screenshots/login_failed.png")
        raise Exception("Login failed - check credentials or selectors.")

def reserve_spot(driver):
    try:
        reserve_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Reserve')] | //a[contains(text(),'Reserve')]"))
        )
        reserve_button.click()
        debug_log("Clicked Reserve button.")
    except TimeoutException:
        driver.save_screenshot("screenshots/no_reserve_button.png")
        raise Exception("No Reserve buttons found.")

def main():
    debug_log("Starting Parkalot Booking Bot...")
    debug_log(f"Email set? {'YES' if EMAIL else 'NO'}")
    debug_log(f"Password set? {'YES' if PASSWORD else 'NO'}")

    if not EMAIL or not PASSWORD:
        raise Exception("EMAIL or PASSWORD not set in secrets.")

    driver = init_driver()
    try:
        login(driver)
        reserve_spot(driver)
    finally:
        driver.quit()
        debug_log("Browser closed.")

if __name__ == "__main__":
    main()
