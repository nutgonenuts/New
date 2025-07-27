# Step 3: Check AGREE checkbox
def check_agree_checkbox(driver, screenshot_dir):
    max_attempts = 5  # Maximum number of different methods to try
    methods = [
        # Method 1: Direct XPath with presence and click
        {
            "locator": (By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')]"),
            "wait_condition": EC.presence_of_element_located,
            "action": lambda elem: elem.click(),
            "description": "Direct XPath with presence and click"
        },
        # Method 2: XPath with visibility and click
        {
            "locator": (By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//div[contains(@class, 'MuiBox-root')]//label//input[@type='checkbox']"),
            "wait_condition": EC.visibility_of_element_located,
            "action": lambda elem: elem.click(),
            "description": "XPath with visibility and click"
        },
        # Method 3: Fallback XPath with JavaScript check
        {
            "locator": (By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox']"),
            "wait_condition": EC.presence_of_element_located,
            "action": lambda elem: driver.execute_script("arguments[0].checked = true;", elem),
            "description": "Fallback XPath with JavaScript check"
        },
        # Method 4: JavaScript force with presence
        {
            "locator": (By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')]"),
            "wait_condition": EC.presence_of_element_located,
            "action": lambda elem: driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change'));", elem),
            "description": "JavaScript force with change event"
        },
        # Method 5: Scroll and retry with click
        {
            "locator": (By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')]"),
            "wait_condition": EC.element_to_be_clickable,
            "action": lambda elem: elem.click(),
            "description": "Scroll and retry with click",
            "pre_action": lambda: driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", driver.find_element(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]"))
        }
    ]

    agree_checkbox = None
    for attempt in range(max_attempts):
        method = methods[attempt]
        print(f"[INFO] Attempt {attempt + 1}/{max_attempts} using method: {method['description']}")
        
        try:
            # Execute pre-action if defined (e.g., scroll)
            if "pre_action" in method:
                method["pre_action"]()
                time.sleep(2)  # Wait after scroll

            # Wait for the element based on the method's condition
            WebDriverWait(driver, 20).until(method["wait_condition"](method["locator"]))
            agree_checkbox = driver.find_element(*method["locator"])
            print(f"[INFO] Found AGREE checkbox with {method['description']}")

            # Perform the action (click or JavaScript)
            method["action"](agree_checkbox)
            print(f"[INFO] Applied action with {method['description']}")

            # Verify the checkbox is checked
            time.sleep(1)  # Brief wait to ensure state updates
            is_checked = agree_checkbox.get_attribute("checked")
            if is_checked:
                print("[INFO] AGREE checkbox is confirmed checked")
                driver.save_screenshot(f"{screenshot_dir}/agree_checked.png")
                return True
            else:
                print(f"[WARN] Checkbox not checked after {method['description']}, trying next method")
                continue

        except TimeoutException:
            print(f"[WARN] {method['description']} failed due to timeout")
            continue
        except Exception as e:
            print(f"[WARN] {method['description']} failed with error: {e}")
            continue

    # If all attempts fail
    print("[ERROR] All attempts to check AGREE checkbox failed")
    # Capture the entire modal HTML and screenshot for debugging
    modal = driver.find_element(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]")
    with open(f"{screenshot_dir}/modal_html.txt", "w") as f:
        f.write(modal.get_attribute("outerHTML"))
    driver.save_screenshot(f"{screenshot_dir}/agree_not_found.png")
    # Additional debug: Print all checkboxes and their details
    checkboxes = driver.find_elements(By.XPATH, "//div[contains(@class, 'MuiDialog-root')]//input[@type='checkbox']")
    print(f"[DEBUG] Found {len(checkboxes)} checkboxes in modal:")
    for i, cb in enumerate(checkboxes, 1):
        attrs = cb.get_attribute("outerHTML")
        print(f"[DEBUG] Checkbox {i}: {attrs}")
    element_state = driver.execute_script("return arguments[0].style.display;", agree_checkbox) if agree_checkbox else "N/A"
    print(f"[DEBUG] Last checkbox display state: {element_state}")
    print("[ERROR] Please ensure the checkbox is visible and tickable, then restart the script.")
    return False
