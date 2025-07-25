import chromedriver_autoinstaller
chromedriver_autoinstaller.install()  # Automatically downloads and sets the correct ChromeDriver version

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Configure Chrome options
options = Options()
options.add_argument("--headless")  # Remove this if you want to see the browser window locally
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize the driver
driver = webdriver.Chrome(options=options)

try:
    driver.get("https://example.com")  # Replace with your actual booking page URL
    print("Page title:", driver.title)
    
    #
