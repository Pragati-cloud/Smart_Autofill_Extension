from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import json
import os
from io import BytesIO
from dotenv import load_dotenv
from openai import OpenAI
import re

# --- Import from services ---
from services.text_extractor import (
    extract_personal_info,
    extract_skills,
    extract_education,
    extract_projects
)

load_dotenv()
client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# PDF PARSER FUNCTION
# -----------------------------
def parse_pdf(file: UploadFile):
    try:
        pdf_bytes = file.file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text.strip()
    except Exception as e:
        return f"PDF parsing error: {str(e)}"

# -----------------------------
# ROUTE 1: Upload and parse PDF
# -----------------------------
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile):
    try:
        extracted_text = parse_pdf(file)
        if extracted_text.startswith("PDF parsing error"):
            return {"error": extracted_text}
        return {"raw_text": extracted_text}
    except Exception as e:
        return {"error": str(e)}

# -----------------------------
# ROUTE 2: Analyze text (from PDF or direct)
# -----------------------------
@app.post("/analyze-raw-text")
async def analyze_raw_text(
    raw_text: str = Form(...),
    use_ai: bool = Form(True)
):
    try:
        # Step 1: Basic parsing using regex + heuristics
        base_data = {
            "personal_info": extract_personal_info(raw_text),
            "skills": extract_skills(raw_text),
            "education": extract_education(raw_text),
            "projects": extract_projects(raw_text),
        }

        # Step 2: AI enhancement
        if use_ai:
            prompt = f"""
You are a structured resume parser.
Extract the following from the resume text and return clean JSON:
- name
- email
- phone
- linkedin
- github
- portfolio (personal website if available)
- education (list of degree, institute, year)
- skills (list)
- projects (list of title + short description)
- experience (if found)
- achievements (if found)

Resume text:
{raw_text}

Initial extraction (context):
{json.dumps(base_data, indent=2)}
Return ONLY pure JSON. No explanation. No markdown. No code blocks. No ``` .

"""
            completion = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a structured resume parsing assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
            )

            ai_output = completion.choices[0].message.content

            # Try to convert to JSON
            try:
                structured = json.loads(ai_output)
            except:
                structured = {"ai_output": ai_output}

            return {
                "parsed_data": structured,
                "raw_extracted": base_data
            }

        return {"parsed_data": base_data, "raw_text": raw_text}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# -----------------------------
# ROUTE 3: Direct analyze file (combo)
# -----------------------------
@app.post("/analyze-file")
async def analyze_file(file: UploadFile):
    """Upload a file → extract text → run AI parser."""
    try:
        extracted_text = parse_pdf(file)
        if not extracted_text or extracted_text.startswith("PDF parsing error"):
            return {"error": "Unable to parse PDF."}

        # Send text for AI-based parsing
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an intelligent resume parser."},
                {"role": "user", "content": f"Parse this resume text into JSON:\n{extracted_text}"}
            ],
            temperature=0.2,
        )
        result = completion.choices[0].message.content
        try:
            data = json.loads(result)
        except:
            data = {"ai_output": result}

        return {"parsed_data": data, "raw_text": extracted_text}

    except Exception as e:
        return {"error": str(e)}
