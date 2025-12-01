import os
import re
import uuid
import logging
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from pypdf import PdfReader

# ADK Imports
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# --- 1. CONFIGURATION ---
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    api_key = os.getenv("gemapi")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    else:
        print("❌ Warning: GOOGLE_API_KEY or 'gemapi' not found.")

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 2. SETUP APP ---
app = FastAPI(title="Career Catalyst API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. AGENT DEFINITION ---
retry_config = types.HttpRetryOptions(attempts=3)

career_agent = LlmAgent(
    name="CareerCoach",
    model=Gemini(model="gemini-2.0-flash-lite-preview-02-05", retry_options=retry_config),
    description="A career coaching agent.",
    instruction="""
    You are an expert Career Coach and Resume Writer.
    
    INPUT:
    1. A Resume (text)
    2. A Job Description (text)
    
    TASK:
    1. Analyze the Job Description for keywords.
    2. Rewrite the Resume to highlight matching skills.
    3. Write a persuasive Cover Letter.
    
    OUTPUT:
    You MUST return the result in this EXACT markdown format:
    
    # RESUME
    (The content of the tailored resume)
    
    # COVER LETTER
    (The content of the cover letter)
    """
)

# --- 4. HELPERS ---

async def parse_resume_file(file: UploadFile) -> str:
    """Reads PDF or Text files and returns string content."""
    filename = file.filename.lower()
    content_bytes = await file.read()
    
    if filename.endswith(".pdf"):
        try:
            pdf_file = io.BytesIO(content_bytes)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"PDF Error: {e}")
            return "Error reading PDF. Please ensure it is text-based."
    else:
        # Assume text/markdown
        return content_bytes.decode("utf-8")

# --- 5. ROUTES ---

@app.get("/")
def health_check():
    """Fixes the 404 error on Render dashboard"""
    return {"status": "Career Catalyst API is Online 🚀"}

@app.post("/optimize")
async def optimize_career(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    try:
        # 1. Parse File (PDF/Text)
        resume_text = await parse_resume_file(resume_file)
        
        # 2. Setup Runner
        session_service = InMemorySessionService()
        runner = Runner(
            agent=career_agent,
            app_name="career_app",
            session_service=session_service
        )
        
        # 3. CRITICAL FIX: Explicitly Create Session
        # This prevents the "Session Not Found" / 500 Error
        session_id = str(uuid.uuid4())
        await session_service.create_session(
            app_name="career_app", 
            user_id="web_user", 
            session_id=session_id
        )
        
        # 4. Construct Prompt
        prompt = (
            f"JOB DESCRIPTION:\n{job_description}\n\n"
            f"RESUME CONTENT:\n{resume_text}\n\n"
            "Action: Tailor the resume and write a cover letter based on the JD."
        )
        
        logger.info(f"🤖 Processing resume: {resume_file.filename}")
        full_response = ""

        # 5. Run Agent
        async for event in runner.run_async(
            new_message=types.Content(parts=[types.Part(text=prompt)]),
            session_id=session_id,
            user_id="web_user"
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        full_response += part.text

        # 6. Parse Response (The Safety Net)
        resume_content = "Could not generate resume."
        cover_letter_content = "Could not generate cover letter."
        
        # Split by the headers we requested in the system prompt
        if "# RESUME" in full_response and "# COVER LETTER" in full_response:
            parts = full_response.split("# COVER LETTER")
            resume_part = parts[0].replace("# RESUME", "").strip()
            cover_part = parts[1].strip()
            
            resume_content = resume_part
            cover_letter_content = cover_part
        else:
            # Fallback: Return raw text in resume if formatting failed
            resume_content = full_response

        return {
            "resume_content": resume_content,
            "cover_letter_content": cover_letter_content
        }

    except Exception as e:
        logger.error(f"❌ Error in /optimize: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
