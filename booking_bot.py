import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

def save_screenshot(driver, name):
    driver.save_screenshot(f"screenshots/{name}.png")

def login(driver):
    print("[DEBUG] Opening Parkalot website...")
    driver.get("https://app.parkalot.io/login")
    save_screenshot(driver, "step1_home")

    print(f"[DEBUG] Email set? {'YES' if EMAIL else 'NO'}")
    print(f"[DEBUG] Password set? {'YES' if PASSWORD else 'NO'}")

    try:
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email']"))
        )
        password_field = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        email_field.clear()
        email_field.send_keys(EMAIL)
        password_field.clear()
        password_field.send_keys(PASSWORD)
        save_screenshot(driver, "step2_filled_login")

        login_button.click()
        print("[DEBUG] Login button clicked.")
    except Exception as e:
        save_screenshot(driver, "error_login")
        print(f"[ERROR] Login failed: {e}")
        raise

def verify_login(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("[DEBUG] Successfully logged in!")
        save_screenshot(driver, "step3_logged_in")
    except Exception as e:
        save_screenshot(driver, "error_login_verify")
        print(f"[ERROR] Login verification failed: {e}")
        raise

def main():
    driver = init_driver()
    try:
        login(driver)
        verify_login(driver)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        print("[DEBUG] Browser closed.")
        driver.quit()

if __name__ == "__main__":
    main()
