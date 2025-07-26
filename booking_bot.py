from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import os
import time

# Setup Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://app.parkalot.io/")
time.sleep(2)

# Create screenshots folder
os.makedirs("screenshots", exist_ok=True)

# Save initial screenshot
driver.save_screenshot("screenshots/step1_login_page.png")
print("[DEBUG] Opened Parkalot login page.")

# LOGIN
email = os.getenv("PARKALOT_EMAIL")
password = os.getenv("PARKALOT_PASSWORD")

try:
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.save_screenshot("screenshots/step2_filled_credentials.png")
    driver.find_element(By.XPATH, "//button[contains(text(), 'LOG IN')]").click()
    print("[DEBUG] Submitted login form.")
except Exception as e:
    driver.save_screenshot("screenshots/error_before_login.png")
    print("[ERROR] Could not enter credentials:", e)
    driver.quit()
    exit(1)

# VERIFY LOGIN
time.sleep(4)
try:
    driver.find_element(By.XPATH, "//span[contains(text(), 'Upcoming')]")
    driver.save_screenshot("screenshots/step3_after_login.png")
    print("[DEBUG] Login successful!")
except NoSuchElementException:
    driver.save_screenshot("screenshots/error_login_failed.png")
    print("[ERROR] Login failed! Dashboard not loaded.")
    driver.quit()
    exit(1)
