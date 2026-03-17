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
        with open(f"site_files/resume.html", "w", encoding="utf-8") as file:
            file.write(html_content)

    # create pdf version of resume
    convert_docx_to_pdf(f"resume/resume_{company_code}_{date_string}.docx")

def main(company_name=None, company_address=None, company_code=None, job_description=None):

    file_path = "Resume_ATSF.docx"
    create_resume(file_path, company_name, company_address, company_code, job_description)

if __name__ == "__main__":
    job_description = """
Job Title: Data Scientist
    
Job Description
The Global Data Science group supports our bank and merchant partners by using our extraordinarily rich data sets that span more than 4 billion cards globally and captures more than 190 billion transactions in a single year. Our focus lies on building creative solutions that have an immediate impact on the business of our highly analytical partners. To support our rapidly growing scope of work capabilities at the intersection of data science, analytics and AI, we are looking for Senior Data Scientists who are passionate and leading team members and solving complex data problems using Visa rich dataset and technical toolkit. You will join one of the Data Science focus areas (e.g., merchants, issuers, enablers, fintechs) and have the opportunity to engage across the Data Science teams, providing broad exposure to Visa’s business.

Essential Functions:

Use and build new predictive models to innovate and optimize customer experiences, revenue generation, data insights, advertising targeting and other business outcomes
Be an out-of-the-box problem solver who is passionate about applying data science techniques and innovate thinking to our unique data to help our clients both innovate and solve the problems they face
Leverage AI coding tools (e.g., GitHub Copilot, Claude Code, Cline, OpenAI Codex) to accelerate development
Apply data science and GenAI techniques to analyze transaction data and deliver actionable client insights
Build agentic AI systems with multi-step reasoning, tool use, and memory for complex payment decisioning workflows
Work with your data science colleagues as well as other teams across Visa to guide the critical thinking for our clients by using the data and tools available to you
Connect with clients as well as client teams regarding the results and strategic recommendations advised by your analyses
Develop visualizations to make your sophisticated analyses accessible to a broad audience
Find opportunities to craft products out of analyses that are suitable for multiple clients
Work with partners throughout the organization to explore opportunities for using Visa data to drive business solutions
This is a hybrid position. Expectation of days in office will be confirmed by your hiring manager.

Qualifications
Basic Qualifications:

2 or more years of work experience with a Bachelor’s Degree or an Advanced Degree (e.g. Masters, MBA, JD, MD, or PhD)

Preferred Qualifications:

3 or more years of work experience with a Bachelor’s Degree or more than 2 years of work experience with an Advanced Degree (e.g. Masters, MBA, JD, MD)
2+ years’ experience in data-based decision-making or quantitative analysis, including exposure to LLMs and GenAI applications
Bachelor’s degree in an analytical field such as statistics, operations research, economics, computer science or many others (graduate degree is a plus)
Experience in understanding and analyzing data using Python or Other statistical software
Experience with extracting and aggregating data from large data sets using SQL, Hive, Spark or other tools
Experience and comfort with machine learning techniques and accompanying packages.
Experience with LLM orchestration frameworks (LangChain or similar), vector databases, and embedding models
Competence in Excel, PowerPoint and Tableau
Previous exposure to financial services, credit cards or merchant analytics is a plus, but not required
    """
    company_name = "VISA (Canada)"
    company_code = "VISA_DS"
    company_address = chat.send_message(
        f"Get the company address for the following company: {company_name}"
    ).text
    main(company_name, company_address, company_code, job_description)
    #main()



