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

    # create resume
    document.save(f'resume/resume_{company_code}_{date_string}.docx')

    # create cover letter
    if description:
        cover_letter_docx = Document()
        cover_letter_docx.add_paragraph(cover_letter_text)
        cover_letter_docx.save(f'resume/coverletter_{company_code}_{date_string}.docx')

    # create html version of resume
    resume_file_name = f"resume_{company_code}_{date_string}"
    if not description:
        resume_file_name = f"resume_None_{date_string}"
    html_content = docx_to_html(f"resume/{resume_file_name}.docx").replace("font-size: 9pt","font-size: 14pt").replace("font-size: 11pt", "font-size: 14pt").replace("font-size: 10pt", "font-size:16pt").replace("body { padding: 14pt 36pt 17pt 36pt; }","body { padding: 14pt 36pt 17pt 36pt; margin-left: 0; width: 50% }")
    soup = BeautifulSoup(html_content, "html.parser")
    html_content = soup.prettify()
    if description:
        with open(f"resume/resume_{company_code}_{date_string}.html", "w", encoding="utf-8") as file:
            file.write(html_content)
    else:
        with open(f"resume.html", "w", encoding="utf-8") as file:
            file.write(html_content)

    # create pdf version of resume
    convert_docx_to_pdf(f"resume/resume_{company_code}_{date_string}.docx")

def main(company_name=None, company_address=None, company_code=None, job_description=None):

    file_path = "Resume_ATSF.docx"
    create_resume(file_path, company_name, company_address, company_code, job_description)

if __name__ == "__main__":
    job_description = """
Job Title: Senior Data Scientist 
    
Current Need:

The Senior Data Scientist (DS) will lead the development of advanced analytics and AI solutions that enhance decision intelligence, operational efficiency, and risk management across Oncology & Multispecialty (O&M) Finance. The Sr DS is the core model builder and analytical executor, turning prioritized use cases into working models and insights. This role balances deep technical work with business context, and is critical to delivering fast, credible results.

Key Responsibilities:

Advanced Analytics and AI Execution

Help define and subsequently execute the approach for 1-2 O&M Finance use cases, e.g., Fraud & Risk Management, Financial Controller / Agentic AI, Forecasting, Collections Improvement Analytics

Develop time series forecasting models (short-term, long-term, sparse data), anomaly detection models (transactions, journals, contracts, pricing), scenario modeling for finance decisions, document entity extraction, and agentic workflows

Explore data products and other upstream sources, evaluate data readiness and quality issues, and engineer features from transactional, contract, and time‑series data

Apply statistical rigor to validate accuracy improvements vs legacy methods

Partner with ML engineering support to harden models for production, and help implement monitoring, drift detection, and retraining strategies

Partner with the Technical Product Manager and Lead DS to define scope, success metrics, and solution iteration plans

Ensure explainability and auditability for finance and SOX contexts where necessary

Stakeholder Engagement

Translate business requirements into technical models and logic

Work directly with Finance SMEs to validate assumptions, interpret outputs, and refine models based on real world constraints

Builds strong, trust-based relationships with stakeholders, including business units, data engineering, and executive leadership through high quality work

Understand and resolve issues that arise during UAT in a well-organized manner

Communication and Documentation

Communicate progress, risks, and dependencies to product leadership and seek leadership support where necessary

Create and maintain product documentation, including technical specs, release notes, and user guides

Minimum Requirement:

Degree or equivalent and typically requires 7+ years of relevant experience

Critical Skills

7+ years of professional experience in progressively advancing data science and applied AI/ML roles

Strong background in forecasting, classification, anomaly detection / risk modeling, statistical modeling

Experience working with financial data (AR/AP, GL, contracts)

Clearly demonstrated experience working with Python, SQL

Solid understanding of modern digital architectures, APIs, cloud platforms, data ecosystems, and software development practices

Comfortable explaining model outputs to non‑technical audiences

Additional Skills:

Demonstrated experience implementing Agent workflows and/or LLM-augmented analytics

Experience supporting SOX, audit, or financial controls

Prior work in healthcare, life sciences, or complex B2B finance

Experience with Power BI or similar BI tools

Exposure to ERP / finance systems (SAP, PeopleSoft, etc.)

    """
    company_name = "McKesson (Canada)"
    company_code = "MCK_SDS"
    company_address = chat.send_message(
        f"Get the company address for the following company: {company_name}"
    ).text
    #main(company_name, company_address, company_code, job_description)
    main()



