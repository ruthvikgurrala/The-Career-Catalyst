# Career Catalyst

Career Catalyst is an AI-powered full-stack application that acts as your personal career coach and resume writer. By leveraging Google's adk and Gemini AI models, the application analyzes your existing resume alongside a target job description, and automatically generates a highly tailored resume and a persuasive cover letter to maximize your employment prospects.

## Features

- **AI-Powered Optimization**: Uses `gemini-2.0-flash-lite-preview-02-05` via `google-adk` to intelligently extract keywords from the Job Description and rewrite your resume.
- **Multiple Formats Support**: Upload resumes in PDF, TXT, or MD formats.
- **Side-by-Side View**: A clean, responsive React frontend provides a side-by-side view to compare your inputs and the AI-generated outputs.
- **Copy & Download**: Easily copy the generated Markdown text or download it directly to your machine.

---

## Technical Stack

- **Frontend**: React.js, Vite, CSS (Glassmorphism layout)
- **Backend**: Python, FastAPI, Uvicorn
- **AI Integration**: Google ADK, Google GenAI
- **File Parsing**: PyPDF

---

## Prerequisites

Before running the application, ensure you have the following installed:

- **Node.js** (v18 or higher recommended)
- **Python** (v3.11 or higher recommended)
- **Google Gemini API Key**: You need an active API key to power the AI backend. Grab one from Google AI Studio.

---

## Installation & Setup

### 1. Clone the repository
Navigate into the project base directory where `frontend` and `backend` folders are located.

### 2. Backend Setup
The backend runs on Python and FastAPI.

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the Python dependencies
pip install -r requirements.txt
```

**Environment Variables**
Create a `.env` file in the `backend/` directory and add your Google API key:

```env
GOOGLE_API_KEY=your_actual_gemini_api_key_here
```

### 3. Frontend Setup
The frontend runs on React and Vite.

```bash
# Open a new terminal and navigate to the frontend directory
cd frontend

# Install Node.js dependencies
npm install
```

**Environment Variables (Optional)**
If your backend is running on a port other than `8000`, or if you are deploying, create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000
```
*(By default, the Vite app will point to `http://localhost:8000/optimize` if this is omitted).*

---

## How to Run the Application

You will need two separate terminal windows—one for the backend and one for the frontend.

### Terminal 1: Run the Backend Server
```bash
cd backend

# Ensure your virtual environment is active!
# Start the FastAPI server using Uvicorn
python main.py
# Or run manually: uvicorn main:app --host 0.0.0.0 --port 8000
```
The FastAPI backend will now be listening on `http://localhost:8000`.

### Terminal 2: Run the Frontend Development Server
```bash
cd frontend

# Start the Vite development server
npm run dev
```
Vite will provide you with a local server URL (usually `http://localhost:5173`). Open this URL in your browser to access the Career Catalyst application.

---

## Deployment Configuration

Check the existing `deployment_guide.md` file at the root of the project for step-by-step instructions on deploying the backend to Render and the frontend to Vercel.
