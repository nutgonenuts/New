import os
import time
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# --- Setup Chrome/Driver ---
def init_driver():
    print("[DEBUG] Installing matching ChromeDriver...")
    chromedriver_autoinstaller.install()

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    for attempt in range(3):
        try:
            driver = webdriver.Chrome(options=chrome_options)
            print("[DEBUG] Chrome started successfully.")
            return driver
        except Exception as e:
            print(f"[ERROR] ChromeDriver launch failed: {e}")
            time.sleep(3)
    raise RuntimeError("Failed to start Chrome after 3 attempts.")

# --- Validate secrets ---
def get_credentials():
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    print(f"[DEBUG] EMAIL set? {'YES' if email else 'NO'}")
    print(f"[DEBUG] PASSWORD set? {'YES' if password else 'NO'}")
    if not email or not password:
        raise ValueError("EMAIL or PASSWORD secret not set!")
    return email, password

# --- Safe element finder ---
def safe_find(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        return None

# --- Login attempt ---
def try_login(driver, email, password):
    driver.get("https://app.parkalot.io/login")
    print("[DEBUG] Opened Parkalot website.")
    driver.save_screenshot("step_home.png")

    email_field = safe_find(driver, By.NAME, "email")
    pass_field = safe_find(driver, By.NAME, "password")
    login_button = safe_find(driver, By.XPATH, "//button[contains(text(), 'LOG IN')]")

    if not email_field or not pass_field or not login_button:
        print("[ERROR] Login fields not found.")
        driver.save_screenshot("step_error_no_fields.png")
        return False

    email_field.send_keys(email)
    pass_field.send_keys(password)
    login_button.click()
    time.sleep(5)

    if "dashboard" in driver.current_url.lower():
        print("[DEBUG] Login successful!")
        driver.save_screenshot("step_logged_in.png")
        return True
    else:
        print("[ERROR] Login failed.")
        driver.save_screenshot("step_login_failed.png")
        return False

# --- Main ---
def main():
    driver = init_driver()
    email, password = get_credentials()

    for attempt in range(3):
        if try_login(driver, email, password):
            break
        else:
            print(f"[WARN] Login attempt {attempt+1} failed. Retrying...")
            time.sleep(3)
    else:
        print("[FATAL] Login failed after 3 attempts.")

    driver.quit()

if __name__ == "__main__":
    main()
