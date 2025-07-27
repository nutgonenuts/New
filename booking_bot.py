import os
import time
import traceback
from datetime import datetime, timedelta
from dotenv import load_dotenv
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

# Load environment variables
def load_environment():
    # Try loading from .env file
    if os.path.exists(".env"):
        load_dotenv()
        print("[INFO] Loaded .env file")
    else:
        print("[INFO] No .env file found, checking direct environment variables")
    
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    
    if not email or not password:
        raise ValueError("EMAIL or PASSWORD not set in .env file or environment variables")
    
    print("[INFO] EMAIL and PASSWORD retrieved successfully")
    return email, password

# Initialize ChromeDriver
def init_driver():
    chromedriver_autoinstaller.install()
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--enable-javascript")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("[INFO] ChromeDriver initialized")
        return driver
    except WebDriverException as e:
        print(f"[ERROR] Failed to initialize ChromeDriver: {e}\n{traceback.format_exc()}")
        raise

# Safe element finder with logging
def safe_find(driver, by, value, timeout=20, description="element"):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        print(f"[INFO] Found {description}: {value}")
        return element
    except TimeoutException:
        print(f"[ERROR] Timeout waiting for {description}: {value}")
        return None

# Login to Parkalot
def try_login(driver, email, password, max_attempts=2):
    driver.get("https://app.parkalot.io/login")
    print("[INFO] Navigated to login page")

    email_locators = [
        (By.ID, "email"),
        (By.NAME, "email"),
        (By.XPATH, "//input[@type='email']"),
        (By.XPATH, "//div[@class='md-form-group float-label']/input[@type='email']"),
        (By.CLASS_NAME, "form-control-sm md-input"),
        (By.XPATH, "//input[contains(@class, 'md-input') and @type='email']"),
        (By.XPATH, "//input[@name='email' or @id='email']"),
    ]
    pass_locators = [
        (By.ID, "password"),
        (By.NAME, "password"),
        (By.XPATH, "//input[@type='password']"),
        (By.XPATH, "//div[@class='md-form-group float-label']/input[@type='password']"),
        (By.CLASS_NAME, "form-control-sm md-input"),
        (By.XPATH, "//input[contains(@class, 'md-input') and @type='password']"),
        (By.XPATH, "//input[@name='password' or @id='password']"),
    ]
    login_button_locators = [
        (By.ID, "login"),
        (By.XPATH, "//button[@type='submit']"),
        (By.XPATH, "//button[contains(text(), 'Log In')]"),
        (By.XPATH, "//button[contains(text(), 'LOG IN')]"),
        (By.CLASS_NAME, "btn btn-block md-raised primary"),
        (By.XPATH, "//button[@type='button']"),
        (By.XPATH, "//button[contains(@class, 'md-btn') and contains(text(), 'LOG IN')]"),
        (By.XPATH, "//button[@type='submit' or contains(@class, 'login')]"),
    ]

    for attempt in range(max_attempts):
        print(f"[INFO] Login attempt {attempt + 1}/{max_attempts}")
        email_field = pass_field = login_button = None

        for by, value in email_locators:
            email_field = safe_find(driver, by, value, description="email field")
            if email_field:
                break
        for by, value in pass_locators:
            pass_field = safe_find(driver, by, value, description="password field")
            if pass_field:
                break
        for by, value in login_button_locators:
            login_button = safe_find(driver, by, value, description="login button")
            if login_button:
                break

        if not all([email_field, pass_field, login_button]):
            print(f"[ERROR] Missing login elements in attempt {attempt + 1}")
            driver.save_screenshot(f"{screenshot_dir}/login_attempt_{attempt + 1}_failed.png")
            continue

        try:
            email_field.clear()
            email_field.send_keys(email)
            pass_field.clear()
            pass_field.send_keys(password)
            login_button.click()
            print("[INFO] Submitted login form")

            WebDriverWait(driver, 20).until(
                EC.any_of(
                    EC.url_contains("dashboard"),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Dashboard') or contains(text(), 'Welcome')]")),
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Sunday')]"))
                )
            )
            print("[INFO] Login successful. URL:", driver.current_url)
            driver.save_screenshot(f"{screenshot_dir}/login_success.png")
            return True
        except TimeoutException:
            print(f"[ERROR] Login failed in attempt {attempt + 1}")
            driver.save_screenshot(f"{screenshot_dir}/login_attempt_{attempt + 1}_failed.png")

    print("[ERROR] All login attempts failed")
    driver.save_screenshot(f"{screenshot_dir}/login_failed.png")
    return False

