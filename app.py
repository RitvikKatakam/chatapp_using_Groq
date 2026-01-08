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
    cur.execute("""
        SELECT timestamp, user_message, assistant_message
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
    for ts, user, assistant in rows:
        export_text += (
            f"[{ts}]\n"
            f"You: {user}\n"
            f"BrainWave AI: {assistant}\n\n"
        )
    return export_text

init_db()

# ================= INITIALIZE LLM =================
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

# ================= BRAND HEADER =================
st.markdown(
    "<h1 style='text-align:center;'>🧠 BrainWave AI</h1>",
    unsafe_allow_html=True
)
st.caption("Think Deeper • Ask Smarter • Powered by Grok")

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

# ================= FILE HANDLING (PDF & TXT ONLY) =================
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

# ================= FILE UPLOAD + CHAT =================
col1, col2 = st.columns([0.35, 0.65])

with col1:
    st.markdown("### 📎 Upload File")

    uploaded_file = st.file_uploader(
        "",
        type=["pdf", "txt"],
        label_visibility="collapsed",
        key="file_uploader"
    )

    if uploaded_file:
        st.session_state.file_context = read_uploaded_file(uploaded_file)
        st.success("File uploaded successfully")

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

for ts, user_msg, bot_msg in reversed(history):
    st.markdown(f"**🧑 You:** {user_msg}")
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
    z-index: 999;
}
</style>

<div class="app-footer">
🤖 <b>BrainWave AI</b> — Created by an AI Student
</div>
""", unsafe_allow_html=True)

# ================= HIDE STREAMLIT UI =================
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
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
