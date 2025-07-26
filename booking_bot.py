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
    chromedriver_autoinstaller.install()  # Ensure compatibility with Chrome 138.0.7204.157
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")  # Improves headless rendering
    chrome_options.add_argument("--start-maximized")  # Ensures full viewport
    chrome_options.add_argument("--enable-javascript")  # Explicitly enable JS
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
def safe_find(driver, by, value, timeout=20):
    try:
        return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))
    except TimeoutException:
        print(f"[ERROR] Element not visible: {value}")
        return None

# --- Login attempt with multiple strategies ---
def try_login(driver, email, password):
    driver.get("https://app.parkalot.io/login")
    print("[DEBUG] Opened Parkalot website.")
    time.sleep(50)  # Increased to 50 seconds for JS rendering
    form = driver.execute_script("return document.querySelector('form');")
    if form:
        driver.execute_script("arguments[0].style.display = 'block';", form)
    else:
        driver.refresh()  # Retry if form not found
        time.sleep(15)  # Additional wait after refresh
        form = driver.execute_script("return document.querySelector('form');")
        if form:
            driver.execute_script("arguments[0].style.display = 'block';", form)
        else:
            driver.execute_script("document.body.innerHTML += '<style>form { display: block !important; }</style>';")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "form")))  # Wait for form

    email_locators = [
        (By.XPATH, "//div[@class='md-form-group float-label']/input[@type='email']"),
        (By.CLASS_NAME, "form-control-sm md-input"),
        (By.XPATH, "//input[@type='email']"),
        (By.XPATH, "//input[contains(@class, 'md-input') and @type='email']"),  # Fallback
        (By.XPATH, "//input[@name='email' or @id='email']")  # Additional fallback
    ]
    pass_locators = [
        (By.XPATH, "//div[@class='md-form-group float-label']/input[@type='password']"),
        (By.CLASS_NAME, "form-control-sm md-input"),
        (By.XPATH, "//input[@type='password']"),
        (By.XPATH, "//input[contains(@class, 'md-input') and @type='password']"),  # Fallback
        (By.XPATH, "//input[@name='password' or @id='password']")  # Additional fallback
    ]
    login_button_locators = [
        (By.XPATH, "//button[contains(text(), 'LOG IN')]"),
        (By.CLASS_NAME, "btn btn-block md-raised primary"),
        (By.XPATH, "//button[@type='button']"),
        (By.XPATH, "//button[contains(@class, 'md-btn') and contains(text(), 'LOG IN')]"),  # Fallback
        (By.XPATH, "//button[@type='submit' or contains(@class, 'login')]")  # Additional fallback
    ]

    max_attempts = 3
    for attempt in range(max_attempts):
        print(f"[DEBUG] Login attempt {attempt + 1}/{max_attempts}")
        email_field = None
        pass_field = None
        login_button = None

        for by, value in email_locators:
            email_field = safe_find(driver, by, value)
            if email_field:
                break
        for by, value in pass_locators:
            pass_field = safe_find(driver, by, value)
            if pass_field:
                break
        for by, value in login_button_locators:
            login_button = safe_find(driver, by, value)
            if login_button:
                break

        if not email_field or not pass_field or not login_button:
            print("[ERROR] Login fields not found in attempt", attempt + 1)
            driver.save_screenshot(f"screenshots/step_error_no_fields_attempt{attempt + 1}.png")
            time.sleep(2)
            continue

        email_field.send_keys(email)
        pass_field.send_keys(password)
        login_button.click()

        try:
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sunday')]")))
            print("[DEBUG] Login successful!")
            driver.save_screenshot("screenshots/step_logged_in.png")
            return True
        except TimeoutException:
            print("[ERROR] Login failed in attempt", attempt + 1)
            driver.save_screenshot(f"screenshots/step_login_failed_attempt{attempt + 1}.png")
            time.sleep(2)

    # Save screenshot after all attempts if login fails
    driver.save_screenshot("screenshots/step_login_failed.png")
    print("[DEBUG] Login validation failed, but dashboard may be reached—check screenshots.")
    return False  # Temporary return to allow manual verification

# --- Main ---
def main():
    driver = None
    try:
        driver = init_driver()
        email, password = get_credentials()
        if try_login(driver, email, password):
            print("[SUCCESS] Login completed successfully.")
        else:
            print("[FAIL] Login failed or validation issue—please verify screenshots.")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
