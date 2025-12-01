import os
import re
import uvicorn
import io
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from google.genai import Client
from google.genai.types import (
    GenerateContentConfig,
    Tool,
    FunctionDeclaration,
    Schema,
    Type
)
from pypdf import PdfReader

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="Career Catalyst API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini Client
client = Client(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Tools ---

def save_tailored_resume(content: str):
    """Saves the tailored resume content."""
    return {"status": "success", "file": "tailored_resume.md", "content": content}

def save_cover_letter(content: str):
    """Saves the cover letter content."""
    return {"status": "success", "file": "cover_letter.md", "content": content}

# Tool Definitions for Gemini
save_tailored_resume_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="save_tailored_resume",
            description="Saves the tailored resume content to a file.",
            parameters=Schema(
                type=Type.OBJECT,
                properties={
                    "content": Schema(type=Type.STRING, description="The full markdown content of the tailored resume.")
                },
                required=["content"]
            )
        )
    ]
)

save_cover_letter_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="save_cover_letter",
            description="Saves the cover letter content to a file.",
            parameters=Schema(
                type=Type.OBJECT,
                properties={
                    "content": Schema(type=Type.STRING, description="The full markdown content of the cover letter.")
                },
                required=["content"]
            )
        )
    ]
)

tools = [save_tailored_resume_tool, save_cover_letter_tool]

# --- Safety Net Logic ---

def manual_save_fallback(full_text_response: str):
    """
    Fallback mechanism to extract resume and cover letter if tools weren't called.
    Looks for markdown blocks or specific headers.
    """
    resume_content = ""
    cover_letter_content = ""

    # Try to find Resume block
    resume_match = re.search(r"##\s*Tailored Resume\s*\n(.*?)(?=\n##|$)", full_text_response, re.DOTALL | re.IGNORECASE)
    if resume_match:
        resume_content = resume_match.group(1).strip()
    else:
        # Fallback: look for generic code block if it's the only thing
        code_blocks = re.findall(r"```(?:markdown)?\n(.*?)```", full_text_response, re.DOTALL)
        if len(code_blocks) >= 1:
            resume_content = code_blocks[0].strip()
        if len(code_blocks) >= 2:
            cover_letter_content = code_blocks[1].strip()

    # Try to find Cover Letter block if not found in code blocks
    if not cover_letter_content:
        cover_match = re.search(r"##\s*Cover Letter\s*\n(.*?)(?=$)", full_text_response, re.DOTALL | re.IGNORECASE)
        if cover_match:
            cover_letter_content = cover_match.group(1).strip()
    
    # If still nothing, just return the whole text as resume (worst case)
    if not resume_content and not cover_letter_content:
        resume_content = full_text_response

    return {
        "resume_content": resume_content,
        "cover_letter_content": cover_letter_content
    }

# --- Agent Logic ---

@app.post("/optimize")
async def optimize_career(
    resume_file: UploadFile,
    job_description: str = Form(...)
):
    try:
        # Read resume content
        content_type = resume_file.content_type
        filename = resume_file.filename.lower()
        
        if filename.endswith(".pdf") or content_type == "application/pdf":
            # Handle PDF
            pdf_bytes = await resume_file.read()
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            resume_content = ""
            for page in reader.pages:
                resume_content += page.extract_text() + "\n"
        else:
            # Handle Text/MD
            resume_content = (await resume_file.read()).decode("utf-8")
        
        prompt = f"""
        You are an expert Career Coach. 
        
        User's Resume:
        {resume_content}
        
        Target Job Description:
        {job_description}
        
        Task:
        1. Read the user's resume and the target job description.
        2. Rewrite the resume to highlight matching skills using keywords from the JD.
        3. Write a compelling cover letter.
        
        You MUST output the content by calling the `save_tailored_resume` and `save_cover_letter` tools.
        If you cannot call the tools, output the content in Markdown format with clear headers "## Tailored Resume" and "## Cover Letter".
        """

        # Call Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite-preview-02-05",
            contents=prompt,
            config=GenerateContentConfig(
                tools=tools,
                temperature=0.7
            )
        )

        # Process Response
        final_output = {"resume_content": "", "cover_letter_content": ""}
        
        # Check for tool calls
        tool_calls_found = False
        if response.function_calls:
             for call in response.function_calls:
                if call.name == "save_tailored_resume":
                    final_output["resume_content"] = call.args["content"]
                    tool_calls_found = True
                elif call.name == "save_cover_letter":
                    final_output["cover_letter_content"] = call.args["content"]
                    tool_calls_found = True

        # Fallback if no tool calls or partial
        if not tool_calls_found or not final_output["resume_content"] or not final_output["cover_letter_content"]:
            # Get text content
            full_text = response.text
            if full_text:
                fallback_data = manual_save_fallback(full_text)
                if not final_output["resume_content"]:
                    final_output["resume_content"] = fallback_data["resume_content"]
                if not final_output["cover_letter_content"]:
                    final_output["cover_letter_content"] = fallback_data["cover_letter_content"]

        return final_output

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
