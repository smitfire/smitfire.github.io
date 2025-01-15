import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import csv
import time
from dotenv import load_dotenv
from utils import parse_relative_date

load_dotenv()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")

# Initialize WebDriver
service = Service(CHROME_DRIVER_PATH)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

try:
    # Step 1: Log in to LinkedIn
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    email_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')

    email_field.send_keys(LINKEDIN_EMAIL)
    password_field.send_keys(LINKEDIN_PASSWORD)
    login_button.click()
    time.sleep(5)

    # Step 2: Navigate to the Saved Jobs page
    driver.get("https://www.linkedin.com/my-items/saved-jobs/?cardType=APPLIED")
    time.sleep(5)

    # Step 3: Extract job information across pages
    job_data = []
    for _ in range(12):  # Loop through 8 pages
        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_items = soup.select(
            "body > div.application-outlet > div.authentication-outlet > div > main > section > div > div:nth-child(4) > div > ul > li"
        )

        for job in job_items:
            try:
                company = job.select_one(
                    "div > div > div > div.pt3.pb3.t-12.t-black--light > div.mb1 > div.t-14.t-black.t-normal"
                ).get_text(strip=True)
            except AttributeError:
                company = "N/A"

            try:
                title_tag = job.select_one(
                    "div > div > div > div.pt3.pb3.t-12.t-black--light > div.mb1 > div.t-roman.t-sans > div > span > span > a"
                )
                title = title_tag.get_text(strip=True)
                job_url = title_tag["href"] if title_tag else "N/A"
                if job_url != "N/A":
                    job_url = job_url.split("?")[0]
            except AttributeError:
                title = "N/A"
                job_url = "N/A"

            try:
                relative_date_text = job.select_one(
                    "div > div > div > div.pt3.pb3.t-12.t-black--light > div.entity-result__insights.t-12 > div > div > div > span"
                ).get_text(strip=True)
                date_applied = parse_relative_date(relative_date_text)
            except AttributeError:
                date_applied = "N/A"

            job_data.append({
                "company": company,
                "title": title,
                "date_applied": date_applied,
                "job_url": job_url
            })

        # Step 4: Click the "Next" button
        try:
            next_button = driver.find_element(
                By.CSS_SELECTOR,
                "button.artdeco-button.artdeco-button--muted.artdeco-button--icon-right.artdeco-button--1.artdeco-button--tertiary.ember-view.artdeco-pagination__button.artdeco-pagination__button--next",
            )
            next_button.click()
            time.sleep(5)  # Allow time for the next page to load
        except NoSuchElementException:
            print("No more pages or unable to find the Next button.")
            break

    # Step 5: Write to CSV
    csv_file = "saved_jobs.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Company", "Job Title", "Date Applied", "Job URL"])
        writer.writeheader()
        for job in job_data:
            writer.writerow({
                "Company": job["company"],
                "Job Title": job["title"],
                "Date Applied": job["date_applied"],
                "Job URL": job["job_url"]
            })

    print(f"Saved jobs extracted and written to {csv_file}")

finally:
    driver.quit()
