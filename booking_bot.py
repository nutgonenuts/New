import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

EMAIL = os.getenv("PARKALOT_EMAIL")
PASSWORD = os.getenv("PARKALOT_PASSWORD")

def debug_log(msg):
    print(f"[DEBUG] {msg}", flush=True)

def screenshot(driver, name):
    os.makedirs("screenshots", exist_ok=True)
    path = f"screenshots/{name}.png"
    driver.save_screenshot(path)
    debug_log(f"Screenshot saved: {path}")

def main():
    debug_log("Starting test login...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_window_size(1920, 1080)
    
    try:
        driver.get("https://app.parkalot.io/login")
        debug_log("Opened Parkalot login page.")
        screenshot(driver, "step1_login_page")
        time.sleep(3)

        # Fill email
        email_input = driver.find_element(By.NAME, "email")
        email_input.clear()
        email_input.send_keys(EMAIL)
        debug_log("Entered email.")

        # Fill password
        password_input = driver.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys(PASSWORD)
        debug_log("Entered password.")
        screenshot(driver, "step2_filled_login")

        # Click login
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'LOG IN')]")
        driver.execute_script("arguments[0].click();", login_button)
        debug_log("Clicked LOG IN button.")

        time.sleep(5)
        screenshot(driver, "step3_after_login")

        if "login" in driver.current_url:
            debug_log("Login failed! Still on login page.")
        else:
            debug_log("Login successful!")
    finally:
        driver.quit()
        debug_log("Browser closed.")

if __name__ == "__main__":
    main()
