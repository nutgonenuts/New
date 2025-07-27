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


class ParkalotBot:
    TIMEOUT_LONG = 20
    TIMEOUT_SHORT = 10

    LOGIN_URL = "https://app.parkalot.io/login"

    EMAIL_LOCATORS = [
        (By.ID, "email"), (By.NAME, "email"), (By.XPATH, "//input[@type='email']"),
        (By.XPATH, "//input[contains(@class, 'md-input') and @type='email']")
    ]
    PASSWORD_LOCATORS = [
        (By.ID, "password"), (By.NAME, "password"), (By.XPATH, "//input[@type='password']"),
        (By.XPATH, "//input[contains(@class, 'md-input') and @type='password']")
    ]
    LOGIN_BUTTON_LOCATORS = [
        (By.XPATH, "//button[@type='submit']"),
        (By.XPATH, "//button[contains(translate(text(),'LOGIN','login'), 'login')]")
    ]

    def __init__(self, headless=True, max_booking_attempts=3, retry_delay=30):
        self.driver = None
        self.screenshot_dir = f"screenshots/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.log_file = os.path.join(self.screenshot_dir, "run.log")
        self.email, self.password = self.load_environment()
        self.headless = headless
        self.max_booking_attempts = max_booking_attempts
        self.retry_delay = retry_delay

    def log(self, message, level="INFO"):
        """Log to console and file."""
        log_msg = f"[{level}] {message}"
        print(log_msg)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} {log_msg}\n")

    def load_environment(self):
        if os.path.exists(".env"):
            load_dotenv()
            self.log("Loaded .env file")
        email = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")
        if not email or not password:
            raise ValueError("EMAIL or PASSWORD not set")
        return email, password

    def init_driver(self):
        chromedriver_autoinstaller.install()
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")
        try:
            self.driver = webdriver.Chrome(options=options)
            self.log("ChromeDriver initialized")
        except WebDriverException as e:
            self.log_exception(e, "ChromeDriver initialization failed")
            raise

    def safe_find(self, by, value, timeout=TIMEOUT_LONG, description="element"):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            self.log(f"Found {description}: {value}")
            return element
        except TimeoutException:
            self.log(f"Timeout waiting for {description}: {value}", "ERROR")
            return None

    def try_login(self, max_attempts=2):
        self.driver.get(self.LOGIN_URL)
        self.log("Navigated to login page")

        for attempt in range(max_attempts):
            self.log(f"Login attempt {attempt + 1}/{max_attempts}")
            email_field = self.find_first_valid(self.EMAIL_LOCATORS, "email field")
            pass_field = self.find_first_valid(self.PASSWORD_LOCATORS, "password field")
            login_button = self.find_first_valid(self.LOGIN_BUTTON_LOCATORS, "login button")

            if not all([email_field, pass_field, login_button]):
                self.log("Missing login elements", "ERROR")
                self.take_screenshot(f"login_attempt_{attempt + 1}_failed.png")
                continue

            try:
                email_field.clear()
                email_field.send_keys(self.email)
                pass_field.clear()
                pass_field.send_keys(self.password)
                login_button.click()
                self.log("Submitted login form")

                WebDriverWait(self.driver, self.TIMEOUT_LONG).until(
                    EC.any_of(
                        EC.url_contains("dashboard"),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Dashboard') or contains(text(), 'Welcome')]"))
                    )
                )
                self.log("Login successful")
                self.take_screenshot("login_success.png")
                return True
            except TimeoutException:
                self.log("Login failed", "ERROR")
                self.take_screenshot(f"login_attempt_{attempt + 1}_failed.png")

        self.log("All login attempts failed", "ERROR")
        self.take_screenshot("login_failed.png")
        return False

    def book_parking_with_retry(self):
        """Attempt to book parking with retries and delays."""
        for attempt in range(1, self.max_booking_attempts + 1):
            self.log(f"Booking attempt {attempt}/{self.max_booking_attempts}")
            if self.book_parking():
                return True
            if attempt < self.max_booking_attempts:
                self.log(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        self.log("All booking attempts failed", "ERROR")
        return False

    def book_parking(self):
        try:
            WebDriverWait(self.driver, self.TIMEOUT_LONG).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'app-body') and not(contains(@class, 'loading'))]"))
            )
            self.log("Dashboard loaded")
            self.take_screenshot("dashboard.png")

            today = datetime.now()
            target_dates = [today + timedelta(days=i * 7) for i in range(3)]

            sunday_elements = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'Sunday') and contains(@style, 'font-size: 24px')]")
            if not sunday_elements:
                self.log("No Sunday elements found", "ERROR")
                self.take_screenshot("sundays_not_found.png")
                return False

            target_sunday = self.find_target_sunday(sunday_elements, target_dates)
            if not target_sunday:
                self.log("No matching Sunday element found", "ERROR")
                self.take_screenshot("sunday_not_found.png")
                return False

            if not self.click_reserve_button(target_sunday):
                return False

            if not self.handle_agree_and_confirm():
                return False

            try:
                WebDriverWait(self.driver, self.TIMEOUT_LONG).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Booking Confirmed') or contains(text(), 'Reservation Successful')]")),
                        EC.url_contains("confirmation")
                    )
                )
                self.log("Booking confirmed", "SUCCESS")
                self.take_screenshot("booking_confirmed.png")
                return True
            except TimeoutException:
                try:
                    alert = self.driver.switch_to.alert
                    alert.accept()
                    self.log("Handled alert for booking confirmation")
                    self.take_screenshot("booking_alert_handled.png")
                    return True
                except NoAlertPresentException:
                    self.log("No confirmation or alert found", "ERROR")
                    self.take_screenshot("booking_failed.png")
                    return False

        except Exception as e:
            self.log_exception(e, "Booking failed")
            return False

    def find_target_sunday(self, sunday_elements, target_dates):
        for target_date in target_dates:
            formats = [
                target_date.strftime("%Y-%m-%d"),
                target_date.strftime("%B %d, %Y"),
                target_date.strftime("%d/%m/%Y"),
                target_date.strftime("%d %b %Y")
            ]
            for sunday in sunday_elements:
                try:
                    date_element = sunday.find_element(
                        By.XPATH,
                        "./preceding-sibling::* | ./parent::*//span | ./ancestor::div[contains(@class, 'r-t') or contains(@class, 'lter-2')]//span[contains(@class, 'pull-left')]"
                    )
                    date_text = date_element.text.strip()
                    if self.match_date_text(date_text, formats):
                        self.log(f"Selected Sunday: {date_text} for {formats[0]}")
                        return sunday
                except NoSuchElementException:
                    continue
        return None

    def match_date_text(self, text, formats):
        return any(fmt in text for fmt in formats)

    def click_reserve_button(self, target_sunday):
        try:
            parent = target_sunday.find_element(By.XPATH, "./ancestor::div[contains(@class, 'r-t') or contains(@class, 'lter-2')]")
            reserve_button = parent.find_element(By.XPATH, ".//button[contains(text(), 'reserve')]")
            if reserve_button and not self.is_disabled(reserve_button):
                reserve_button.click()
                self.log("Clicked first reserve button")
                self.take_screenshot("first_reserve_clicked.png")
                return True
        except NoSuchElementException:
            pass
        self.log("Reserve button not found or disabled", "ERROR")
        self.take_screenshot("reserve_not_found.png")
        return False

    def handle_agree_and_confirm(self):
        try:
            WebDriverWait(self.driver, self.TIMEOUT_SHORT).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox']"))
            )
            checkbox = self.safe_find(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox']", self.TIMEOUT_SHORT, "AGREE checkbox")
            if checkbox:
                self.driver.execute_script("arguments[0].click();", checkbox)
                self.log("Checked AGREE checkbox")
                self.take_screenshot("agree_checked.png")

                confirm_button = self.safe_find(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//button[contains(translate(text(), 'CONFIRM', 'confirm'), 'confirm')]", self.TIMEOUT_SHORT, "Confirm button")
                if confirm_button:
                    confirm_button.click()
                    self.log("Clicked Confirm button")
                    self.take_screenshot("confirm_clicked.png")
                    return True
            return False
        except TimeoutException:
            self.log("AGREE modal not found", "ERROR")
            self.take_screenshot("agree_not_found.png")
            return False

    def is_disabled(self, element):
        return element.get_attribute("disabled") or "disabled" in element.get_attribute("class").lower()

    def find_first_valid(self, locators, description):
        for by, value in locators:
            el = self.safe_find(by, value, description=description)
            if el:
                return el
        return None

    def take_screenshot(self, name):
        path = os.path.join(self.screenshot_dir, name)
        self.driver.save_screenshot(path)
        self.log(f"Screenshot saved: {path}")

    def log_exception(self, e, context="Error"):
        self.log(f"{context}: {e}\n{traceback.format_exc()}", "ERROR")
        self.take_screenshot(f"{context.replace(' ', '_').lower()}.png")

    def run(self):
        try:
            self.init_driver()
            if self.try_login():
                if self.book_parking_with_retry():
                    self.log("Parking booked successfully", "SUCCESS")
                else:
                    self.log("Failed to book parking", "ERROR")
            else:
                self.log("Login failed", "ERROR")
        except Exception as e:
            self.log_exception(e, "Unexpected error")
        finally:
            if self.driver:
                self.driver.quit()
                self.log("ChromeDriver closed")


if __name__ == "__main__":
    bot = ParkalotBot(max_booking_attempts=3, retry_delay=30)
    bot.run()
