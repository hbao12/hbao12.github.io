import pandas as pd
from google import genai
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin
from urllib.parse import urlparse
import datetime

import time
load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_KEY"])
chat = client.chats.create(model="gemini-2.5-flash-lite-preview-09-2025")


options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def process_link(company_name, url, tag_link):
    driver.get(url)
    time.sleep(15)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    job_bank = pd.read_csv("job_bank.csv")

    found_links = set()
    list_of_dicts = []

    for anchor_tag in soup.find_all('a', href=True):
        href = anchor_tag['href']
        text = anchor_tag.get_text(strip=True)
        absolute_url = urljoin(url, href)

        if (absolute_url not in found_links) and (tag_link in absolute_url) and (urlparse(url).netloc in absolute_url):
            found_links.add(absolute_url)
            date_today = datetime.datetime.now().strftime("%Y-%m-%d")
            if not (job_bank['job_url'] == absolute_url).any():
                list_of_dicts.append({'company': company_name, 'job_title': text, 'job_url': absolute_url, 'job_date': date_today})


    if len(list_of_dicts) > 0:
        df_new_jobs = pd.DataFrame(list_of_dicts)
        df_job_bank = pd.concat([job_bank, df_new_jobs])
        df_job_bank.to_csv("job_bank.csv", index=False)



df_companies = pd.read_csv("company_list.csv")
df_companies = df_companies.apply(lambda x: process_link(x.company, x.url, x.job_link_tag), axis=1)
driver.close()
