from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

try:
    driver.get("YOUR_BOOKING_PAGE_URL")
    print("Page loaded.")

    # Click the first RESERVE button
    reserve_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'RESERVE')]"))
    )
    reserve_button.click()
    print("Clicked first RESERVE button.")

    # Wait to ensure modal is open
    time.sleep(3)

    # Save screenshot for debugging
    driver.save_screenshot("modal_debug.png")
    print("Saved modal screenshot.")

    # Click the modal RESERVE button using JS (more reliable)
    modal_reserve_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'RESERVE')]"))
    )
    driver.execute_script("arguments[0].click();", modal_reserve_button)
    print("Clicked modal RESERVE button.")

    time.sleep(3)

finally:
    driver.quit()
