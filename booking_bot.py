import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

os.makedirs("screenshots", exist_ok=True)

options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    driver.get("https://app.parkalot.io/")  # Replace with your login page or booking URL
    time.sleep(5)
    driver.save_screenshot("screenshots/step1_page.png")
finally:
    driver.quit()
