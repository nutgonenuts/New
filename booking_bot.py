print("[DEBUG] Entering login credentials...")
driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(USER_EMAIL)
driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(USER_PASSWORD)
driver.save_screenshot("screenshots/before_login_click.png")

print("[DEBUG] Clicking login button...")
driver.find_element(By.XPATH, "//button[contains(text(),'LOG IN')]").click()

# Wait for redirect and check if login succeeded
time.sleep(3)
driver.save_screenshot("screenshots/login_attempt.png")

if "login" in driver.current_url.lower():
    print("[ERROR] Login failed. Still on login page.")
else:
    print("[DEBUG] Successfully logged in!")