# Book parking for the next available Sunday
def book_parking(driver):
    try:
        # Wait for dashboard to be fully interactive
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'app-body') and not(contains(@class, 'loading'))]"))
        )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("window.scrollTo(0, 0);")
        print("[INFO] Dashboard loaded")
        driver.save_screenshot(f"{screenshot_dir}/dashboard.png")

        # Calculate target Sunday (today or next Sunday)
        today = datetime.now()
        days_to_sunday = (6 - today.weekday()) % 7
        target_sunday_date = today if days_to_sunday == 0 else today + timedelta(days=days_to_sunday)
        target_date_str = target_sunday_date.strftime("%Y-%m-%d")  # Primary format
        alt_date_str = target_sunday_date.strftime("%B %d, %Y")  # Alternative format

        sunday_elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'Sunday')]")
        if not sunday_elements:
            print("[ERROR] No Sunday elements found")
            driver.save_screenshot(f"{screenshot_dir}/sundays_not_found.png")
            return False

        print(f"[INFO] Found {len(sunday_elements)} Sunday elements")
        target_sunday = None
        for sunday in sunday_elements:
            try:
                date_element = sunday.find_element(By.XPATH, "./preceding-sibling::*[contains(@class, 'date')] | ./parent::*/span[contains(@class, 'date')]")
                date_text = date_element.text.strip()
                print(f"[INFO] Sunday date: {date_text}")
                if target_date_str in date_text or alt_date_str in date_text:
                    target_sunday = sunday
                    break
            except NoSuchElementException:
                print("[INFO] No date found for Sunday element")

        if not target_sunday:
            print(f"[ERROR] No matching Sunday element found for date: {target_date_str} or {alt_date_str}")
            # Fallback: Try next Sunday
            next_sunday_date = target_sunday_date + timedelta(days=7)
            target_date_str = next_sunday_date.strftime("%Y-%m-%d")
            alt_date_str = next_sunday_date.strftime("%B %d, %Y")
            for sunday in sunday_elements:
                try:
                    date_element = sunday.find_element(By.XPATH, "./preceding-sibling::*[contains(@class, 'date')] | ./parent::*/span[contains(@class, 'date')]")
                    date_text = date_element.text.strip()
                    if target_date_str in date_text or alt_date_str in date_text:
                        target_sunday = sunday
                        print(f"[INFO] Fallback to next Sunday: {date_text}")
                        break
                except NoSuchElementException:
                    continue

        if not target_sunday:
            print(f"[ERROR] No matching Sunday element found for fallback date: {target_date_str}")
            driver.save_screenshot(f"{screenshot_dir}/sunday_not_found.png")
            return False

        reserve_button_locators = [
            (By.XPATH, "//button[contains(translate(text(), 'RESERVE', 'reserve'), 'reserve')]"),
            (By.CLASS_NAME, "md-btn.md-flat.m-r"),
            (By.XPATH, ".//ancestor::div[contains(@class, 'r-t') or contains(@class, 'lter-2')]/descendant::div[contains(@class, 'pull-right') and contains(@class, 'p-a-sm')]/button[contains(@class, 'md-btn md-flat m-r') and contains(translate(text(), 'RESERVE', 'reserve'), 'reserve')]"),
            (By.XPATH, ".//ancestor::div[contains(@class, 'r-t') or contains(@class, 'lter-2')]/descendant::div[contains(@class, 'pull-right')]/button[contains(@class, 'md-btn md-flat m-r') and contains(translate(text(), 'RESERVE', 'reserve'), 'reserve')]"),
        ]

        reserve_button = None
        for by, value in reserve_button_locators:
            try:
                reserve_button = target_sunday.find_element(by, value)
                if reserve_button:
                    if reserve_button.get_attribute("disabled") or "disabled" in reserve_button.get_attribute("class").lower():
                        print("[INFO] Reserve button is disabled for this Sunday")
                        continue
                    print(f"[INFO] Found reserve button: {value}")
                    break
            except NoSuchElementException:
                print(f"[INFO] Reserve button not found with locator: {value}")

        if not reserve_button:
            print("[ERROR] Reserve button not found or all buttons disabled")
            driver.save_screenshot(f"{screenshot_dir}/reserve_not_found.png")
            return False

        reserve_button.click()
        print("[INFO] Clicked reserve button")
        driver.save_screenshot(f"{screenshot_dir}/reserve_clicked.png")

        try:
            confirm_button = safe_find(
                driver,
                By.XPATH,
                "//button[contains(translate(text(), 'CONFIRMOKSUBMIT',
