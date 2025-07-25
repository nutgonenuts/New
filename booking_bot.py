import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Create screenshots folder
os.makedirs("screenshots", exist_ok=True)

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    print("Opening Parkalot...")
    driver.get("https://app.parkalot.io/")
    time.sleep(5)
    driver.save_screenshot("screenshots/step1_home.png")

    # TODO: Add login steps if required
    # Example:
    # driver.find_element(By.ID, "username").send_keys("your_username")
    # driver.find_element(By.ID, "password").send_keys("your_password")
    # driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    # time.sleep(3)
    # driver.save_screenshot("screenshots/step2_logged_in.png")

    print("Looking for Reserve button...")
    reserve_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'RESERVE')]")
    if reserve_buttons:
        reserve_buttons[0].click()
        time.sleep(2)
        driver.save_screenshot("screenshots/step3_reserve_clicked.png")
        print("Reserve button clicked!")
    else:
        print("No Reserve button found!")

finally:
    driver.quit()
