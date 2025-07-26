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
def safe_find(driver, by, value, timeout=20):  # Increased to 20 seconds for login
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        print(f"[ERROR] Element not found: {value}")
        return None

# --- Login attempt with multiple strategies ---
def try_login(driver, email, password):
    driver.get("https://app.parkalot.io/login")
    print("[DEBUG] Opened Parkalot website.")
    time.sleep(5)  # Wait for JS to load
    driver.save_screenshot("screenshots/step_home.png")

    # Updated locators based on screenshot
    email_locators = [
        (By.XPATH, "//input[@type='email' and @label='email']"),
        (By.CLASS_NAME, "form-control float-label"),
        (By.NAME, "email"),
        (By.ID, "user_email"),
        (By.XPATH, "//input[@type='email']")
    ]
    pass_locators = [
        (By.XPATH, "//input[@type='password' and @label='password']"),
        (By.CLASS_NAME, "form-control float-label"),
        (By.NAME, "password"),
        (By.ID, "user_password"),
        (By.XPATH, "//input[@type='password']")
    ]
    login_button_locators = [
        (By.XPATH, "//button[contains(text(), 'LOG IN')]"),
        (By.CLASS_NAME, "btn primary"),
        (By.ID, "login-btn"),
        (By.XPATH, "//button[@type='submit']")
    ]

    max_attempts = 3
