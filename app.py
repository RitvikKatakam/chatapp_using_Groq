import os
import sqlite3
import json
import streamlit as st
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from datetime import datetime

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
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
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
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_message, assistant_message, timestamp) VALUES (?, ?, ?)",
        (user_msg, assistant_msg, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def load_messages():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_message, assistant_message FROM chat_history ORDER BY id ASC"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def clear_messages():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()

# Initialize DB
init_db()

# ================= INITIALIZE LLM =================
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

# ================= BRAND HEADER =================
st.markdown(
    "<h1 style='text-align: center;'>🧠 BrainWave AI</h1>",
    unsafe_allow_html=True
)
st.caption("Think Deeper • Ask Smarter • Powered by Grok")

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("## 🧠 BrainWave AI")
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

def ask_assistant(question):
    prompt = f"{SYSTEM_PROMPT}\n\nUser Question:\n{question}"
    response = llm.invoke(prompt)
    return response.content

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
