from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os



user_data_path = os.getenv("USER_PATH")
profile = "Profile 1" 

options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={user_data_path}")
options.add_argument(f"--profile-directory={profile}")
options.add_argument("--use-fake-ui-for-media-stream")
options.add_argument("--use-fake-device-for-media-stream")
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")

print("Starting driver...")
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("Driver started.")
except Exception as e:
    print(f"Failed to start driver: {e}")
    print("Trying without specific profile...")
    options = webdriver.ChromeOptions()
    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_argument("--use-fake-device-for-media-stream")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("Driver started without profile.")

wait = WebDriverWait(driver, 30)

meet_link = "MEET_LINK"

print(f"Opening meet link: {meet_link}")
driver.get(meet_link)
print("Page loaded.")

try:
    mic = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@aria-label, "microphone") or contains(@aria-label, "mic")]')))
    if "Turn off" in mic.get_attribute("aria-label"):
        mic.click()
        print("Mic muted")
    else:
        print("Mic already muted")
except Exception as e:
    print(f"Mic button issue: {e}")

try:
    cam = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@aria-label, "camera") or contains(@aria-label, "cam")]')))
    if "Turn off" in cam.get_attribute("aria-label"):
        cam.click()
        print("Camera disabled")
    else:
        print("Camera already disabled")
except Exception as e:
    print(f"Camera button issue: {e}")

try:
    join_xpath = '//span[contains(text(), "Join now") or contains(text(), "Ask to join")]'
    join = wait.until(EC.element_to_be_clickable((By.XPATH, join_xpath)))
    join.click()
    print("Joined meeting")
except Exception as e:
    print(f"Join button not found or not clickable: {e}")
time.sleep(60)
driver.quit()
