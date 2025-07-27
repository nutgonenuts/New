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
        target_dates = [today + timedelta(days=i * 7) for i in range(3)]  # Today + 2 more Sundays
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

        if driver.find_elements(By.XPATH, "//*[contains(text(), 'No spaces available') or contains(text(), 'Fully booked')]"):
            print("[ERROR] No parking spaces available for this Sunday")
            driver.save_screenshot(f"{screenshot_dir}/no_spaces_available.png")
            return False

        reserve_button.click()
        print("[INFO] Clicked first reserve button")
        driver.save_screenshot(f"{screenshot_dir}/first_reserve_clicked.png")

        # Step 2: Wait for second reserve option and handle modal
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//button[@type='button' and contains(@class, 'md-btn') and contains(text(), 'reserve')]"))
            )
            # Try to close any modal overlay
            try:
                modal_close = driver.find_element(By.XPATH, "//div[contains(@class, 'modal black-overlay')]//button[contains(@class, 'close')]")
                modal_close.click()
                WebDriverWait(driver, 5).until_not(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'modal black-overlay')]"))
                )
                print("[INFO] Closed modal overlay")
            except NoSuchElementException:
                print("[INFO] No modal overlay found to close")
            print("[INFO] Second reserve option detected")
        except TimeoutException:
            print("[ERROR] Second reserve option timed out")
            driver.save_screenshot(f"{screenshot_dir}/second_reserve_timeout.png")
            return False

        # Step 2: Click second Reserve button
        second_reserve_button_locators = [
            (By.XPATH, "//button[@type='button' and contains(@class, 'md-btn') and contains(text(), 'reserve')]"),
            (By.CSS_SELECTOR, "button.md-btn.md-flat.m-r"),
            (By.CSS_SELECTOR, "div.modal button, div.dialog button"),
            (By.XPATH, "//*[contains(@class, 'modal') or contains(@class, 'dialog')]//button[contains(text(), 'reserve')]"),
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

        second_reserve_button.click()
        print("[INFO] Clicked second reserve button")
        driver.save_screenshot(f"{screenshot_dir}/second_reserve_clicked.png")

        # Step 3: Wait for AGREE modal with retry
        max_attempts = 3
        for attempt in range(max_attempts):
            agree_checkbox = safe_find(driver, By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')]", 20, "AGREE checkbox")
            if agree_checkbox:
                driver.execute_script("arguments[0].click();", agree_checkbox)
                print(f"[INFO] Checked AGREE checkbox on attempt {attempt + 1}")
                driver.save_screenshot(f"{screenshot_dir}/agree_checked.png")
                break
            else:
                print(f"[ERROR] AGREE checkbox not found on attempt {attempt + 1}")
                driver.save_screenshot(f"{screenshot_dir}/agree_not_found_{attempt + 1}.png")
                if attempt < max_attempts - 1:
                    time.sleep(3)  # Increased wait between retries
        else:
            print("[ERROR] Failed to find AGREE checkbox after all attempts")
            driver.save_screenshot(f"{screenshot_dir}/agree_not_found.png")
            return False

        # Step 4: Click Confirm button with retry
        max_attempts = 3
        for attempt in range(max_attempts):
            confirm_button = safe_find(driver, By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//button[contains(translate(text(), 'CONFIRM', 'confirm'), 'confirm')]", 10, "Confirm button")
            if confirm_button:
                confirm_button.click()
                print(f"[INFO] Clicked Confirm button on attempt {attempt + 1}")
                driver.save_screenshot(f"{screenshot_dir}/confirm_clicked.png")
                break
            else:
                print(f"[ERROR] Confirm button not found on attempt {attempt + 1}")
                driver.save_screenshot(f"{screenshot_dir}/confirm_not_found_{attempt + 1}.png")
                if attempt < max_attempts - 1:
                    time.sleep(2)
        else:
            print("[ERROR] Failed to find Confirm button after all attempts")
            driver.save_screenshot(f"{screenshot_dir}/confirm_not_found.png")
            return False

        # Wait for booking confirmation
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
