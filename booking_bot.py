import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def take_screenshot(driver, name="screenshot"):
    path = f"{name}.png"
    driver.save_screenshot(path)
    print(f"[DEBUG] Screenshot saved: {path}")

print("[DEBUG] Starting Parkalot Booking Bot...")

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')  # Remove this if you want to see the browser
options.add_argument('--window-size=1920,1080')

try:
    driver = webdriver.Chrome(options=options)
    print("[DEBUG] Chrome started successfully.")
except Exception as e:
    print("[ERROR] Failed to start Chrome:", e)
    exit(1)

try:
    driver.get("https://app.parkalot.io/")
    print("[DEBUG] Opened Parkalot website.")
    time.sleep(5)
    take_screenshot(driver, "step1_home")

    # Example: Click "Reserve" button (adjust selector as needed)
    reserve_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'RESERVE')]")
    if reserve_buttons:
        reserve_buttons[0].click()
        print("[DEBUG] Clicked the first Reserve button.")
        time.sleep(3)
        take_screenshot(driver, "step2_reserve")
    else:
        print("[ERROR] No Reserve buttons found.")
        take_screenshot(driver, "step_error_no_reserve")
        driver.quit()
        exit(1)

    # Example: Click "Reserve" in the modal (adjust selector)
    confirm_button = driver.find_element(By.XPATH, "//button[contains(., 'RESERVE')]")
    confirm_button.click()
    print("[DEBUG] Clicked confirm Reserve.")
    time.sleep(3)
    take_screenshot(driver, "step3_confirm")

    print("[SUCCESS] Booking attempt completed.")
except Exception as e:
    print("[ERROR] Exception during booking:", e)
    take_screenshot(driver, "step_error")
finally:
    driver.quit()
    print("[DEBUG] Browser closed.")
