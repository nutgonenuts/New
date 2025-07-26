import os
import time
from dotenv import load_dotenv
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Load environment variables from .env file
load_dotenv()

# --- Setup Chrome/Driver ---
def init_driver():
    print("[DEBUG] Installing matching ChromeDriver...")
    chromedriver_autoinstaller.install()
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("[DEBUG] Chrome started successfully.")
        return driver
    except Exception as e:
        print(f"[ERROR] ChromeDriver launch failed: {e}")
        raise

# --- Validate secrets ---
def get_credentials():
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    print(f"[DEBUG] EMAIL set? {'YES' if email else 'NO'}")
    print(f"[DEBUG] PASSWORD set? {'YES' if password else 'NO'}")
    if not email or not password:
        raise ValueError("EMAIL or PASSWORD not set in .env file!")
    return email, password

# --- Safe element finder ---
def safe_find(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        return None

# --- Login attempt ---
def try_login(driver, email, password):
    driver.get("
