import os
import sqlite3
import streamlit as st
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from datetime import datetime
from PyPDF2 import PdfReader

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

# ================= USER NAME HANDLING =================
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if not st.session_state.user_name:
    st.markdown("## 👋 Welcome to BrainWave AI")
    st.markdown("Before we start, please tell me your name 😊")

    name = st.text_input("Your name")

    if st.button("Start Chat"):
        if name.strip():
            st.session_state.user_name = name.strip()
            st.rerun()
        else:
            st.warning("Please enter your name to continue.")

    st.stop()  # 🚨 Stop app until name is entered

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
            user_name TEXT,
            user_message TEXT,
            assistant_message TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_message(user_name, user_msg, assistant_msg):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_history VALUES (NULL, ?, ?, ?, ?)",
        (user_name, user_msg, assistant_msg, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def load_messages():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp, user_name, user_message, assistant_message
        FROM chat_history
        ORDER BY id ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def clear_messages():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()

def export_chat_history():
    rows = load_messages()
    export_text = ""
    for ts, uname, user, assistant in rows:
        export_text += (
            f"[{ts}]\n"
            f"{uname}: {user}\n"
            f"BrainWave AI: {assistant}\n\n"
        )
    return export_text

init_db()

# ================= INITIALIZE LLM =================
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

# ================= HEADER =================
st.markdown(
    f"<h1 style='text-align:center;'>🧠 BrainWave AI</h1>",
    unsafe_allow_html=True
)
st.caption(f"Welcome, **{st.session_state.user_name}** 👋 | Powered by Groq")

# ================= SETTINGS PANEL =================
with st.expander("⚙️ Settings & Controls", expanded=False):

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Clear Chat History"):
            clear_messages()
            st.success("Chat history cleared")

    with col2:
        chat_export = export_chat_history()
        if chat_export.strip():
            st.download_button(
                label="⬇️ Download Chat History",
                data=chat_export,
                file_name="brainwave_ai_chat_history.txt",
                mime="text/plain"
            )

# ================= SYSTEM PROMPT =================
SYSTEM_PROMPT = f"""
You are a Personal AI Knowledge Assistant.

Identity rules:
- If the user asks about your name or identity, respond exactly with:
  "I am Groq AI."

Conversation rules:
- The user's name is {st.session_state.user_name}
- Be friendly and address the user by name when appropriate
- Explain concepts step by step
- Use simple language
- Give examples
- Be accurate and concise
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

    elif uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")

    return ""

# ================= SESSION STATE =================
if "file_context" not in st.session_state:
    st.session_state.file_context = ""

# ================= FILE UPLOAD =================
col1, col2 = st.columns([0.35, 0.65])

with col1:
    st.markdown("### 📎 Upload File")

    uploaded_file = st.file_uploader(
        "",
        type=["pdf", "txt"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        st.session_state.file_context = read_uploaded_file(uploaded_file)
        st.success("File uploaded successfully")

with col2:
    st.markdown("### 💬 Chat with BrainWave AI")

# ================= AI FUNCTION =================
def ask_assistant(question):
    identity_triggers = ["what is your name", "who are you"]

    if any(t in question.lower() for t in identity_triggers):
        return "I am Groq AI."

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
    question = st.text_input(f"{st.session_state.user_name}, ask any question")
    submitted = st.form_submit_button("Submit")

    if submitted and question.strip():
        answer = ask_assistant(question)
        save_message(st.session_state.user_name, question, answer)

# ================= DISPLAY CHAT =================
st.markdown("---")
history = load_messages()

for ts, uname, user_msg, bot_msg in reversed(history):
    st.markdown(f"**🧑 {uname}:** {user_msg}")
    st.markdown(f"**🤖 BrainWave AI:** {bot_msg}")
    st.caption(f"🕒 {ts}")
    st.markdown("---")

# ================= FOOTER =================
st.markdown("""
<style>
.app-footer {
    position: fixed;
    bottom: 10px;
    left: 0;
    width: 100%;
    text-align: center;
    color: #9aa0a6;
    font-size: 14px;
}
</style>

<div class="app-footer">
🤖 <b>BrainWave AI</b> — Created by an AI Student
</div>
""", unsafe_allow_html=True)
