# Deployment Guide: Career Catalyst

This guide walks you through deploying the **Career Catalyst** application.
- **Backend**: Deployed on [Render](https://render.com/).
- **Frontend**: Deployed on [Vercel](https://vercel.com/).

---

## 1. Backend Deployment (Render)

1.  **Log in to Render** and click **"New +"** -> **"Web Service"**.
2.  **Connect GitHub**: Select your repository `ruthvikgurrala/The-Career-Catalyst`.
3.  **Configure Service**:
    *   **Name**: `career-catalyst-backend` (or similar).
    *   **Root Directory**: `backend` (Important!).
    *   **Runtime**: `Python 3`.
    *   **Build Command**: `pip install -r requirements.txt`.
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
4.  **Environment Variables** (Scroll down to "Advanced"):
    *   Key: `GOOGLE_API_KEY`
    *   Value: `Your_Google_Gemini_API_Key` (Copy this from your local `.env` file).
    *   Key: `PYTHON_VERSION`
    *   Value: `3.11.0` (Optional, but good for stability).
5.  **Deploy**: Click **"Create Web Service"**.
6.  **Wait**: Wait for the deployment to finish. Once live, copy the **onrender.com URL** (e.g., `https://career-catalyst-backend.onrender.com`). You will need this for the frontend.

---

## 2. Frontend Deployment (Vercel)

1.  **Log in to Vercel** and click **"Add New..."** -> **"Project"**.
2.  **Import Git Repository**: Select `The-Career-Catalyst`.
3.  **Configure Project**:
    *   **Framework Preset**: `Vite` (Should be auto-detected).
    *   **Root Directory**: Click "Edit" and select `frontend`.
4.  **Environment Variables**:
    *   Key: `VITE_API_URL`
    *   Value: Paste your **Render Backend URL** (e.g., `https://career-catalyst-backend.onrender.com`). **Do not add a trailing slash `/`**.
5.  **Deploy**: Click **"Deploy"**.
6.  **Visit**: Once deployed, click the domain provided by Vercel to see your live app!

---

## Troubleshooting

*   **Backend 502/Error**: Check the Render logs. Ensure `requirements.txt` is correct and `GOOGLE_API_KEY` is set.
*   **Frontend API Error**: Check the Network tab in your browser's developer tools. Ensure the request is going to your Render URL, not `localhost`. Verify `VITE_API_URL` is set correctly in Vercel.
*   **CORS Issues**: If you see CORS errors, you might need to update the backend `main.py` to explicitly allow the Vercel domain in `CORSMiddleware`, although `allow_origins=["*"]` is currently set, which allows all.
