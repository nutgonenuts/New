import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# --- Configuration ---
USER_EMAIL = os.getenv("PARKALOT_EMAIL", "your-email@example.com")
USER_PASSWORD = os.getenv("PARKALOT_PASSWORD", "your-password")
BASE_URL = "https://your-parkalot-login-url.com"

# --- Chrome Setup ---
print("[DEBUG] Setting up Chrome driver...")
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Create screenshot directory
os.makedirs("screenshots", exist_ok=True)

def save_screenshot(step_name):
    filename = f"screenshots/{step_name}.png"
    driver.save_screenshot(filename)
    print(f"[DEBUG] Screenshot saved: {filename}")

try:
    # --- Step 1: Open Website ---
    print("[DEBUG] Opening Parkalot website...")
    driver.get(BASE_URL)
    time.sleep(2)
    save_screenshot("step1_home")

    # --- Step 2: Login ---
    print("[DEBUG] Entering login credentials...")
    driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(USER_EMAIL)
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(USER_PASSWORD)
    save_screenshot("step2_before_login")

    print("[DEBUG] Clicking login button...")
    driver.find_element(By.XPATH, "//button[contains(text(),'LOG IN')]").click()
    time.sleep(3)
    save_screenshot("step3_after_login")

    if "login" in driver.current_url.lower():
        print("[ERROR] Login failed. Still on login page.")
        save_screenshot("error_login_failed")
        raise Exception("Login failed")

    print("[DEBUG] Successfully logged in!")

    # --- Step 3: Find Reserve Button ---
    print("[DEBUG] Searching for Reserve button...")
    reserve_buttons = driver.find_elements(By.XPATH, "//button[contains(text(),'Reserve')]")
    if not reserve_buttons:
        print("[ERROR] No Reserve buttons found.")
        save_screenshot("error_no_reserve")
        raise Exception("No Reserve buttons found")

    print(f"[DEBUG] Found {len(reserve_buttons)} Reserve button(s). Clicking the first one...")
    reserve_buttons[0].click()
    time.sleep(2)
    save_screenshot("step4_reserved")

    print("[DEBUG] Booking successful!")

except Exception as e:
    print(f"[ERROR] {e}")

finally:
    print("[DEBUG] Closing browser.")
    driver.quit()
