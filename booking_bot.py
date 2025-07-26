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
        raise Exception("Login form
