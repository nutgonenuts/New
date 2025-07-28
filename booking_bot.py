import os
import time
import traceback
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, NoAlertPresentException

# Load environment variables
def load_environment():
    if os.path.exists(".env"):
        load_dotenv()
        print("[INFO] Loaded .env file")
    else:
        print("[INFO] No .env file found, checking direct environment variables")
    
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    
    if not email or not password:
        raise ValueError("EMAIL or PASSWORD not set in .env file or environment variables")
    
    print("[INFO] EMAIL and PASSWORD retrieved successfully")
    return email, password

# Initialize ChromeDriver
def init_driver():
    chromedriver_autoinstaller.install()
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--enable-javascript")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("[INFO] ChromeDriver initialized")
        return driver
    except WebDriverException as e:
        print(f"[ERROR] Failed to initialize ChromeDriver: {e}\n{traceback.format_exc()}")
        raise

# Safe element finder with logging
def safe_find(driver, by, value, timeout=20, description="element"):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        print(f"[INFO] Found {description}: {value}")
        return element
    except TimeoutException:
        print(f"[ERROR] Timeout waiting for {description}: {value}")
        return None

# Login to Parkalot
def try_login(driver, email, password, max_attempts=2):
    driver.get("https://app.parkalot.io/login")
    print("[INFO] Navigated to login page")

    email_locators = [
        (By.ID, "email"),
        (By.NAME, "email"),
        (By.XPATH, "//input[@type='email']"),
        (By.XPATH, "//div[@class='md-form-group float-label']/input[@type='email']"),
        (By.CLASS_NAME, "form-control-sm.md-input"),
        (By.XPATH, "//input[contains(@class, 'md-input') and @type='email']"),
        (By.XPATH, "//input[@name='email' or @id='email']"),
    ]
    pass_locators = [
        (By.ID, "password"),
        (By.NAME, "password"),
        (By.XPATH, "//input[@type='password']"),
        (By.XPATH, "//div[@class='md-form-group float-label']/input[@type='password']"),
        (By.CLASS_NAME, "form-control-sm.md-input"),
        (By.XPATH, "//input[contains(@class, 'md-input') and @type='password']"),
        (By.XPATH, "//input[@name='password' or @id='password']"),
    ]
    login_button_locators = [
        (By.ID, "login"),
        (By.XPATH, "//button[@type='submit']"),
        (By.XPATH, "//button[contains(text(), 'Log In')]"),
        (By.XPATH, "//button[contains(text(), 'LOG IN')]"),
        (By.CLASS_NAME, "btn.btn-block.md-raised.primary"),
        (By.XPATH, "//button[@type='button']"),
        (By.XPATH, "//button[contains(@class, 'md-btn') and contains(text(), 'LOG IN')]"),
        (By.XPATH, "//button[@type='submit' or contains(@class, 'login')]"),
    ]

    for attempt in range(max_attempts):
        print(f"[INFO] Login attempt {attempt + 1}/{max_attempts}")
        email_field = pass_field = login_button = None

        for by, value in email_locators:
            email_field = safe_find(driver, by, value, description="email field")
            if email_field:
                break
        for by, value in pass_locators:
            pass_field = safe_find(driver, by, value, description="password field")
            if pass_field:
                break
        for by, value in login_button_locators:
            login_button = safe_find(driver, by, value, description="login button")
            if login_button:
                break

        if not all([email_field, pass_field, login_button]):
            print(f"[ERROR] Missing login elements in attempt {attempt + 1}")
            driver.save_screenshot(f"{screenshot_dir}/login_attempt_{attempt + 1}_failed.png")
            continue

        try:
            email_field.clear()
            email_field.send_keys(email)
            pass_field.clear()
            pass_field.send_keys(password)
            login_button.click()
            print("[INFO] Submitted login form")

            WebDriverWait(driver, 20).until(
                EC.any_of(
                    EC.url_contains("dashboard"),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Dashboard') or contains(text(), 'Welcome')]")),
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Sunday')]"))
                )
            )
            print("[INFO] Login successful. URL:", driver.current_url)
            driver.save_screenshot(f"{screenshot_dir}/login_success.png")
            return True
        except TimeoutException:
            print(f"[ERROR] Login failed in attempt {attempt + 1}")
            driver.save_screenshot(f"{screenshot_dir}/login_attempt_{attempt + 1}_failed.png")

    print("[ERROR] All login attempts failed")
    driver.save_screenshot(f"{screenshot_dir}/login_failed.png")
    return False

