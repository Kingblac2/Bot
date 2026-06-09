import os
import httpx
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Set up Streamlit Page Page Config
st.set_page_config(
    page_title="Gemini AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern visual layout & style adjustments
st.markdown("""
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container styling tweaks */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 900px;
    }
    
    /* Glassmorphism sidebar info card */
    .sidebar-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Accent text */
    .accent-text {
        font-weight: 600;
        color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)


# --- API Helper Functions ---
def get_backend_health() -> dict:
    """
    Checks the status of the FastAPI backend.
    """
    try:
        response = httpx.get(f"{BACKEND_URL}/health", timeout=3.0)
        if response.status_code == 200:
            return response.json()
        return {"status": "degraded", "gemini_configured": False, "model_configured": ""}
    except Exception as e:
        return {"status": "offline", "gemini_configured": False, "model_configured": f"Connection error: {str(e)}"}


def query_chatbot(messages: list, system_instruction: str = None) -> tuple[str, bool]:
    """
    Sends message history to backend chat endpoint and returns (response_text, is_success).
    """
    payload = {
        "messages": messages,
        "system_instruction": system_instruction if system_instruction else None
    }
    
    try:
        # Send POST request to FastAPI /chat endpoint
        response = httpx.post(
            f"{BACKEND_URL}/chat",
            json=payload,
            timeout=60.0  # Allow adequate time for Gemini to process
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response content received."), True
        else:
            # Try to extract detailed error from response
            try:
                error_detail = response.json().get("detail", "Unknown backend error.")
            except Exception:
                error_detail = f"Server returned status {response.status_code}: {response.text}"
            return error_detail, False
            
    except httpx.ConnectError:
        return f"Unable to reach the backend service at {BACKEND_URL}. Please verify if the backend container or server is running.", False
    except httpx.TimeoutException:
        return "The request to the AI model timed out. Please try again.", False
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}", False


# --- App Header ---
st.title("🤖 Gemini AI Chatbot")
st.markdown("A production-ready full-stack chatbot powered by FastAPI, Streamlit, and Google Gemini.")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # 1. Health Status Indicators
    st.subheader("System Status")
    health = get_backend_health()
    
    if health.get("status") == "healthy":
        st.success("● Backend: Online")
        if health.get("gemini_configured"):
            st.info(f"🧬 Model: {health.get('model_configured')}")
        else:
            st.warning("⚠️ API Key is missing on backend!")
    elif health.get("status") == "degraded":
        st.warning("● Backend: Degraded (No API Key)")
    else:
        st.error("● Backend: Offline")
        st.caption(f"Backend URL: {BACKEND_URL}")
        st.info("ℹ️ If the backend is deployed on Render's free tier, it spins down after inactivity. It can take 50-70 seconds to wake up on the first request.")
        
    st.divider()
    
    # 2. Chat Settings
    st.subheader("Chat Settings")
    system_instruction = st.text_area(
        "System Instruction (Optional)",
        placeholder="e.g. 'You are a helpful assistant who is an expert in computer science. Respond concisely.'",
        help="Instructions to guide the AI chatbot's persona and response guidelines."
    )
    
    st.divider()
    
    # 3. Actions / Utility Buttons
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.success("Chat history cleared!")
        st.rerun()

    # Footer Card
    st.markdown(f"""
    <div class="sidebar-card">
        <h4>About this Application</h4>
        <p>This UI interacts directly with a FastAPI backend, which handles API key validations and interfaces securely with the Gemini model.</p>
        <p><strong>Stack:</strong> FastAPI, Streamlit, Docker, google-generativeai</p>
    </div>
    """, unsafe_allow_html=True)


# --- Conversation State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Message Rendering ---
# Display previous conversation messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# --- Chat Input & Request Execution ---
if prompt := st.chat_input("Type your message here..."):
    # 1. Reject empty messages
    clean_prompt = prompt.strip()
    if not clean_prompt:
        st.error("Message cannot be empty.")
    else:
        # 2. Append and display user message
        st.session_state.messages.append({"role": "user", "content": clean_prompt})
        with st.chat_message("user"):
            st.markdown(clean_prompt)

        # 3. Request Gemini response from backend
        with st.chat_message("assistant"):
            # Show a spinner typing indicator
            with st.spinner("Thinking..."):
                response_text, success = query_chatbot(
                    messages=st.session_state.messages,
                    system_instruction=system_instruction
                )
            
            if success:
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            else:
                st.error("Error generating response.")
                st.warning(response_text)
                # Remove the user message from state so it can be re-sent once corrected
                # (Optional behavior: allows user to retry without breaking history stream)
                st.info("Ensure the backend server is running and GEMINI_API_KEY is configured in your .env file.")
                st.session_state.messages.pop()  # Pop the failed message out of context
