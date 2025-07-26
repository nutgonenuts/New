import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot(driver, name):
    driver.save_screenshot(os.path.join(SCREENSHOT_DIR, f"{name}.png"))

print("[DEBUG] Starting Parkalot Booking Bot...")

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://app.parkalot.io/")
    print("[DEBUG] Opened Parkalot website.")
    take_screenshot(driver, "step1_home")

    # Fill login form
    driver.find_element(By.NAME, "email").send_keys(os.environ.get("PARKALOT_EMAIL"))
    driver.find_element(By.NAME, "password").send_keys(os.environ.get("PARKALOT_PASSWORD"))
    driver.find_element(By.XPATH, "//button[contains(text(), 'LOG IN')]").click()
    print("[DEBUG] Login attempted.")
    time.sleep(3)
    take_screenshot(driver, "step2_after_login")

    # Check if logged in
    if "dashboard" in driver.current_url:
        print("[DEBUG] Successfully logged in.")
    else:
        print("[ERROR] Login failed.")
        take_screenshot(driver, "error_login_failed")
        exit(1)

except Exception as e:
    print(f"[ERROR] {e}")
    take_screenshot(driver, "error_exception")
    exit(1)
finally:
    driver.quit()
    print("[DEBUG] Browser closed.")
