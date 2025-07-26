import os
import time
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Auto-install correct ChromeDriver
chromedriver_autoinstaller.install()

# Check secrets
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

if not EMAIL or not PASSWORD:
    print("[ERROR] EMAIL or PASSWORD environment variable is missing.")
    exit(1)

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(), options=chrome_options)

try:
    driver.get("https://app.parkalot.io")
    time.sleep(2)
    driver.save_screenshot("screenshots/step1_home.png")
    print("[DEBUG] Opened Parkalot website.")

    # Retry login 3 times
    success = False
    for attempt in range(1, 4):
        try:
            print(f"[DEBUG] Attempt {attempt}: Logging in...")
            driver.find_element(By.NAME, "email").send_keys(EMAIL)
            driver.find_element(By.NAME, "password").send_keys(PASSWORD)
            driver.find_element(By.XPATH, "//button[contains(text(),'LOG IN')]").click()
            time.sleep(3)

            if "dashboard" in driver.current_url.lower():
                success = True
                print("[DEBUG] Login successful.")
                driver.save_screenshot("screenshots/login_success.png")
                break
            else:
                driver.save_screenshot(f"screenshots/login_fail_{attempt}.png")
        except Exception as e:
            print(f"[ERROR] Login attempt {attempt} failed: {e}")
            driver.save_screenshot(f"screenshots/error_{attempt}.png")

    if not success:
        print("[ERROR] Login failed after 3 attempts.")
        exit(1)

    # Add reservation code here
    print("[DEBUG] Bot is ready for next steps.")

finally:
    driver.quit()
    print("[DEBUG] Browser closed.")
