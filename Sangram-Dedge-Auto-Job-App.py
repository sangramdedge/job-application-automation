#!/usr/bin/env python
# coding: utf-8

# In[7]:


import json
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager

def solve_captcha(driver):
    """Solve CAPTCHA with improved validation"""
    try:
        captcha_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "captchaQuestion"))
        )
        question = captcha_element.text
        solution = int(captcha_element.get_attribute("data-solution"))

        captcha_input = driver.find_element(By.ID, "captchaInput")
        captcha_input.clear()
        captcha_input.send_keys(str(solution))

        # Validate input
        driver.execute_script("""
            const event = new Event('input', { bubbles: true });
            arguments[0].dispatchEvent(event);
        """, captcha_input)
        
        print(f"Solved CAPTCHA: {question} = {solution}")
        return True
    except Exception as e:
        print(f"CAPTCHA error: {str(e)}")
        return False

def handle_alerts(driver):
    """Handle unexpected alerts"""
    try:
        WebDriverWait(driver, 2).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"Alert detected: {alert.text}")
        alert.accept()
    except (TimeoutException, NoAlertPresentException):
        pass

def main():
    with open("C:/Users/sangr/.jupyter/user1_data.json", "r") as f:
        user_data = json.load(f)

    # Verify resume exists
    resume_path = os.path.abspath(user_data["resume"])
    if not os.path.exists(resume_path):
        raise FileNotFoundError(f"Resume not found at: {resume_path}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        driver.get("file:///C:/Users/sangr/.jupyter/index1.html")

        # Fill form fields
        fields = [
            ("full_name", "name"),
            ("email", "email"),
            ("phone", "phone"),
            ("experience", "experience")
        ]
        
        for field_id, data_key in fields:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, field_id))
            ).send_keys(user_data[data_key])

        # Job selection
        Select(driver.find_element(By.ID, "job_position")).select_by_visible_text(
            user_data["job_position"])
        
        # Employment type
        employment_type = "full_time" if user_data["employment_type"] == "Full-time" else "part_time"
        driver.find_element(By.ID, employment_type).click()

        # Resume upload
        driver.find_element(By.ID, "resume").send_keys(resume_path)
        print(f"Uploaded resume: {resume_path}")

        # Solve CAPTCHA
        if not solve_captcha(driver):
            raise Exception("CAPTCHA resolution failed")

        # Handle any residual alerts
        handle_alerts(driver)

        # Submit form
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        ).click()

        # Verify success
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "successMessage"))
        )
        print("Form submitted successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")
        handle_alerts(driver)
    finally:
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    main()


# In[ ]:




