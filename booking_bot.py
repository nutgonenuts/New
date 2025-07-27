# Step 3: Check AGREE checkbox
agree_checkbox_locators = [
    (By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//label[contains(text(), 'I Agree')]//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')]"),
    (By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')]"),
    (By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//div[contains(@class, 'MuiBox-root')]//label//input[@type='checkbox']"),
    (By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox']"),  # Fallback
]

agree_checkbox = None
for by, value in agree_checkbox_locators:
    agree_checkbox = safe_find(driver, by, value, timeout=15, description="AGREE checkbox")  # Increased timeout to 15s
    if agree_checkbox:
        break

if agree_checkbox:
    # Scroll to the end of the modal to satisfy the requirement
    modal = driver.find_element(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]")
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
    time.sleep(2)  # Increased wait to ensure scroll completes

    # Wait for checkbox to be clickable after scroll
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//label[contains(text(), 'I Agree')]//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')]")))
    
    # Ensure the checkbox is visible and scroll into view
    driver.execute_script("arguments[0].scrollIntoView(true);", agree_checkbox)
    time.sleep(1)  # Brief wait for scroll to complete

    # Check if checkbox is already checked or disabled
    is_checked = agree_checkbox.get_attribute("checked")
    is_disabled = agree_checkbox.get_attribute("disabled")
    if is_checked or is_disabled:
        print(f"[INFO] AGREE checkbox is already checked: {is_checked}, disabled: {is_disabled}")
    else:
        try:
            # Attempt to click normally
            agree_checkbox.click()
            print("[INFO] Checked AGREE checkbox with normal click")
        except Exception as e:
            print(f"[ERROR] Normal click failed: {e}, using JavaScript")
            driver.execute_script("arguments[0].click();", agree_checkbox)
            print("[INFO] Checked AGREE checkbox with JavaScript")

    driver.save_screenshot(f"{screenshot_dir}/agree_checked.png")
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
