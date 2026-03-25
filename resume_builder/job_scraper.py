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
from git import Repo
from pyvirtualdisplay import Display
import logging

# Load environmental variables from .env file
load_dotenv()

# Configure the logging
logging.basicConfig(
    filename='job_scraper.log',  # Name of the log file
    level=logging.INFO,   # Minimum severity level to log
    format='%(asctime)s - %(levelname)s - %(message)s' # Format of the log messages
)

# Start virtual display (so that the code can be run as a cronjob)
display = Display(visible=0, size=(1920, 1080)) # Set visible=0 for true headless operation with display
display.start()

# Gemini
client = genai.Client(api_key=os.environ["GEMINI_KEY"])
chat = client.chats.create(model="gemini-2.5-flash-lite-preview-09-2025")

# SQLAlchemy
ssl_args = {
    'sslmode': os.environ["SSL_MODE"],
    'sslrootcert': os.environ["SSL_ROOT"],
}
engine = create_engine(os.environ["SQLA_CONN_STRING"], connect_args=ssl_args)

# Selenium
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(30)

def db_connect():

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
        logging.error(f"Database error: {e}")
        raise

    return job_url_list, df_companies, cur, conn

def process_link(company_name, url, tag_link, job_url_list, cur, conn, dropdown_id=None, dropdown_value=None):

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

        # initialize set to store links
        found_links = set()

        # loop through links on webpage
        for anchor_tag in soup.find_all('a', href=True):
            href = anchor_tag['href']
            job_title = anchor_tag.get_text(strip=True)
            absolute_url = urljoin(url, href)

            # if the link meets the criteria for a job posting
            if (absolute_url not in found_links) and (tag_link in absolute_url) and (urlparse(url).netloc in absolute_url):
                found_links.add(absolute_url)
                date_today = datetime.datetime.now().date()

                # open link and extract job description info
                if absolute_url not in job_url_list:
                    driver.get(absolute_url)
                    time.sleep(15)
                    job_html_content = driver.page_source
                    job_soup = BeautifulSoup(job_html_content, 'html.parser')
                    job_text = job_soup.get_text()

                    # use Gemini to extract job info
                    extracted_job_description = chat.send_message(
                        f"Extract the job description and job requirements from the following text and only provide the job description and job requirements: {job_text}"
                    ).text
                    extracted_job_location = chat.send_message(
                        f"Extract the job location from the following text and only provide a list of the cities: {job_text}"
                    ).text.replace("\n",",")

                    # if the job location is remote
                    if 'remote' in extracted_job_location.lower():
                        extracted_job_location = "Remote"

                    # if Metrolinx, job title is in the description and locations are actually addresses
                    if company_name == "Metrolinx":
                        job_title = chat.send_message(
                            f"Extract the job title from the following text and only provide the job title: {job_text}"
                        )
                        extracted_job_location = "Canada"

                    # after job description/location extract, we insert into the job bank database
                    if ("**job description" in extracted_job_description.lower()) and ("skip to results" not in job_title.lower()):
                        values = (company_name, job_title, absolute_url, date_today, extracted_job_location, extracted_job_description)
                        cur.execute(
                            "INSERT INTO job_bank (comp_name, job_title, job_posting_url, date_accessed, job_location, job_description) VALUES (%s, %s, %s, %s, %s, %s)",
                            values)
                        conn.commit()

    except Exception as e:
        logging.warning(f"Failed for website: {url}\n Error: {e}")


def build_job_html():
    with engine.connect() as sqlalc_conn:
        query = f"SELECT comp_name, job_location, job_title, job_posting_url FROM job_bank ORDER BY job_id DESC LIMIT 100"
        df_jobs = pd.read_sql_query(query, sqlalc_conn)
        df_jobs['link'] = df_jobs.apply(lambda x: f'<a href="{x["job_posting_url"]}">{x["job_title"]}</a>', axis=1)
        df_jobs = df_jobs.drop(columns=['job_title', 'job_posting_url'])
        html_table = df_jobs.to_html(escape=False)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_page = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Job Bank</title>
            <style>
                table {{ border-collapse: collapse; width: 50%; }}
                th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h2>Job Bank Dataframe</h2>
            <p>Last updated: {timestamp}<br>
            This dataframe contains job posting data scraped through Selenium using cronjob.<br>
            The HTML file is then pushed to Github pages using GitPython.<br>
            This table only contains the last 100 entries.</p>
            {html_table}
        </body>
        </html>
        """

        with open("/home/hai/PycharmProjects/hbao12.github.io/site_files/jobs.html", "w") as f:
            f.write(html_page)


def git_push():
    repo = Repo(r'/home/hai/PycharmProjects/hbao12.github.io')
    repo.index.add(['site_files/jobs.html'])  # Stages all modified/deleted files
    repo.index.commit('Automated commit from Python script')  # Commits the staged changes
    origin = repo.remote(name='origin')  # Gets the 'origin' remote
    origin.push()  # Pushes the committed changes
    logging.info('Code successfully pushed. Scrape completed.')

if __name__ == "__main__":
    logging.info("Job scrape start.")
    job_url_list, df_companies, cur, conn = db_connect()
    df_companies = df_companies.apply(lambda x: process_link(x.company_name, x.company_job_link_url, x.company_job_link_tag, job_url_list, cur, conn, x.dropdown_id, x.dropdown_value), axis=1)
    driver.close()
    build_job_html()
    git_push()
    display.stop()