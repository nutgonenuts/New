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

# LOGIN
email = os.getenv("PARKALOT_EMAIL")
password = os.getenv("PARKALOT_PASSWORD")

driver.find_element(By.NAME, "email").send_keys(email)
driver.find_element(By.NAME, "password").send_keys(password)
driver.find_element(By.XPATH, "//button[contains(text(), 'LOG IN')]").click()
time.sleep(3)

# VERIFY LOGIN
try:
    driver.find_element(By.XPATH, "//span[contains(text(), 'Upcoming')]")  # Example element after login
    print("[DEBUG] Login successful!")
    driver.save_screenshot("screenshots/after_login.png")
except NoSuchElementException:
    print("[ERROR] Login failed - could not find dashboard elements.")
    driver.save_screenshot("screenshots/login_failed.png")
    driver.quit()
    exit(1)
