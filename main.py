from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from typing import Dict
import os

load_dotenv()

from google.generativeai import configure, GenerativeModel

app = FastAPI()


# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input):
    model = GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file.file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

input_prompt = """
Hey Act Like a skilled or very experienced ATS(Application Tracking System)
with a deep understanding of the tech field, software engineering, data science, data analyst,
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
the best assistance for improving the resumes. Assign the percentage Matching based 
on JD and
the missing keywords with high accuracy
resume: {text}
description: {jd}

I want the response in one single string having the structure
{"JD Match": "%", "MissingKeywords": [], "Profile Summary": ""}
"""

@app.post("/submit")
async def submit_resume(data: Dict[str, str] = Form(...)):
    try:
        response = get_gemini_response(input_prompt.format(text=data['resume'], jd=data['jd']))
        return JSONResponse(content={"response": response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        text = input_pdf_text(file)
        return JSONResponse(content={"text": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



