from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from webdriver_manager.chrome import ChromeDriverManager

# File paths
CREDENTIALS_FILE = 'credentials.txt'
ERROR_LOG_FILE = 'error.log'
CHANGED_PASSWORDS_FILE = 'changed_passwords.txt'
NEW_PASSWORDS_OUTPUT_FILE = 'new_passwords.txt'  # New file to output new passwords

# Set up logging
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
file_handler = logging.FileHandler(ERROR_LOG_FILE)
error_logger.addHandler(file_handler)


def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def select_first_profile(driver):
    try:
        status_update("Step 10: Waiting for profile items to load...", 20)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="SelectProfilePage_profile-item"]'))
        )
        status_update("Step 20: Profile items loaded. Selecting the first profile...", 30)
        first_profile = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="SelectProfilePage_profile-item"]')
        first_profile.click()
        time.sleep(2)
        status_update("Step 30: First profile selected.", 40)
    except Exception as e:
        error_logger.error(f"Error selecting profile: {e}")
        status_update(f"Error selecting profile: {e}", 0)


def change_password(driver, current_password, new_password):
    try:
        status_update("Step 40: Navigating to the change password page...", 50)
        driver.get('https://shahid.mbc.net/ar/hub/change-password')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'currentPassword'))
        )
        status_update("Step 50: Change password page loaded.", 60)
        driver.find_element(By.ID, 'currentPassword').send_keys(current_password)
        driver.find_element(By.ID, 'newPassword').send_keys(new_password)
        driver.find_element(By.ID, 'newPasswordRetype').send_keys(new_password)
        driver.find_element(By.ID, 'newPasswordRetype').send_keys(Keys.RETURN)
        status_update("Step 60: Password change attempted.", 70)
        time.sleep(5)
    except Exception as e:
        error_logger.error(f"Error changing password: {e}")
        status_update(f"Error changing password: {e}", 0)


def logout(driver):
    try:
        status_update("Step 70: Logging out...", 80)
        driver.get('https://shahid.mbc.net/en/logout')
        time.sleep(5)
        status_update("Step 80: Logged out successfully.", 90)
    except Exception as e:
        error_logger.error(f"Error logging out: {e}")
        status_update(f"Error logging out: {e}", 0)


def status_update(message, progress):
    global status_message, progress_value
    status_message = message
    progress_value = progress


def main():
    global status_message, progress_value
    status_message = "Initializing..."
    progress_value = 10

    driver = initialize_driver()
    status_update("Step 0: Driver initialized.", 20)

    with open(CREDENTIALS_FILE, 'r') as file:
        accounts = file.readlines()

    with open(CHANGED_PASSWORDS_FILE, 'w') as log_file, open(NEW_PASSWORDS_OUTPUT_FILE, 'w') as new_passwords_file:
        total_accounts = len(accounts)
        for i, account in enumerate(accounts):
            email, current_password = account.strip().split(':')
            try:
                status_update(f"Step {i * 10 + 10}: Logging in with {email}", 30 + (70 * i // total_accounts))
                driver.get('https://shahid.mbc.net/en/hub/login')
                time.sleep(2)
                driver.find_element(By.ID, 'emailMobileSignIn.userName').send_keys(email)
                driver.find_element(By.ID, 'emailMobileSignIn.password').send_keys(current_password)
                driver.find_element(By.ID, 'emailMobileSignIn.password').send_keys(Keys.RETURN)
                status_update("Step 40: Login attempt made.", 50)
                time.sleep(5)

                select_first_profile(driver)

                new_password = 'passShifter'
                change_password(driver, current_password, new_password)

                log_file.write(f"{email}:{new_password}\n")
                new_passwords_file.write(f"{email}:{new_password}\n")
                status_update(f"Step 50: Password changed for {email}.", 70 + (30 * i // total_accounts))

                logout(driver)

                status_update("Step 60: Returning to login page...", 80)
                driver.get('https://shahid.mbc.net/en/hub/login')
                time.sleep(2)
            except Exception as e:
                error_logger.error(f"Error processing account {email}: {e}")
                status_update(f"Error processing account {email}: {e}", 0)
                logout(driver)

    driver.quit()
    status_update("All accounts processed. WebDriver closed.", 100)


if __name__ == "__main__":
    main()
