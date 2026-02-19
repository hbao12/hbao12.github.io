from docx import Document
from docx.enum.text import WD_BREAK
from google import genai
from dotenv import load_dotenv
import mammoth
import os
from docx_parser_converter import docx_to_html


load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_KEY"])
chat = client.chats.create(model="gemini-2.5-flash-lite-preview-09-2025")


job_description = """
We’re looking for a Data Scientist to join our Triangle Data Products team. You’ll help build and enhance models that drive targeted offers, recommendations, and customer engagement for millions of loyalty members. This role is ideal for someone early in their career who wants to grow into applied ML, experimentation, and production systems.

What You’ll Do

Support the development of machine learning models for offer personalization, customer propensity, next-best-product, and related use cases. 
Explore, clean, and analyze large datasets to uncover insights and trends. 
Build prototypes, run experiments, and contribute to model evaluation and validation. 
Work with engineering teams to integrate models into production pipelines. 
Help maintain and optimize existing ML workflows (Airflow, Dataproc, on-prem clusters, or cloud platforms). 
Build dashboards and reports that communicate findings to business partners. 
Participate in code reviews and follow team best practices. 

What You Bring

2+ years of experience in data science or applied machine learning. 
Strong Python skills with exposure to ML libraries (e.g., scikit-learn, XGBoost, LightGBM). 
Solid SQL skills and comfort working with large datasets. 
Understanding of core ML concepts: regression, classification, validation, feature engineering. 
Curiosity, problem-solving ability, and willingness to learn deeper modeling and production skills. 
Ability to communicate analytical findings clearly and concisely. 
Exposure to recommendation systems or marketing analytics is an asset. 
Experience with A/B testing or experiment analysis is an asset.. 
Familiarity with Airflow, Docker, cloud compute (GCP/Azure), or distributed systems is an asset. 
Knowledge of embeddings, uplift modeling, or personalization frameworks is an asset. 
"""

def create_resume(filename, description):
    """
    Extracts all text from a .docx file.
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

        if description:
            response = chat.send_message(
                f"Read the following text denoted by triple backticks and generate a single resume statement that is 70 words or less based on the "
                f"job description denoted by double backticks. ```{resume_text}``` ``{description}``"
            )
        else:
            response = chat.send_message(
                f"Read the following text denoted by triple backticks and generate a single resume statement that is 70 words or less.```{resume_text}```")

        document.paragraphs[7].text = response.text

        document.save('resume_edited.docx')

        html_content = docx_to_html("resume_edited.docx").replace("font-size: 9pt","font-size: 14pt").replace("font-size: 11pt", "font-size: 14pt").replace("font-size: 10pt", "font-size:16pt").replace("body { padding: 14pt 36pt 17pt 36pt; }","body { padding: 14pt 36pt 17pt 36pt; margin-left: 0; width: 50% }")
        with open("resume.html", "w", encoding='utf-8') as file:
            file.write(html_content)
    except Exception as error:
        return f"Error: {error}"


# Example usage:
file_path = "Resume_ATSF.docx"
print(create_resume(file_path, job_description))
