from openai import OpenAI
import fitz  # PyMuPDF
from typing import Union
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Set the OpenAI API key

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def process_cv(content: Union[str, bytes], file_type: str):
    if file_type == 'application/pdf':
        content = extract_text_from_pdf(content)
    elif isinstance(content, bytes):
        content = content.decode('utf-8')
    extracted_info = extract_info_with_gpt4(content)
    assessment = assess_qualification(extracted_info)
    return {"extracted_info": extracted_info, "assessment": assessment}

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_info_with_gpt4(content: str):
    prompts = {
        "Awards": "Extract any nationally or internationally recognized awards mentioned in this CV.",
        "Membership": "Extract memberships in associations that require outstanding achievements.",
        "Press": "Extract any published material in professional or major trade publications about the beneficiary.",
        "Judging": "Extract evidence of participation as a judge of the work of others.",
        "Original contribution": "Extract evidence of original scientific, scholarly, or business-related contributions of major significance.",
        "Scholarly articles": "Extract evidence of authorship of scholarly articles.",
        "Critical employment": "Extract evidence of employment in a critical or essential capacity for distinguished organizations.",
        "High remuneration": "Extract evidence of commanding a high salary or other remuneration."
    }

    extracted_info = {}
    for criterion, prompt in prompts.items():
        response = client.chat.completions.create(model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{prompt}\n\nCV:\n{content}"}
        ])
        extracted_info[criterion] = response.choices[0].message.content.strip()
    return extracted_info

def assess_qualification(extracted_info):
    assessment = {}
    thresholds = {
        "Awards": {"low": 1, "medium": 2, "high": 3},
        "Membership": {"low": 1, "medium": 2, "high": 3},
        "Press": {"low": 1, "medium": 2, "high": 3},
        "Judging": {"low": 1, "medium": 2, "high": 3},
        "Original contribution": {"low": 1, "medium": 2, "high": 3},
        "Scholarly articles": {"low": 1, "medium": 2, "high": 3},
        "Critical employment": {"low": 1, "medium": 2, "high": 3},
        "High remuneration": {"low": 1, "medium": 2, "high": 3},
    }

    for criterion, info in extracted_info.items():
        count = len(info.split('\n'))  # Simplistic way to count relevant entries by counting number of new chunks       
        if count >= thresholds[criterion]["high"]:
            assessment[criterion] = "high"
        elif count >= thresholds[criterion]["medium"]:
            assessment[criterion] = "medium"
        else:
            assessment[criterion] = "low"

    return assessment

 
