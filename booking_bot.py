import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

EMAIL = os.getenv("PARKALOT_EMAIL")
PASSWORD = os.getenv("PARKALOT_PASSWORD")

def save_screenshot(driver, name):
    os.makedirs("screenshots", exist_ok=True)
    driver.save_screenshot(f"screenshots/{name}.png")

def main():
    print("[DEBUG] Starting Parkalot Booking Bot...")

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get("https://app.parkalot.io")
        print("[DEBUG] Opened Parkalot website.")
        save_screenshot(driver, "step1_home")

        # Fill login form
        driver.find_element(By.NAME, "email").send_keys(EMAIL)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        save_screenshot(driver, "step2_filled_login")

        driver.find_element(By.XPATH, "//button[contains(text(), 'LOG IN')]").click()
        print("[DEBUG] Login button clicked.")
        time.sleep(5)
        save_screenshot(driver, "step3_after_login")

        # Check if login was successful
        if "login" in driver.current_url.lower():
            raise Exception("Login failed. Still on login page.")

        print("[DEBUG] Login successful.")
    except Exception as e:
        print(f"[ERROR] {e}")
        save_screenshot(driver, "step_final_error")
        exit(1)
    finally:
        driver.quit()
        print("[DEBUG] Browser closed.")

if __name__ == "__main__":
    main()
