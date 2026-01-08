import os
import sqlite3
import streamlit as st
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from datetime import datetime
from PyPDF2 import PdfReader
from PIL import Image

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="BrainWave AI",
    page_icon="🧠",
    layout="wide"
)

# ================= LOAD ENV =================
load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    st.error("❌ GROQ_API_KEY not found. Set it in Streamlit Secrets or .env")
    st.stop()

# ================= DATABASE SETUP =================
DB_PATH = "chat_history.db"

def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            assistant_message TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_message(user_msg, assistant_msg):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_history VALUES (NULL, ?, ?, ?)",
        (user_msg, assistant_msg, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def load_messages():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_message, assistant_message FROM chat_history ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    return rows

def clear_messages():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()

init_db()

# ================= INITIALIZE LLM =================
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

# ================= BRAND HEADER =================
st.markdown("<h1 style='text-align:center;'>🧠 BrainWave AI</h1>", unsafe_allow_html=True)
st.caption("Think Deeper • Ask Smarter • Powered by Grok")

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("## 🧠 BrainWave AI")
    st.info("⬅️ Use this sidebar for controls")
    st.markdown("AI-powered chat & deep research assistant")
    st.divider()

    if st.button("🗑️ Clear Chat History"):
        clear_messages()
        st.success("Chat history cleared")

    st.divider()
    st.markdown("🚀 Powered by Grok API")

# ================= SYSTEM PROMPT =================
SYSTEM_PROMPT = """
You are a Personal AI Knowledge Assistant.

Rules:
- Explain concepts step by step
- Use simple language
- Give examples
- Mention time and space complexity if applicable
- Be accurate and concise
- Ask ONE follow-up question at the end
"""

# ================= FILE HANDLING =================
def read_uploaded_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
        return text

    elif uploaded_file.type.startswith("image"):
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        return "The user uploaded an image. Analyze and explain it in detail."

    elif uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")

    return ""

# ================= SESSION STATE =================
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if "file_context" not in st.session_state:
    st.session_state.file_context = ""

# ================= EXTENDED FILE UPLOAD UI =================
col1, col2 = st.columns([0.35, 0.65])

with col1:
    st.markdown("### 📎 Upload File")

    uploaded_file = st.file_uploader(
        "",
        type=["pdf", "txt", "png", "jpg", "jpeg"],
        label_visibility="collapsed",
        key="file_uploader"
    )

    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.session_state.file_context = read_uploaded_file(uploaded_file)
        st.success("File uploaded successfully")

    # ❌ Cross button for images
    if (
        st.session_state.uploaded_file
        and st.session_state.uploaded_file.type.startswith("image")
    ):
        _, col_x = st.columns([0.85, 0.15])
        with col_x:
            if st.button("❌", help="Remove image"):
                st.session_state.uploaded_file = None
                st.session_state.file_context = ""
                st.session_state.file_uploader = None
                st.rerun()

with col2:
    st.markdown("### 💬 Chat with BrainWave AI")

# ================= AI FUNCTION =================
def ask_assistant(question):
    prompt = f"""
{SYSTEM_PROMPT}

Uploaded File Context:
{st.session_state.file_context}

User Question:
{question}
"""
    return llm.invoke(prompt).content

# ================= CHAT INPUT =================
with st.form("chat_form", clear_on_submit=True):
    question = st.text_input("Ask any question")
    submitted = st.form_submit_button("Submit")

    if submitted and question.strip():
        answer = ask_assistant(question)
        save_message(question, answer)

# ================= DISPLAY CHAT =================
st.markdown("---")
history = load_messages()

for user_msg, bot_msg in reversed(history):
    st.markdown(f"**🧑 You:** {user_msg}")
    st.markdown(f"**🤖 BrainWave AI:** {bot_msg}")
    st.markdown("---")

# ================= CUSTOM CSS + BRIGHT STICKER =================
st.markdown("""
<style>
section[data-testid="stFileUploader"] {
    width: 100%;
}
section[data-testid="stFileUploader"] > div {
    min-height: 220px;
    padding: 20px;
    border-radius: 14px;
}
section[data-testid="stFileUploader"] label {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 180px;
    font-size: 16px;
}

/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Bright Sidebar Sticker */
.sidebar-sticker {
    position: fixed;
    top: 50%;
    left: 10px;
    transform: translateY(-50%);
    background: linear-gradient(135deg, #00E5FF, #7C4DFF);
    color: white;
    padding: 12px 16px;
    border-radius: 12px;
    font-weight: bold;
    font-size: 14px;
    box-shadow: 0 0 18px rgba(0,229,255,0.9);
    animation: pulse 1.5s infinite;
    z-index: 9999;
}

@keyframes pulse {
    0% { box-shadow: 0 0 10px rgba(0,229,255,0.6); }
    50% { box-shadow: 0 0 28px rgba(124,77,255,1); }
    100% { box-shadow: 0 0 10px rgba(0,229,255,0.6); }
}
</style>

<div class="sidebar-sticker">
⬅️ Open Sidebar
</div>
""", unsafe_allow_html=True)
