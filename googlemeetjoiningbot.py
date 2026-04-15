import os
import time
import threading
import numpy as np
import scipy.io.wavfile as wavfile
import sounddevice as sd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def join_meet(meet_link, duration_mins, profile_name, logger_callback, cancel_event):
    logger_callback("Starting driver...")
    
    user_data_path = os.getenv("USERPROFILE") + "\\AppData\\Local\\Google\\Chrome\\User Data"
    
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={user_data_path}")
    options.add_argument(f"--profile-directory={profile_name}")
    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_argument("--use-fake-device-for-media-stream")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")

    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        logger_callback("Driver started using profile: " + profile_name)
    except Exception as e:
        logger_callback(f"Failed to start driver with profile (is a Chrome window open with this profile?): {e}")
        logger_callback("Trying without specific profile (Anonymous)...")
        options = webdriver.ChromeOptions()
        options.add_argument("--use-fake-ui-for-media-stream")
        options.add_argument("--use-fake-device-for-media-stream")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        logger_callback("Driver started without profile.")

    if cancel_event.is_set():
        driver.quit()
        return

    logger_callback(f"Opening meet link: {meet_link}")
    try:
        driver.get(meet_link)
        logger_callback("Page loaded.")
    except Exception as e:
        logger_callback(f"Error loading page: {e}")
        driver.quit()
        return

    wait = WebDriverWait(driver, 30)

    # Mute Mic
    try:
        mic = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@aria-label, "microphone") or contains(@aria-label, "mic")]')))
        if "Turn off" in mic.get_attribute("aria-label"):
            mic.click()
            logger_callback("Mic muted")
        else:
            logger_callback("Mic already muted")
    except Exception as e:
        logger_callback(f"Mic button issue: {e}")

    # Disable Cam
    try:
        cam = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@aria-label, "camera") or contains(@aria-label, "cam")]')))
        if "Turn off" in cam.get_attribute("aria-label"):
            cam.click()
            logger_callback("Camera disabled")
        else:
            logger_callback("Camera already disabled")
    except Exception as e:
        logger_callback(f"Camera button issue: {e}")

    # Join Event
    joined = False
    try:
        logger_callback("Searching for Join button...")
        join_xpath = '//*[contains(translate(text(),"JOIN","join"), "join") or contains(translate(text(),"ASK","ask"), "ask")]/ancestor-or-self::button | //button[.//span[contains(translate(text(),"JOIN","join"), "join")]]'
        join_btn = wait.until(EC.presence_of_element_located((By.XPATH, join_xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", join_btn)
        time.sleep(1)
        try:
            join_btn.click()
        except:
            driver.execute_script("arguments[0].click();", join_btn)
        logger_callback(f"✅ Joined meeting at {time.strftime('%H:%M:%S')}")
        joined = True
    except Exception as ie:
        logger_callback(f"Join button not found or not clickable. Check if meeting requires permission.")
        driver.quit()
        return

    if not joined:
        driver.quit()
        return

    # Start Recording concurrent with waiting
    duration_seconds = int(duration_mins * 60)
    logger_callback(f"Starting audio recording for {duration_mins} minutes...")
    
    # We use a separate thread for recording so we can monitor cancel_event in the main loop
    rec_data = []
    def record_audio():
        nonlocal rec_data
        try:
            rec_data = sd.rec(int(duration_seconds * 44100), samplerate=44100, channels=2)
            sd.wait()
        except Exception as e:
            logger_callback(f"Recording error: {e}")

    rec_thread = threading.Thread(target=record_audio)
    rec_thread.start()

    # Wait loop
    elapsed = 0
    poll_interval = 2
    while elapsed < duration_seconds:
        if cancel_event.is_set():
            logger_callback("Bot cancelled by user.")
            break
        time.sleep(poll_interval)
        elapsed += poll_interval

    logger_callback("Class duration reached or bot stopped. Cleaning up...")
    
    # Wait for recording if not cancelled
    if not cancel_event.is_set() and rec_thread.is_alive():
        rec_thread.join(timeout=2)
        
    if len(rec_data) > 0:
        np.save("meeting_audio.npy", rec_data)
        wavfile.write("meeting_audio.wav", 44100, rec_data)
        logger_callback("Audio recording saved securely.")

    if driver:
        driver.quit()
    
    logger_callback(f"Left meeting at {time.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    # Fallback to test standalone
    def print_log(msg):
        print("[BOT]", msg)
    evt = threading.Event()
    join_meet("https://meet.google.com/puz-gnsx-eof?authuser=0&pli=1", 90, "Profile 2", print_log, evt)
