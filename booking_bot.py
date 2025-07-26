import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def take_screenshot(driver, name):
    os.makedirs("screenshots", exist_ok=True)
    path = os.path.join("screenshots", name)
    driver.save_screenshot(path)
    print(f"[DEBUG] Screenshot saved: {path}")

# Chrome Options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

print("[DEBUG] Starting Parkalot Booking Bot...")

try:
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://app.parkalot.io/")
    print("[DEBUG] Opened Parkalot website.")
    take_screenshot(driver, "step1_home.png")

    # Wait for page to load
    time.sleep(3)

    # Try multiple selectors for Reserve button
    reserve_button = None
    selectors = [
        "//button[contains(text(), 'Reserve')]",
        "//div[contains(@class,'reserve')]",
        "//a[contains(text(), 'Reserve')]",
        "//button[contains(@aria-label, 'Reserve')]"
    ]

    for selector in selectors:
        try:
            reserve_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            print(f"[DEBUG] Found Reserve button using selector: {selector}")
            break
        except TimeoutException:
            print(f"[DEBUG] Selector failed: {selector}")

    if not reserve_button:
        take_screenshot(driver, "step_error_no_reserve.png")
        raise Exception("No Reserve buttons found.")

    reserve_button.click()
    print("[DEBUG] Clicked Reserve button.")
    take_screenshot(driver, "step2_after_click.png")

    # Wait for confirmation or next step
    time.sleep(3)

except Exception as e:
    print(f"Error: {e}")
    take_screenshot(driver, "step_final_error.png")

finally:
    driver.quit()
    print("[DEBUG] Browser closed.")
