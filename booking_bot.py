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

# Check AGREE checkbox (updated function)
def check_agree_checkbox(driver, screenshot_dir):
    print("[INFO] Waiting for AGREE modal to fully load")
    time.sleep(5)  # Initial delay to ensure modal rendering

    try:
        modal_content = driver.find_element(By.XPATH, "//div[contains(@class, 'MuiDialogContent-root')] | //div[contains(@class, 'MuiDialog-root')]//div[contains(@class, 'MuiBox-root')]")
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", modal_content)
        print("[INFO] Scrolled to bottom of modal content")
        time.sleep(3)
    except Exception as e:
        print(f"[WARN] Could not scroll modal content: {e}")

    max_attempts = 7
    state_check_attempts = 3
    methods = [
        {
            "locator": (By.XPATH, "(//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')])[1]"),
            "wait_condition": EC.presence_of_element_located,
            "action": lambda elem: elem.click(),
            "description": "Direct click on first input with presence"
        },
        {
            "locator": (By.XPATH, "(//div[contains(@class, 'MuiDialog-root')]//div[contains(@class, 'MuiBox-root')]//label//input[@type='checkbox'])[1]"),
            "wait_condition": EC.visibility_of_element_located,
            "action": lambda elem: elem.click(),
            "description": "Click first input with visibility"
        },
        {
            "locator": (By.XPATH, "(//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox'])[1]"),
            "wait_condition": EC.presence_of_element_located,
            "action": lambda elem: driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change'));", elem),
            "description": "JavaScript check with change event on first input"
        },
        {
            "locator": (By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//label[contains(text(), 'I Agree')]"),
            "wait_condition": EC.element_to_be_clickable,
            "action": lambda elem: elem.click(),
            "description": "Click label with 'I Agree'",
            "pre_action": lambda: driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", driver.find_element(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]"))
        },
        {
            "locator": (By.XPATH, "(//div[contains(@class, 'MuiDialog-root')]//span[contains(@class, 'MuiCheckbox-root')])[1]"),
            "wait_condition": EC.element_to_be_clickable,
            "action": lambda elem: elem.click(),
            "description": "Click first span with MuiCheckbox-root",
            "pre_action": lambda: driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", driver.find_element(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]"))
        },
        {
            "locator": (By.XPATH, "(//div[contains(@class, 'MuiDialog-root')]//span[contains(@class, 'MuiCheckbox-root')])[1]"),
            "wait_condition": EC.presence_of_element_located,
            "action": lambda elem: driver.execute_script("arguments[0].click();", elem),
            "description": "JavaScript click on first span",
            "pre_action": lambda: driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", driver.find_element(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]"))
        },
        {
            "locator": (By.XPATH, "(//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')])[1]"),
            "wait_condition": EC.presence_of_element_located,
            "action": lambda elem: driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('input')); arguments[0].dispatchEvent(new Event('change'));", elem),
            "description": "JavaScript check with input and change events on first input"
        }
    ]

    checkboxes = driver.find_elements(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')]")
    print(f"[DEBUG] Found {len(checkboxes)} checkboxes in modal")
    for i, cb in enumerate(checkboxes, 1):
        attrs = cb.get_attribute("outerHTML")
        display_state = driver.execute_script("return arguments[0].style.display;", cb)
        is_disabled = cb.get_attribute("disabled")
        is_checked = cb.get_attribute("checked")
        print(f"[DEBUG] Checkbox {i}: {attrs}, Display: {display_state}, Disabled: {is_disabled}, Checked: {is_checked}")

    agree_checkbox = None
    for attempt in range(max_attempts):
        method = methods[attempt]
        print(f"[INFO] Attempt {attempt + 1}/{max_attempts} using method: {method['description']}")
        
        try:
            if "pre_action" in method:
                method["pre_action"]()
                time.sleep(3)

            WebDriverWait(driver, 25).until(method["wait_condition"](method["locator"]))
            agree_checkbox = driver.find_element(*method["locator"])
            print(f"[INFO] Found element with {method['description']}: {agree_checkbox.get_attribute('outerHTML')}")

            if "input" in method["locator"][1]:
                display_state = driver.execute_script("return arguments[0].style.display;", agree_checkbox)
                is_disabled = agree_checkbox.get_attribute("disabled")
                is_checked = agree_checkbox.get_attribute("checked")
                print(f"[DEBUG] Element state - Display: {display_state}, Disabled: {is_disabled}, Checked: {is_checked}")
            else:
                try:
                    span = driver.find_element(By.XPATH, "(//div[contains(@class, 'MuiDialog-root')]//span[contains(@class, 'MuiCheckbox-root')])[1]")
                    is_checked = "Mui-checked" in span.get_attribute("class")
                    display_state = driver.execute_script("return arguments[0].style.display;", span)
                    print(f"[DEBUG] Span state - Mui-checked: {is_checked}, Display: {display_state}")
                except Exception as e:
                    print(f"[DEBUG] Could not check span state: {e}")

            method["action"](agree_checkbox)
            print(f"[INFO] Applied action with {method['description']}")

            for check_attempt in range(state_check_attempts):
                time.sleep(1)
                try:
                    checkbox = driver.find_element(By.XPATH, "(//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')])[1]")
                    is_checked = checkbox.get_attribute("checked")
                    display_state = driver.execute_script("return arguments[0].style.display;", checkbox)
                    is_disabled = checkbox.get_attribute("disabled")
                    span = driver.find_element(By.XPATH, "(//div[contains(@class, 'MuiDialog-root')]//span[contains(@class, 'MuiCheckbox-root')])[1]")
                    is_span_checked = "Mui-checked" in span.get_attribute("class")
                    print(f"[DEBUG] State check {check_attempt + 1}/{state_check_attempts} - Input Checked: {is_checked}, Input Display: {display_state}, Input Disabled: {is_disabled}, Span Mui-checked: {is_span_checked}")
                    if is_checked or is_span_checked:
                        print("[INFO] AGREE checkbox is confirmed checked")
                        driver.save_screenshot(f"{screenshot_dir}/agree_checked.png")
                        return True
                except Exception as e:
                    print(f"[WARN] State check {check_attempt + 1}/{state_check_attempts} failed: {e}")
                    continue

            print(f"[WARN] Checkbox not checked after {method['description']}, trying next method")

        except TimeoutException:
            print(f"[WARN] {method['description']} failed due to timeout")
            continue
        except Exception as e:
            print(f"[WARN] {method['description']} failed with error: {e}")
            continue

    print("[ERROR] All attempts to check AGREE checkbox failed")
    try:
        modal = driver.find_element(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]")
        with open(f"{screenshot_dir}/modal_html.txt", "w") as f:
            f.write(modal.get_attribute("outerHTML"))
        driver.save_screenshot(f"{screenshot_dir}/agree_not_found.png")
        checkboxes = driver.find_elements(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox']")
        print(f"[DEBUG] Found {len(checkboxes)} checkboxes in modal:")
        for i, cb in enumerate(checkboxes, 1):
            attrs = cb.get_attribute("outerHTML")
            display_state = driver.execute_script("return arguments[0].style.display;", cb)
            is_disabled = cb.get_attribute("disabled")
            is_checked = cb.get_attribute("checked")
            print(f"[DEBUG] Checkbox {i}: {attrs}, Display: {display_state}, Disabled: {is_disabled}, Checked: {is_checked}")
        element_state = driver.execute_script("return arguments[0].style.display;", agree_checkbox) if agree_checkbox else "N/A"
        print(f"[DEBUG] Last element display state: {element_state}")
    except Exception as e:
        print(f"[ERROR] Failed to capture modal HTML or screenshot: {e}")
    print("[ERROR] Please ensure the checkbox is visible and tickable, then restart the script or adjust the methods list.")
    return False

# Book parking for the next available Sunday
def book_parking(driver):
    try:
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'app-body') and not(contains(@class, 'loading'))]"))
        )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("window.scrollTo(0, 0);")
        print("[INFO] Dashboard loaded")
        driver.save_screenshot(f"{screenshot_dir}/dashboard.png")

        today = datetime.now()
        target_dates = [today + timedelta(days=i * 7) for i in range(3)]
        target_dates = [d for d in target_dates if d >= today]

        sunday_elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'Sunday') and contains(@style, 'font-size: 24px')]")
        if not sunday_elements:
            print("[ERROR] No Sunday elements found")
            driver.save_screenshot(f"{screenshot_dir}/sundays_not_found.png")
            return False

        print(f"[INFO] Found {len(sunday_elements)} Sunday elements")
        target_sunday = None
        for target_date in target_dates:
            target_date_str = target_date.strftime("%Y-%m-%d")
            alt_date_str = target_date.strftime("%B %d, %Y")
            alt_date_str2 = target_date.strftime("%d/%m/%Y")
            alt_date_str3 = target_date.strftime("%d %b %Y")

            for sunday in sunday_elements:
                try:
                    date_element = sunday.find_element(By.XPATH, "./preceding-sibling::* | ./parent::*//span | ./ancestor::div[contains(@class, 'r-t') or contains(@class, 'lter-2')]//span[contains(@class, 'pull-left')]")
                    date_text = date_element.text.strip()
                    date_element_html = date_element.get_attribute("outerHTML")
                    print(f"[DEBUG] Sunday date element: {date_element_html}, Text: {date_text}, Target: {target_date_str}")
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

        if driver.find_elements(By.XPATH, "//*[contains(text(), 'No spaces available') or contains(text(), 'Fully booked')]"):
            print("[ERROR] No parking spaces available for this Sunday")
            driver.save_screenshot(f"{screenshot_dir}/no_spaces_available.png")
            return False

        reserve_button.click()
        print("[INFO] Clicked first reserve button")
        driver.save_screenshot(f"{screenshot_dir}/first_reserve_clicked.png")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='animate']/div/div/div[3]/button[2]"))
        )
        print("[INFO] Second reserve option detected")

        second_reserve_button_locators = [
            (By.XPATH, "//*[@id='animate']/div/div/div[3]/button[2]"),
            (By.XPATH, "/html/body/div[2]/div[1]/div[1]/div/div/div/div/div[3]/button[2]"),
            (By.CSS_SELECTOR, "#animate > div > div > div.modal-footer > button.md-btn.success.p-x-md:nth-child(2)"),
            (By.XPATH, "//div[contains(@class, 'modal-footer')]//button[contains(@class, 'md-btn success p-x-md') and contains(text(), 'Reserve')]"),
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

        driver.execute_script("arguments[0].scrollIntoView(true);", second_reserve_button)
        time.sleep(1)

        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='animate']/div/div/div[3]/button[2]")))
            second_reserve_button.click()
            print("[INFO] Clicked second reserve button")
        except Exception as e:
            print(f"[ERROR] Click intercepted or failed: {e}, using JavaScript")
            driver.execute_script("arguments[0].click();", second_reserve_button)
            print("[INFO] Clicked second reserve button with JavaScript")

        driver.save_screenshot(f"{screenshot_dir}/second_reserve_clicked.png")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox']"))
        )
        print("[INFO] AGREE modal detected")

        if not check_agree_checkbox(driver, screenshot_dir):
            return False

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
                    time.sleep(2)
        else:
            print("[ERROR] Failed to find or enable Confirm button after all attempts")
            driver.save_screenshot(f"{screenshot_dir}/confirm_not_found.png")
            return False

        try:
            WebDriverWait(driver, 20).until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Booking Confirmed') or contains(text(), 'Reservation Successful')]")),
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
                return False

    except Exception as e:
        print(f"[ERROR] Booking failed: {e}\n{traceback.format_exc()}")
        driver.save_screenshot(f"{screenshot_dir}/booking_error.png")
        return False

# Main execution
def main():
    global screenshot_dir
    screenshot_dir = f"screenshots/{datetime.now().strftime('%Y%m%d_%H%M%SS')}"
    os.makedirs(screenshot_dir, exist_ok=True)
    driver = None
    try:
        email, password = load_environment()
        driver = init_driver()
        if try_login(driver, email, password):
            if book_parking(driver):
                print("[SUCCESS] Parking booked successfully")
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
