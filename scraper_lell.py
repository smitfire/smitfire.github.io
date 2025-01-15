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
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")

def init_driver():
    service = Service(CHROME_DRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Enable headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login_to_linkedin(driver):
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    email_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')

    email_field.send_keys(LINKEDIN_EMAIL)
    password_field.send_keys(LINKEDIN_PASSWORD)
    login_button.click()
    time.sleep(5)

def scrape_jobs(page_number):
    driver = init_driver()
    login_to_linkedin(driver)
    
    driver.get(f"https://www.linkedin.com/my-items/saved-jobs/?cardType=APPLIED&start={page_number*10}")
    print(f"https://www.linkedin.com/my-items/saved-jobs/?cardType=APPLIED&start={page_number*10}")
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_items = soup.select(
        "body > div.application-outlet > div.authentication-outlet > div > main > section > div > div:nth-child(4) > div > ul > li"
    )

    job_data = []
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
            "date_applied": date_applied,
            "company": company,
            "title": title,
            "job_url": job_url
        })

    driver.quit()
    return job_data

def main():
    job_data = []
    with ThreadPoolExecutor(max_workers=13) as executor:
        futures = [executor.submit(scrape_jobs, page) for page in range(0, 12)]
        for future in futures:
            job_data.extend(future.result())

    # Save the job data to a CSV file
    with open("saved_jobs_lell.csv", "w", newline="") as csvfile:
        fieldnames = ["date_applied", "company", "title", "job_url"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(job_data)

    print("Job data saved to saved_jobs_lell.csv")

if __name__ == "__main__":
    main()