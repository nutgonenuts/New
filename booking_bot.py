import os
import time
import traceback
from datetime import datetime, timedelta
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
        print(f"[ERROR] Timeout waiting for {description]: {value}")
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

# Book parking for the next available Sunday
def book_parking(driver):
    try:
        # Wait for dashboard to be fully interactive
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'app-body') and not(contains(@class, 'loading'))]"))
        )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("window.scrollTo(0, 0);")
        print("[INFO] Dashboard loaded")
        driver.save_screenshot(f"{screenshot_dir}/dashboard.png")

        # Calculate target Sundays for 2-week lookahead
        today = datetime.now()
        target_dates = [today + timedelta(days=i * 7) for i in range(3)]  # Today + 2 more Sundays (2 weeks)
        target_dates = [d for d in target_dates if d >= today]  # Ensure no past dates

        sunday_elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'Sunday') and contains(@style, 'font-size: 24px')]")
        if not sunday_elements:
            print("[ERROR] No Sunday elements found")
            driver.save_screenshot(f"{screenshot_dir}/sundays_not_found.png")
            return False

        print(f"[INFO] Found {len(sunday_elements)} Sunday elements")
        target_sunday = None
        for target_date in target_dates:
            target_date_str = target_date.strftime("%Y-%m-%d")  # e.g., 2025-07-27
            alt_date_str = target_date.strftime("%B %d, %Y")   # e.g., July 27, 2025
            alt_date_str2 = target_date.strftime("%d/%m/%Y")   # e.g., 27/07/2025
            alt_date_str3 = target_date.strftime("%d %b %Y")   # e.g., 27 Jul 2025

            for sunday in sunday_elements:
                try:
                    date_element = sunday.find_element(By.XPATH, "./preceding-sibling::* | ./parent::*//span | ./ancestor::div[contains(@class, 'r-t') or contains(@class, 'lter-2')]//span[contains(@class, 'pull-left')]")
                    date_text = date_element.text.strip()
                    print(f"[INFO] Checking Sunday date: {date_text} against {target_date_str}")
                    if any(fmt in date_text for fmt in [target_date_str, alt_date_str, alt_date_str2, alt_date_str3]):
                        target_sunday = sunday
                        print(f"[INFO] Selected Sunday: {date_text} for {target_date_str}")
                        break
                except NoSuchElementException:
                    print("[INFO] No date found for Sunday element")
                if target_sunday:
                    break
            if target_sunday:
                break

        if not target_sunday:
            print(f"[ERROR] No matching Sunday element found for any date in lookahead")
            print("[INFO] Falling back to first Sunday element")
            target_sunday = sunday_elements[0] if sunday_elements else None
            if not target_sunday:
                driver.save_screenshot(f"{screenshot_dir}/sunday_not_found.png")
                return False

        # Step 1: Click first Reserve button
        reserve_button_locators = [
            (By.XPATH, "//button[@type='button' and contains(@class, 'md-btn') and contains(text(), 'reserve')]"),
            (By.CSS_SELECTOR, "button.md-btn.md-flat.m-r"),
            (By.CSS_SELECTOR, "div.pull-right.p-a-sm button:nth-child(3)"),
            (By.XPATH, ".//ancestor::div[contains(@class, 'pull-right') and contains(@class, 'p-a-sm')]/button[contains(@class, 'md-btn md-flat m-r') and contains(text(), 'reserve')]"),
            (By.XPATH, ".//ancestor::div[contains(@class, 'r-t') or contains(@class, 'lter-2')]/descendant::div[contains(@class, 'pull-right')]/button[contains(@class, 'md-btn md-flat m-r') and contains(text(), 'reserve')]"),
        ]

        reserve_button = None
        for by, value in reserve_button_locators:
            try:
                parent = target_sunday.find_element(By.XPATH, "./ancestor::div[contains(@class, 'r-t') or contains(@class, 'lter-2')]")
                reserve_button = parent.find_element(by, value)
                if reserve_button:
                    if reserve_button.get_attribute("disabled") or "disabled" in reserve_button.get_attribute("class").lower():
                        print("[INFO] Reserve button is disabled for this Sunday")
                        continue
                    print(f"[INFO] Found first reserve button: {value}, enabled: {not reserve_button.get_attribute('disabled')}")
                    break
            except NoSuchElementException:
                print(f"[INFO] First reserve button not found with locator: {value}")

        if not reserve_button:
            print("[ERROR] First reserve button not found or all buttons disabled")
            driver.save_screenshot(f"{screenshot_dir}/reserve_not_found.png")
            return False

        # Check for no spaces available before clicking
        if driver.find_elements(By.XPATH, "//*[contains(text(), 'No spaces available') or contains(text(), 'Fully booked')]"):
            print("[ERROR] No parking spaces available for this Sunday")
            driver.save_screenshot(f"{screenshot_dir}/no_spaces_available.png")
            return False

        reserve_button.click()
        print("[INFO] Clicked first reserve button")
        driver.save_screenshot(f"{screenshot_dir}/first_reserve_clicked.png")

        # Wait for second reserve option to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='animate']/div/div/div[3]/button[2]"))
        )
        print("[INFO] Second reserve option detected")

        # Step 2: Click second Reserve button
        second_reserve_button_locators = [
            (By.XPATH, "//*[@id='animate']/div/div/div[3]/button[2]"),  # Specific XPath from structure
            (By.XPATH, "/html/body/div[2]/div[1]/div[1]/div/div/div/div/div[3]/button[2]"),  # Absolute XPath
            (By.CSS_SELECTOR, "#animate > div > div > div.modal-footer > button.md-btn.success.p-x-md:nth-child(2)"),  # CSS Selector
            (By.XPATH, "//div[contains(@class, 'modal-footer')]//button[contains(@class, 'md-btn success p-x-md') and contains(text(), 'Reserve')]"),  # Generic modal footer
        ]

        second_reserve_button = None
        for by, value in second_reserve_button_locators:
            try:
                second_reserve_button = driver.find_element(by, value)
                if second_reserve_button:
                    if second_reserve_button.get_attribute("disabled") or "disabled" in second_reserve_button.get_attribute("class").lower():
                        print("[INFO] Second reserve button is disabled")
                        continue
                    print(f"[INFO] Found second reserve button: {value}, enabled: {not second_reserve_button.get_attribute('disabled')}")
                    break
            except NoSuchElementException:
                print(f"[INFO] Second reserve button not found with locator: {value}")

        if not second_reserve_button:
            print("[ERROR] Second reserve button not found or disabled")
            driver.save_screenshot(f"{screenshot_dir}/second_reserve_not_found.png")
            return False

        # Ensure the button is visible and scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", second_reserve_button)
        time.sleep(1)  # Brief wait for scroll to complete

        # Attempt to click the button, fallback to JavaScript if intercepted
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='animate']/div/div/div[3]/button[2]")))
            second_reserve_button.click()
            print("[INFO] Clicked second reserve button")
        except Exception as e:
            print(f"[ERROR] Click intercepted or failed: {e}, using JavaScript")
            driver.execute_script("arguments[0].click();", second_reserve_button)
            print("[INFO] Clicked second reserve button with JavaScript")

        driver.save_screenshot(f"{screenshot_dir}/second_reserve_clicked.png")

        # Wait for AGREE modal to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox']"))
        )
        print("[INFO] AGREE modal detected")

        # Step 3: Check AGREE checkbox
        agree_checkbox_locators = [
            (By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//label[contains(., 'I Agree')]//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')]"),
            (By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')]"),
            (By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//div[contains(@class, 'MuiBox-root')]//label//input[@type='checkbox']"),
            (By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox']"),  # Fallback
        ]

        agree_checkbox = None
        for by, value in agree_checkbox_locators:
            agree_checkbox = safe_find(driver, by, value, timeout=20, description="AGREE checkbox")  # Increased timeout to 20s
            if agree_checkbox:
                break

        if agree_checkbox:
            # Scroll to the end of the modal to satisfy the requirement
            modal = driver.find_element(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]")
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
            time.sleep(3)  # Increased wait to 3s to ensure scroll completes

            # Wait for the label containing the checkbox to be visible
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//label[contains(., 'I Agree')]")))
            
            # Wait for checkbox to be clickable after scroll
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//label[contains(., 'I Agree')]//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')]")))
            
            # Ensure the checkbox is visible and scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", agree_checkbox)
            time.sleep(1)  # Brief wait for scroll to complete

            # Attempt to check the checkbox
            try:
                agree_checkbox.click()
                print("[INFO] Attempted to check AGREE checkbox with normal click")
            except Exception as e:
                print(f"[ERROR] Normal click failed: {e}, using JavaScript")
                driver.execute_script("arguments[0].click();", agree_checkbox)
                print("[INFO] Attempted to check AGREE checkbox with JavaScript")

            # Verify the checkbox is checked
            time.sleep(1)  # Brief wait to ensure state updates
            is_checked = agree_checkbox.get_attribute("checked")
            if is_checked:
                print("[INFO] AGREE checkbox is confirmed checked")
                driver.save_screenshot(f"{screenshot_dir}/agree_checked.png")
            else:
                print("[ERROR] AGREE checkbox is not checked. Please ensure the checkbox is ticked manually, then restart the script.")
                driver.save_screenshot(f"{screenshot_dir}/agree_not_checked.png")
                return False  # Fail the run to require manual intervention

        else:
            print("[ERROR] AGREE checkbox not found")
            # Capture the entire modal HTML and screenshot for debugging
            modal = driver.find_element(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]")
            with open(f"{screenshot_dir}/modal_html.txt", "w") as f:
                f.write(modal.get_attribute("outerHTML"))
            driver.save_screenshot(f"{screenshot_dir}/agree_not_found.png")
            # Additional debug: Print all checkboxes and their details in the modal
            checkboxes = driver.find_elements(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox']")
            print(f"[DEBUG] Found {len(checkboxes)} checkboxes in modal:")
            for i, cb in enumerate(checkboxes, 1):
                attrs = cb.get_attribute("outerHTML")
                print(f"[DEBUG] Checkbox {i}: {attrs}")
            return False

        # Step 4: Click Confirm button with retry
        max_attempts = 3
        for attempt in range(max_attempts):
            confirm_button = safe_find(driver, By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//button[contains(text(), 'Confirm') and not(@disabled)]", 10, "Confirm button")
            if confirm_button:
                confirm_button.click()
                print(f"[INFO] Clicked Confirm button on attempt {attempt + 1}")
                driver.save_screenshot(f"{screenshot_dir}/confirm_clicked.png")
                break
            else:
                print(f"[WARN] Confirm button not clickable or not found on attempt {attempt + 1}, waiting for enable...")
                driver.save_screenshot(f"{screenshot_dir}/confirm_not_clickable_{attempt + 1}.png")
                if attempt < max_attempts - 1:
                    time.sleep(2)  # Wait for the button to become enabled
        else:
            print("[ERROR] Failed to find or enable Confirm button after all attempts")
            driver.save_screenshot(f
