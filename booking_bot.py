import chromedriver_autoinstaller
chromedriver_autoinstaller.install()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Chrome options
options = Options()
options.add_argument("--headless")  # Comment this if you want to see the browser
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    # Go to your parking booking page
    driver.get("YOUR_BOOKING_PAGE_URL_HERE")
    time.sleep(5)  # Wait for page to load

    # Look for the first "RESERVE" button and click it
    reserve_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'RESERVE')]")
    if reserve_buttons:
        reserve_buttons[0].click()
        print("Clicked RESERVE button!")
    else:
        print("No RESERVE button found.")

    time.sleep(3)

finally:
    driver.quit()
