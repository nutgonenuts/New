from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Create screenshots directory
os.makedirs("screenshots", exist_ok=True)

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

try:
    driver.get("YOUR_BOOKING_PAGE_URL")
    driver.save_screenshot("screenshots/page_loaded.png")
    print("Saved screenshot: page_loaded.png")

    # Click first RESERVE button
    reserve_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'RESERVE')]"))
    )
    reserve_button.click()
    time.sleep(2)
    driver.save_screenshot("screenshots/modal_opened.png")
    print("Saved screenshot: modal_opened.png")

    # Click modal RESERVE button
    modal_reserve_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'RESERVE')]"))
    )
    driver.execute_script("arguments[0].click();", modal_reserve_button)
    time.sleep(2)
    driver.save_screenshot("screenshots/after_booking.png")
    print("Saved screenshot: after_booking.png")

finally:
    driver.quit()
