from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Setup Chrome options
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

try:
    driver.get("YOUR_BOOKING_PAGE_URL_HERE")
    print("Page loaded.")
    
    # Wait for first RESERVE button
    reserve_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'RESERVE')]"))
    )
    reserve_button.click()
    print("Clicked first RESERVE button.")
    
    # Wait for modal RESERVE button
    modal_reserve_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'dialog')]//button[contains(., 'RESERVE')]"))
    )
    modal_reserve_button.click()
    print("Clicked modal RESERVE button. Booking should be confirmed.")

    # Optional wait to ensure booking processed
    time.sleep(2)

finally:
    driver.quit()
