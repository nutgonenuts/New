import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Credentials from GitHub Secrets ---
EMAIL = os.getenv("PARKALOT_EMAIL")
PASSWORD = os.getenv("PARKALOT_PASSWORD")

# --- Chrome Setup for GitHub Actions ---
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

try:
    print("Opening Parkalot login page...")
    driver.get("https://app.parkalot.io/#/login")

    # --- Login ---
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
    driver.find_element(By.NAME, "email").send_keys(EMAIL)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[contains(text(),'LOG IN')]").click()
    print("Logging in...")

    WebDriverWait(driver, 10).until(EC.url_contains("dashboard"))
    print("Login successful!")

    # --- Booking ---
    print("Looking for booking options...")
    time.sleep(5)  # Wait for the booking page to fully load

    booking_buttons = driver.find_elements(By.XPATH, "//button[contains(text(),'Book')]")
    if not booking_buttons:
        print("No available booking slots found.")
    else:
        for btn in booking_buttons:
            try:
                btn.click()
                print("Booked a slot!")
                time.sleep(1)
            except Exception as e:
                print(f"Failed to book a slot: {e}")

    print("Booking process completed.")

finally:
    driver.quit()
