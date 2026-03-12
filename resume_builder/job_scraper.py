import pandas as pd
from google import genai
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from urllib.parse import urljoin
from urllib.parse import urlparse
import datetime
import psycopg2
from sqlalchemy import create_engine
import time

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_KEY"])
chat = client.chats.create(model="gemini-2.5-flash-lite-preview-09-2025")
ssl_args = {
    'sslmode': os.environ["SSL_MODE"],
    'sslrootcert': os.environ["SSL_ROOT"],
}
engine = create_engine(os.environ["SQLA_CONN_STRING"], connect_args=ssl_args)

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(30)

try:

    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PW"],
        sslmode=os.environ["SSL_MODE"],
        sslrootcert=os.environ["SSL_ROOT"]
    )
    cur = conn.cursor()

    with engine.connect() as sqlalc_conn:
        query = f"SELECT job_posting_url FROM job_bank"
        df_links = pd.read_sql_query(query, sqlalc_conn)
        job_url_list = df_links['job_posting_url'].to_list()
        query2 = f"SELECT company_name, company_job_link_url, company_job_link_tag, dropdown_id, dropdown_value FROM company_list"
        df_companies = pd.read_sql_query(query2, sqlalc_conn)

except Exception as e:
    print(f"Database error: {e}")
    raise

def process_link(company_name, url, tag_link, dropdown_id=None, dropdown_value=None):
    try:
        # go to website
        driver.get(url)
        time.sleep(15)

        # if website has dropdown for "most recent" jobs
        if dropdown_id:
            dropdown = driver.find_element(By.ID, dropdown_id)
            Select(dropdown).select_by_value(dropdown_value)
            time.sleep(15)

        # parse html
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')


        found_links = set()

        for anchor_tag in soup.find_all('a', href=True):
            href = anchor_tag['href']
            job_title = anchor_tag.get_text(strip=True)
            absolute_url = urljoin(url, href)

            if (absolute_url not in found_links) and (tag_link in absolute_url) and (urlparse(url).netloc in absolute_url):
                found_links.add(absolute_url)
                date_today = datetime.datetime.now().date()
                if absolute_url not in job_url_list:
                    # open link and extract job description info
                    driver.get(absolute_url)
                    time.sleep(15)
                    job_html_content = driver.page_source
                    job_soup = BeautifulSoup(job_html_content, 'html.parser')
                    job_text = job_soup.get_text()

                    extracted_job_description = chat.send_message(
                        f"Extract the job description and job requirements from the following text and only provide the job description and job requirements: {job_text}"
                    ).text
                    extracted_job_location = chat.send_message(
                        f"Extract the job location from the following text and only provide a list of the cities: {job_text}"
                    ).text.replace("\n",",")

                    # after job description/location extract, we insert into the job bank database
                    if "**job description" in extracted_job_description.lower():
                        values = (company_name, job_title, absolute_url, date_today, extracted_job_location, extracted_job_description)
                        cur.execute(
                            "INSERT INTO job_bank (comp_name, job_title, job_posting_url, date_accessed, job_location, job_description) VALUES (%s, %s, %s, %s, %s, %s)",
                            values)
                        conn.commit()
    except Exception as e:
        print(f"Failed for website: {url}\n Error: {e}")

df_companies = df_companies.apply(lambda x: process_link(x.company_name, x.company_job_link_url, x.company_job_link_tag, x.dropdown_id, x.dropdown_value), axis=1)
driver.close()