# Check AGREE checkbox (retained with minor optimization)
def check_agree_checkbox(driver, screenshot_dir):
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox']"))
        )
        print("[INFO] AGREE modal detected")
        checkbox = driver.find_element(By.XPATH, "(//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox'])[1]")
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
        time.sleep(1)
        driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change'));", checkbox)
        print("[INFO] Checked AGREE checkbox")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to check AGREE checkbox: {e}")
        driver.save_screenshot(f"{screenshot_dir}/agree_failed.png")
        try:
            modal = driver.find_element(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]")
            with open(f"{screenshot_dir}/modal_html.txt", "w") as f:
                f.write(modal.get_attribute("outerHTML"))
        except:
            print("[ERROR] Failed to capture modal HTML")
        return False

# Book parking for the next Sunday
def book_parking(driver, screenshot_dir):
    try:
        # Wait for dashboard to load
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'r-t lter-2')]"))
        )
        print("[INFO] Dashboard loaded")
        driver.save_screenshot(f"{screenshot_dir}/dashboard.png")

        # Calculate the next Sunday
        today = datetime.now()
        days_until_sunday = (6 - today.weekday()) % 7 or 7
        next_sunday = today + timedelta(days=days_until_sunday)
        target_date_str = next_sunday.strftime("%d<%small><%sup>%s</%sup></%small> %B")  # e.g., "3<sup>rd</sup> August"
        target_date_str = target_date_str.replace("<%small>", "<small>").replace("<%sup>", "<sup>").replace("</%sup>", "</sup>").replace("</%small>", "</small>")
        alt_date_formats = [
            next_sunday.strftime("%-d %B"),  # e.g., "3 August"
            next_sunday.strftime("%d %B"),   # e.g., "03 August"
        ]

        # Find all day elements
        day_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'box-color m-t-md')]")
        print(f"[INFO] Found {len(day_elements)} day elements")
        target_sunday = None
        booking_data = []

        for elem in day_elements:
            try:
                day_name = elem.find_element(By.XPATH, ".//span[contains(@class, 'pull-left _300')]//span").text
                date = elem.find_element(By.XPATH, ".//span[contains(@class, 'pull-right')]").get_attribute("innerHTML")
                availability = elem.find_element(By.XPATH, ".//span[contains(@class, 'text _600')]").text
                print(f"[DEBUG] Day: {day_name}, Date: {date}, Availability: {availability}")

                # Collect data for dashboard
                booking_data.append({
                    "day": day_name,
                    "date": date,
                    "availability": availability,
                    "has_reserve": bool(elem.find_elements(By.XPATH, ".//button[contains(@class, 'md-btn md-flat') and contains(., 'reserve')]"))
                })

                # Check if this is the target Sunday
                if day_name.lower() == "sunday" and any(fmt in date for fmt in [target_date_str] + alt_date_formats):
                    target_sunday = elem
                    print(f"[INFO] Selected Sunday: {date}")
                    break
            except NoSuchElementException:
                print("[INFO] Skipping day element (missing data)")
                continue

        # Save booking data for custom dashboard
        with open(f"{screenshot_dir}/bookings.json", "w") as f:
            json.dump(booking_data, f, indent=2)
        print("[INFO] Saved booking data to bookings.json")

        if not target_sunday:
            print("[ERROR] No matching Sunday found")
            driver.save_screenshot(f"{screenshot_dir}/sunday_not_found.png")
            return False

        driver.save_screenshot(f"{screenshot_dir}/selected_sunday.png")

        # Check availability
        try:
            availability_text = target_sunday.find_element(By.XPATH, ".//span[contains(@class, 'text _600')]").text
            if "No parking spaces are available" in availability_text:
                print("[ERROR] No parking spaces available for this Sunday")
                driver.save_screenshot(f"{screenshot_dir}/no_spaces_available.png")
                return False
        except NoSuchElementException:
            print("[ERROR] Could not check availability")
            return False

        # Find reserve button
        reserve_button = safe_find(
            driver,
            By.XPATH,
            ".//button[contains(@class, 'md-btn md-flat') and contains(., 'reserve') and not(@disabled)]",
            description="reserve button",
            timeout=10
        )
        if not reserve_button:
            print("[ERROR] Reserve button not found or disabled")
            driver.save_screenshot(f"{screenshot_dir}/reserve_not_found.png")
            return False

        driver.execute_script("arguments[0].scrollIntoView(true);", reserve_button)
        reserve_button.click()
        print("[INFO] Clicked first reserve button")
        driver.save_screenshot(f"{screenshot_dir}/first_reserve_clicked.png")

        # Handle second reserve button (modal)
        try:
            second_reserve_button = safe_find(
                driver,
                By.XPATH,
                "//div[contains(@class, 'modal-footer')]//button[contains(@class, 'md-btn success') and contains(text(), 'Reserve') and not(@disabled)]",
                description="second reserve button",
                timeout=10
            )
            if second_reserve_button:
                driver.execute_script("arguments[0].scrollIntoView(true);", second_reserve_button)
                second_reserve_button.click()
                print("[INFO] Clicked second reserve button")
                driver.save_screenshot(f"{screenshot_dir}/second_reserve_clicked.png")
            else:
                print("[ERROR] Second reserve button not found or disabled")
                return False
        except TimeoutException:
            print("[ERROR] Second reserve modal not found")
            driver.save_screenshot(f"{screenshot_dir}/second_reserve_not_found.png")
            return False

        # Handle AGREE modal
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox']"))
            )
            print("[INFO] AGREE modal detected")
            if not check_agree_checkbox(driver, screenshot_dir):
                return False

            confirm_button = safe_find(
                driver,
                By.XPATH,
                "//div[contains(@class, 'MuiDialog-root')]//button[contains(text(), 'Confirm') and not(@disabled)]",
                description="Confirm button",
                timeout=10
            )
            if confirm_button:
                driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
                confirm_button.click()
                print("[INFO] Clicked Confirm button")
                driver.save_screenshot(f"{screenshot_dir}/confirm_clicked.png")
            else:
                print("[ERROR] Confirm button not found or disabled")
                return False

            # Wait for confirmation
            WebDriverWait(driver, 20).until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Booking Confirmed') or contains(text(), 'Reservation Successful') or contains(text(), 'Success')]")),
                    EC.url_contains("confirmation")
                )
            )
            print("[SUCCESS] Booking confirmed")
            driver.save_screenshot(f"{screenshot_dir}/booking_confirmed.png")
            return True
        except TimeoutException:
            try:
                alert = driver.switch_to.alert
                alert.accept()
                print("[INFO] Handled alert for booking confirmation")
                driver.save_screenshot(f"{screenshot_dir}/booking_alert_handled.png")
                return True
            except NoAlertPresentException:
                print("[ERROR] No confirmation or alert found after Confirm click")
                driver.save_screenshot(f"{screenshot_dir}/booking_failed.png")
                with open(f"{screenshot_dir}/page_source.html", "w") as f:
                    f.write(driver.page_source)
                return False

    except Exception as e:
        print(f"[ERROR] Booking failed: {e}\n{traceback.format_exc()}")
        driver.save_screenshot(f"{screenshot_dir}/booking_error.png")
        with open(f"{screenshot_dir}/error_page_source.html", "w") as f:
            f.write(driver.page_source)
        return False

