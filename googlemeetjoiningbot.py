from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile

user_data_path = os.getenv("USERPROFILE") + "\\AppData\\Local\\Google\\Chrome\\User Data"
profile = "Profile 2" 

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



meet_link = "https://meet.google.com/puz-gnsx-eof?authuser=0&pli=1"

print(f"Opening meet link: {meet_link}")
driver.get(meet_link)
print("Page loaded.")

wait = WebDriverWait(driver, 30)
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
    print("Searching for Join button...")
    join_found = False
    # Wait for the join button to be present
    join_xpath = '//*[contains(text(), "Join now") or contains(text(), "Ask to join") or contains(text(), "Join")]/ancestor-or-self::button | //button[.//span[contains(text(), "Join now") or contains(text(), "Ask to join")]]'
    try:
        join_btn = wait.until(EC.presence_of_element_located((By.XPATH, join_xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", join_btn)
        time.sleep(1)
        try:
            join_btn.click()
        except:
            driver.execute_script("arguments[0].click();", join_btn)
        print(f"Joined meeting at {time.strftime('%H:%M:%S')}")
        joined = True
    except Exception as ie:
        print(f"Detailed Join button issue: {ie}")
        raise ie
    time.sleep(5400)# class length generally 90 mins, adjust as needed
except Exception as e:
    print(f"Join button not found or not clickable: {e}")
driver.quit()
if not driver.service.process:
    log_file = "meet_joining_log.txt"
    with open(log_file, "w") as f:
        f.write(f"Joined meeting at {time.strftime('%H:%M:%S')}\n")
        f.write(f"Left meeting at {time.strftime('%H:%M:%S')}\n")
    print(f"Meeting log saved to {log_file}")
else:
    print("Driver process still running, log not saved.")

recording = sd.rec(int(5400 * 44100),samplerate=44100, channels=2)
sd.wait()
np.save("meeting_audio.npy", recording)
wavfile.write("meeting_audio.wav", 44100, recording)#converting the numpy array to wav file for easier access
