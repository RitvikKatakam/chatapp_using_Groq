import os
import sqlite3
import streamlit as st
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from datetime import datetime
from PyPDF2 import PdfReader
from PIL import Image

# ================= PAGE CONFIG (FIRST STREAMLIT CALL) =================
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
    st.markdown("AI-powered chat & deep research assistant")
    st.divider()

    if st.button("🗑️ Clear Chat History"):
        clear_messages()
        st.success("Chat history cleared")

    if st.button("📎 Clear Uploaded File"):
        st.session_state.file_context = ""
        st.success("Uploaded file cleared")

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
if "file_context" not in st.session_state:
    st.session_state.file_context = ""

# ================= + FILE UPLOAD UI =================
col1, col2 = st.columns([0.08, 0.92])

with col1:
    uploaded_file = st.file_uploader(
        "➕",
        label_visibility="collapsed",
        type=["pdf", "txt", "png", "jpg", "jpeg"]
    )

    if uploaded_file:
        st.session_state.file_context = read_uploaded_file(uploaded_file)
        st.success("File uploaded successfully")

with col2:
    st.markdown("### Chat with BrainWave AI")

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

# ================= HIDE STREAMLIT UI =================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
