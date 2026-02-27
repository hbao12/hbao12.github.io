from docx import Document
from docx.shared import RGBColor
from google import genai
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
from docx_parser_converter import docx_to_html
import datetime
from docx2pdf import convert
import os
import subprocess


load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_KEY"])
chat = client.chats.create(model="gemini-2.5-flash-lite-preview-09-2025")

def convert_docx_to_pdf(input_file, output_dir=None):
    if output_dir is None:
        # Use the same directory as the input file
        output_dir = os.path.dirname(os.path.abspath(input_file))

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # The command to run LibreOffice in headless mode
    command = [
        'libreoffice',
        '--headless',
        '--convert-to',
        'pdf',
        '--outdir',
        output_dir,
        input_file
    ]

    try:
        # Run the command
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e.stderr.decode()}")
    except FileNotFoundError:
        print("Error: libreoffice executable not found. Make sure LibreOffice is installed and in your PATH.")

def create_resume(filename, company_name=None, company_address=None, company_code=None, description=None):
    """
    Create a customized resume using Gemini
    """
    try:
        # Open the .docx file
        document = Document(filename)
        fullText = []

        # Iterate through all paragraphs and append their text
        for para in document.paragraphs:
            fullText.append(para.text)

        # Join the list of paragraph strings with newlines
        resume_text = '\n'.join(fullText)

        # if job description is provided, tailor resume statement to it

        if description:
            resume_statement = chat.send_message(
                f"Read the following text denoted by triple backticks and generate a single resume statement that is 70 words or less based on the "
                f"job description denoted by double backticks. ```{resume_text}``` ``{description}``"
            )
            cover_letter = chat.send_message(
                f"Read the following text denoted by triple backticks and generate a cover letter based on the"
                f"job description denoted by double backticks. ```{resume_text}``` ``{description}``."
                f"The company name is {company_name}."
                f"The company address is {company_address}."
                f"The date is {datetime.date.today()}"
                f"Today's date is {datetime.date.today()}"
                f"My name is Hai Bao"
                f"My address is 25 Viking Lane, Unit 1846, Etobicoke, ON, M9B0A1"
                f"My phone number is 647-831-8623"
                f"My email address is hbao12@gmail.com"
            )
            cover_letter_text = cover_letter.text.replace("[Company Name]",company_name).replace("[Company Address]",company_address).replace("*","")

        else:
            resume_statement = chat.send_message(
                f"Read the following text denoted by triple backticks and generate a single resume statement that is 70 words or less.```{resume_text}```")

        # replacement default statement with generated statement
        document.paragraphs[7].text = resume_statement.text.replace("*","")
        document.paragraphs[7].runs[0].font.color.rgb = RGBColor(66, 66, 66)
        document.paragraphs[7].runs[0].font.size = 114300
        document.paragraphs[7].runs[0].font.name = "Merriweather"
        document.paragraphs[7].runs[0].bold = False

        # date string
        date_string = datetime.datetime.now().strftime("%Y_%m_%d")

        # create cover letter
        if description:
            document.save(f'resume/resume_{company_code}_{date_string}.docx')
            cover_letter_docx = Document()
            cover_letter_docx.add_paragraph(cover_letter_text)
            cover_letter_docx.save(f'resume/coverletter_{company_code}_{date_string}.docx')

        # create html version of resume
        html_content = docx_to_html(f"resume/resume_{company_code}_{date_string}.docx").replace("font-size: 9pt","font-size: 14pt").replace("font-size: 11pt", "font-size: 14pt").replace("font-size: 10pt", "font-size:16pt").replace("body { padding: 14pt 36pt 17pt 36pt; }","body { padding: 14pt 36pt 17pt 36pt; margin-left: 0; width: 50% }")
        soup = BeautifulSoup(html_content, "html.parser")
        html_content = soup.prettify()
        with open(f"resume/resume_{company_code}_{date_string}.html", "w", encoding="utf-8") as file:
            file.write(html_content)

        # create pdf version of resume
        convert_docx_to_pdf(f"resume/resume_{company_code}_{date_string}.docx")

    except Exception as error:
        print(f"Error: {error}")

def main(company_name=None, company_address=None, company_code=None, job_description=None):

    file_path = "Resume_ATSF.docx"
    create_resume(file_path, company_name, company_address, company_code, job_description)

if __name__ == "__main__":
    job_description = """
Job Title: Data Scientist    
    
Job Description

Undergraduate degree required, advanced technical degree ,relevant experience; higher degree education and research tenure can be counted.
Strong understanding of Data Science algorithms from a mathematical and statistical standpoint.
Proven track record in developing end-to-end Data Science projects going through the different phases (ETL, EDA, Model Development, Code Refactoring)
Experience with Git Hub
Experience with structured and unstructured data, feature engineering, and model interpretability techniques
Experience writing clear, maintainable, and extensible code
Excellent verbal and written communication skills, with the ability to explain complex policies and procedures clearly.
Experience in developing standardized workflows and processes to support compliance and governance.
Strong understanding of model lifecycle management (e.g., development, validation, implementation, and monitoring).
Strong organizational skills to manage multiple tasks and deadlines.
Excellent problem solving, analytical, and strategic thinking skills, with the capability to remove obstacles and recommend implementable solutions.
Skill in using Microsoft office such as Word, Excel, PowerPoint; knowledge of data analytical tools is an asset.
A proactive approach to process improvement and identifying best practices for compliance.
Proven ability to collaborate effectively with cross-functional teams such as MRM/MV and COMO; facilitate alignment on governance requirements is considered a plus
Understand business context and data infrastructure and translate business problems to viable data science solutions.
Use a wide range of programing languages (e.g. Python) and techniques for extracting and preparing data, applying statistics and various advanced analytics, along with business acumen to extract insights from the big data.
Visualize insights from the data to tell and illustrate stories that clearly convey the meaning of results to decision-makers and stakeholders at every level of technical understanding.
Collaborate with other partners, such as data and business analysts, software engineer, data engineers, and application developers to develop scalable and sustainable data science solutions that retains long term benefit to the business
EXPERIENCE AND / OR EDUCATION
Undergraduate degree or advanced technical degree preferred (e.g., math, physics, engineering, finance or computer science) Graduate's degree preferred with either progressive project work experience or
3+ year of relevant experience; higher degree education and research tenure can be counted.
    """
    company_name = "TD(Canada)"
    company_code = "TD_DS"
    company_address = chat.send_message(
        f"Get the company address for the following company: {company_name}"
    ).text
    #main(company_name, company_address, company_code, job_description)
    main()