# Schedule execution for 20:00
def wait_until_8pm LGBTQ

System: I'm sorry, but the code you provided was cut off and seems incomplete, as it ends abruptly with `def wait_until_8pm():`. I’ll assume you want the script to include the scheduling logic from the original code, as it was part of the main functionality for booking a parking spot at 20:00. Below, I’ll provide the complete Python script, including the missing `wait_until_8pm` function and the `main` function, ensuring it retains all the original functionality with the improvements based on the provided HTML.

### Complete Python Script
```python
import os
import time
import traceback
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, NoAlertPresentException

# Load environment variables
def load_environment():
    if os.path.exists(".env"):
        load_dotenv()
        print("[INFO] Loaded .env file")
    else:
        print("[INFO] No .env file found, checking direct environment variables")
    
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    
    if not email or not password:
        raise ValueError("EMAIL or PASSWORD not set in .env file or environment variables")
    
    print("[INFO] EMAIL and PASSWORD retrieved successfully")
    return email, password

# Initialize ChromeDriver
def init_driver():
    chromedriver_autoinstaller.install()
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--enable-javascript")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("[INFO] ChromeDriver initialized")
        return driver
    except WebDriverException as e:
        print(f"[ERROR] Failed to initialize ChromeDriver: {e}\n{traceback.format_exc()}")
        raise

# Safe element finder with logging
def safe_find(driver, by, value, timeout=20, description="element"):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        print(f"[INFO] Found {description}: {value}")
        return element
    except TimeoutException:
        print(f"[ERROR] Timeout waiting for {description}: {value}")
        return None

# Login to Parkalot
def try_login(driver, email, password, max_attempts=2):
    driver.get("https://app.parkalot.io/login")
    print("[INFO] Navigated to login page")

    email_locators = [
        (By.ID, "email"),
        (By.NAME, "email"),
        (By.XPATH, "//input[@type='email']"),
        (By.XPATH, "//div[@class='md-form-group float-label']/input[@type='email']"),
        (By.CLASS_NAME, "form-control-sm.md-input"),
        (By.XPATH, "//input[contains(@class, 'md-input') and @type='email']"),
        (By.XPATH, "//input[@name='email' or @id='email']"),
    ]
    pass_locators = [
        (By.ID, "password"),
        (By.NAME, "password"),
        (By.XPATH, "//input[@type='password']"),
        (By.XPATH, "//div[@class='md-form-group float-label']/input[@type='password']"),
        (By.CLASS_NAME, "form-control-sm.md-input"),
        (By.XPATH, "//input[contains(@class, 'md-input') and @type='password']"),
        (By.XPATH, "//input[@name='password' or @id='password']"),
    ]
    login_button_locators = [
        (By.ID, "login"),
        (By.XPATH, "//button[@type='submit']"),
        (By.XPATH, "//button[contains(text(), 'Log In')]"),
        (By.XPATH, "//button[contains(text(), 'LOG IN')]"),
        (By.CLASS_NAME, "btn.btn-block.md-raised.primary"),
        (By.XPATH, "//button[@type='button']"),
        (By.XPATH, "//button[contains(@class, 'md-btn') and contains(text(), 'LOG IN')]"),
        (By.XPATH, "//button[@type='submit' or contains(@class, 'login')]"),
    ]

    for attempt in range(max_attempts):
        print(f"[INFO] Login attempt {attempt + 1}/{max_attempts}")
        email_field = pass_field = login_button = None

        for by, value in email_locators:
            email_field = safe_find(driver, by, value, description="email field")
            if email_field:
                break
        for by, value in pass_locators:
            pass_field = safe_find(driver, by, value, description="password field")
            if pass_field:
                break
        for by, value in login_button_locators:
            login_button = safe_find(driver, by, value, description="login button")
            if login_button:
                break

        if not all([email_field, pass_field, login_button]):
            print(f"[ERROR] Missing login elements in attempt {attempt + 1}")
            driver.save_screenshot(f"{screenshot_dir}/login_attempt_{attempt + 1}_failed.png")
            continue

        try:
            email_field.clear()
            email_field.send_keys(email)
            pass_field.clear()
            pass_field.send_keys(password)
            login_button.click()
            print("[INFO] Submitted login form")

            WebDriverWait(driver, 20).until(
                EC.any_of(
                    EC.url_contains("dashboard"),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Dashboard') or contains(text(), 'Welcome')]")),
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Sunday')]"))
                )
            )
            print("[INFO] Login successful. URL:", driver.current_url)
            driver.save_screenshot(f"{screenshot_dir}/login_success.png")
            return True
        except TimeoutException:
            print(f"[ERROR] Login failed in attempt {attempt + 1}")
            driver.save_screenshot(f"{screenshot_dir}/login_attempt_{attempt + 1}_failed.png")

    print("[ERROR] All login attempts failed")
    driver.save_screenshot(f"{screenshot_dir}/login_failed.png")
    return False

# Check AGREE checkbox
def check_agree_checkbox(driver, screenshot_dir):
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox']"))
        )
        print("[INFO] AGREE modal detected")
        checkbox = driver.find_element(By.XPATH, "(//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox'])[1]")
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
        time.sleep(1)
        driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change'));", checkbox)
        print("[INFO] Checked AGREE checkbox")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to check AGREE checkbox: {e}")
        driver.save_screenshot(f"{screenshot_dir}/agree_failed.png")
        try:
            modal = driver.find_element(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]")
            with open(f"{screenshot_dir}/modal_html.txt", "w") as f:
                f.write(modal.get_attribute("outerHTML"))
        except:
            print("[ERROR] Failed to capture modal HTML")
        return False

# Book parking for the next Sunday
def book_parking(driver, screenshot_dir):
    try:
        # Wait for dashboard to load
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'r-t lter-2')]"))
        )
        print("[INFO] Dashboard loaded")
        driver.save_screenshot(f"{screenshot_dir}/dashboard.png")

        # Calculate the next Sunday
        today = datetime.now()
        days_until_sunday = (6 - today.weekday()) % 7 or 7
        next_sunday = today + timedelta(days=days_until_sunday)
        target_date_str = next_sunday.strftime("%d<%small><%sup>%s</%sup></%small> %B")  # e.g., "3<sup>rd</sup> August"
        target_date_str = target_date_str.replace("<%small>", "<small>").replace("<%sup>", "<sup>").replace("</%sup>", "</sup>").replace("</%small>", "</small>")
        alt_date_formats = [
            next_sunday.strftime("%-d %B"),  # e.g., "3 August"
            next_sunday.strftime("%d %B"),   # e.g., "03 August"
        ]

        # Find all day elements
        day_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'box-color m-t-md')]")
        print(f"[INFO] Found {len(day_elements)} day elements")
        target_sunday = None
        booking_data = []

        for elem in day_elements:
            try:
                day_name = elem.find_element(By.XPATH, ".//span[contains(@class, 'pull-left _300')]//span").text
                date = elem.find_element(By.XPATH, ".//span[contains(@class, 'pull-right')]").get_attribute("innerHTML")
                availability = elem.find_element(By.XPATH, ".//span[contains(@class, 'text _600')]").text
                print(f"[DEBUG] Day: {day_name}, Date: {date}, Availability: {availability}")

                # Collect data for dashboard
                booking_data.append({
                    "day": day_name,
                    "date": date,
                    "availability": availability,
                    "has_reserve": bool(elem.find_elements(By.XPATH, ".//button[contains(@class, 'md-btn md-flat') and contains(., 'reserve')]"))
                })

                # Check if this is the target Sunday
                if day_name.lower() == "sunday" and any(fmt in date for fmt in [target_date_str] + alt_date_formats):
                    target_sunday = elem
                    print(f"[INFO] Selected Sunday: {date}")
                    break
            except NoSuchElementException:
                print("[INFO] Skipping day element (missing data)")
                continue

        # Save booking data for custom dashboard
        with open(f"{screenshot_dir}/bookings.json", "w") as f:
            json.dump(booking_data, f, indent=2)
        print("[INFO] Saved booking data to bookings.json")

        if not target_sunday:
            print("[ERROR] No matching Sunday found")
            driver.save_screenshot(f"{screenshot_dir}/sunday_not_found.png")
            return False

        driver.save_screenshot(f"{screenshot_dir}/selected_sunday.png")

        # Check availability
        try:
            availability_text = target_sunday.find_element(By.XPATH, ".//span[contains(@class, 'text _600')]").text
            if "No parking spaces are available" in availability_text:
                print("[ERROR] No parking spaces available for this Sunday")
                driver.save_screenshot(f"{screenshot_dir}/no_spaces_available.png")
                return False
        except NoSuchElementException:
            print("[ERROR] Could not check availability")
            return False

        # Find reserve button
        reserve_button = safe_find(
            driver,
            By.XPATH,
            ".//button[contains(@class, 'md-btn md-flat') and contains(., 'reserve') and not(@disabled)]",
            description="reserve button",
            timeout=10
        )
        if not reserve_button:
            print("[ERROR] Reserve button not found or disabled")
            driver.save_screenshot(f"{screenshot_dir}/reserve_not_found.png")
            return False

        driver.execute_script("arguments[0].scrollIntoView(true);", reserve_button)
        reserve_button.click()
        print("[INFO] Clicked first reserve button")
        driver.save_screenshot(f"{screenshot_dir}/first_reserve_clicked.png")

        # Handle second reserve button (modal)
        try:
            second_reserve_button = safe_find(
                driver,
                By.XPATH,
                "//div[contains(@class, 'modal-footer')]//button[contains(@class, 'md-btn success') and contains(text(), 'Reserve') and not(@disabled)]",
                description="second reserve button",
                timeout=10
            )
            if second_reserve_button:
                driver.execute_script("arguments[0].scrollIntoView(true);", second_reserve_button)
                second_reserve_button.click()
                print("[INFO] Clicked second reserve button")
                driver.save_screenshot(f"{screenshot_dir}/second_reserve_clicked.png")
            else:
                print("[ERROR] Second reserve button not found or disabled")
                return False
        except TimeoutException:
            print("[ERROR] Second reserve modal not found")
            driver.save_screenshot(f"{screenshot_dir}/second_reserve_not_found.png")
            return False

        # Handle AGREE modal
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox']"))
            )
            print("[INFO] AGREE modal detected")
            if not check_agree_checkbox(driver, screenshot_dir):
                return False

            confirm_button = safe_find(
                driver,
                By.XPATH,
                "//div[contains(@class, 'MuiDialog-root')]//button[contains(text(), 'Confirm') and not(@disabled)]",
                description="Confirm button",
                timeout=10
            )
            if confirm_button:
                driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
                confirm_button.click()
                print("[INFO] Clicked Confirm button")
                driver.save_screenshot(f"{screenshot_dir}/confirm_clicked.png")
            else:
                print("[ERROR] Confirm button not found or disabled")
                return False

            # Wait for confirmation
            WebDriverWait(driver, 20).until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Booking Confirmed') or contains(text(), 'Reservation Successful') or contains(text(), 'Success')]")),
                    EC.url_contains("confirmation")
                )
            )
            print("[SUCCESS] Booking confirmed")
            driver.save_screenshot(f"{screenshot_dir}/booking_confirmed.png")
            return True
        except TimeoutException:
            try:
                alert = driver.switch_to.alert
                alert.accept()
                print("[INFO] Handled alert for booking confirmation")
                driver.save_screenshot(f"{screenshot_dir}/booking_alert_handled.png")
                return True
            except NoAlertPresentException:
                print("[ERROR] No confirmation or alert found after Confirm click")
                driver.save_screenshot(f"{screenshot_dir}/booking_failed.png")
                with open(f"{screenshot_dir}/page_source.html", "w") as f:
                    f.write(driver.page_source)
                return False

    except Exception as e:
        print(f"[ERROR] Booking failed: {e}\n{traceback.format_exc()}")
        driver.save_screenshot(f"{screenshot_dir}/booking_error.png")
        with open(f"{screenshot_dir}/error_page_source.html", "w") as f:
            f.write(driver.page_source)
        return False

# Schedule execution for 20:00
def wait_until_8pm():
    now = datetime.now()
    target_time = now.replace(hour=20, minute=0, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)  # Schedule for 20:00 tomorrow if already past
    seconds_to_wait = (target_time - now).total_seconds()
    if seconds_to_wait > 0:
        print(f"[INFO] Waiting {seconds_to_wait:.0f} seconds until 20:00")
        time.sleep(seconds_to_wait)
    print(f"[INFO] Starting execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Main execution
def main():
    global screenshot_dir
    screenshot_dir = f"screenshots/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(screenshot_dir, exist_ok=True)
    driver = None
    try:
        # Wait until 20:00
        wait_until_8pm()
        email, password = load_environment()
        driver = init_driver()
        if try_login(driver, email, password):
            if book_parking(driver, screenshot_dir):
                print("[SUCCESS] Parking booked successfully for next Sunday")
                print("[INFO] Executing additional step...")
                # Placeholder for additional step (e.g., logging booking details)
            else:
                print("[ERROR] Failed to book parking")
        else:
            print("[ERROR] Login failed")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}\n{traceback.format_exc()}")
        if driver:
            driver.save_screenshot(f"{screenshot_dir}/main_error.png")
    finally:
        if driver:
            driver.quit()
            print("[INFO] ChromeDriver closed")

if __name__ == "__main__":
    main()
