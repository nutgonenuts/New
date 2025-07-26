import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

EMAIL = os.getenv("PARKALOT_EMAIL")
PASSWORD = os.getenv("PARKALOT_PASSWORD")

def debug_log(message):
    print(f"[DEBUG] {message}", flush=True)

def take_screenshot(driver, name):
    os.makedirs("screenshots", exist_ok=True)
    path = f"screenshots/{name}.png"
    driver.save_screenshot(path)
    debug_log(f"Screenshot saved: {path}")

def login(driver):
    debug_log("Opening Parkalot website...")
    driver.get("https://app.parkalot.io/")
    time
