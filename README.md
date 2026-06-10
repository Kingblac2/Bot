---
title: Bot
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.37.0"
app_file: frontend/app.py
pinned: false
---



# Full-Stack Gemini AI Chatbot

A production-ready full-stack AI Chatbot application built using **FastAPI** for the backend, **Streamlit** for the frontend, and containerized using **Docker** and **Docker Compose**.

## Architecture & Features

- **Backend (FastAPI)**:
  - Exposes REST API endpoints:
    - `GET /health`: Checks system health and configuration status.
    - `POST /chat`: Receives session messages, structures the conversation, calls Google Generative AI (Gemini), and returns responses.
  - Implements async endpoints using standard `asyncio.to_thread` for non-blocking I/O when processing model generations.
  - Configures CORS middleware to secure and allow requests from the Streamlit client.
  - Features robust middleware logging for request metadata, execution time, and error propagation.

- **Frontend (Streamlit)**:
  - Clean and responsive ChatGPT-like interface utilizing Streamlit's native `st.chat_message` and `st.chat_input` components.
  - Preserves chat session history within `st.session_state`.
  - Side configuration panel to set System Instructions (custom persona/rules) and clear history.
  - Interactive spinner typing indicator while waiting for the model to respond.
  - Graceful connection, network failure, and missing/invalid API key notifications.

- **Deployment**:
  - Multi-stage optimized Docker builds to minimize container footprint.
  - Orchestration via Docker Compose for easy local deployment.

---

## Getting Started

### Prerequisites
- [Google AI Studio Gemini API Key](https://aistudio.google.com/)
- Docker & Docker Compose (optional for local running)
- Python 3.11+ (if running locally without Docker)

---

## Option 1: Running with Docker Compose (Recommended)

1. Clone or download this project.
2. In the root directory, configure your Gemini API Key in the `.env` file:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
3. Run the following command to build and launch both services:
   ```bash
   docker-compose up --build
   ```
4. Once built and running:
   - **Streamlit Frontend**: Access at [http://localhost:8501](http://localhost:8501)
   - **FastAPI Backend**: Access at [http://localhost:8000](http://localhost:8000)
   - **Interactive Swagger Docs**: View endpoints at [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Option 2: Running Locally (Without Docker)

If you do not have Docker installed, you can easily run both services locally in separate terminal windows.

### 1. Set Up Environment Variables
Copy `.env` configuration (make sure `GEMINI_API_KEY` is set):
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your_actual_api_key_here"

# Linux/macOS
export GEMINI_API_KEY="your_actual_api_key_here"
```

### 2. Run the FastAPI Backend
Open a terminal:
```bash
# Navigate to backend folder
cd backend

# Create a virtual environment and activate it
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```
The backend server will start running on [http://localhost:8000](http://localhost:8000).

### 3. Run the Streamlit Frontend
Open a **new** terminal:
```bash
# Navigate to frontend folder
cd frontend

# Create a virtual environment and activate it
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit
streamlit run app.py --server.port 8501
```
The frontend application will load automatically in your web browser at [http://localhost:8501](http://localhost:8501).

---

## Error Handling Scenarios
- **Invalid API Key**: If you enter an invalid API key, the Streamlit app sidebar will report a Degraded status and the chat output will guide you with a warning stating your key is invalid or inactive.
- **Connection Failures**: If the backend server stops, the frontend displays an offline warning on the sidebar and notifies you of the failure to connect.
- **Empty Message Safeguards**: Front and backend code block and validate empty/whitespace prompts.

---

## Deployment Guide (Render + Hugging Face Spaces)

To connect the frontend (Hugging Face) and backend (Render) successfully:

### 1. Backend (FastAPI on Render)
- Select **Web Service** on Render.
- Connect your GitHub repo.
- Configure:
  - **Root Directory**: `backend`
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Add Environment Variables in Render:
  - `GEMINI_API_KEY`: *[Your API Key]*
  - `GEMINI_MODEL_NAME`: `gemini-3.5-flash`
  - `PYTHONPATH`: `.`
- Copy the public Render URL (e.g. `https://your-backend.onrender.com`).

### 2. Frontend (Streamlit on Hugging Face Spaces)
- Select **Streamlit** SDK.
- Push the contents of the `frontend/` directory (just `app.py` and `requirements.txt`) directly to the root of your Hugging Face Space repository.
- Go to Hugging Face Space **Settings** -> **Variables and secrets**.
- Add a Variable:
  - **Name**: `BACKEND_URL`
  - **Value**: `https://your-backend.onrender.com` (Your Render URL)

*Note: Since Streamlit runs server-side on Hugging Face, browser CORS is bypassed automatically for all API calls.*
