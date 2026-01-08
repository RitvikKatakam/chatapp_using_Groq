import os
import json
import streamlit as st
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# ================= PAGE CONFIG (FIRST STREAMLIT CALL) =================
st.set_page_config(
    page_title="BrainWave AI",
    page_icon="🧠",
    layout="wide"
)

# ================= LOAD ENV =================
load_dotenv()

# Safety check for API key
if not os.getenv("GROQ_API_KEY"):
    st.error("❌ GROQ_API_KEY not found. Set it in Streamlit Secrets or .env")
    st.stop()

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

    if st.button("🗑️ Clear Chat"):
        st.session_state.history = []
        st.success("Chat cleared")

    if "history" in st.session_state and st.session_state.history:
        st.download_button(
            label="⬇️ Download Chat History",
            data=json.dumps(st.session_state.history, indent=2),
            file_name="brainwave_ai_chat_history.json",
            mime="application/json"
        )

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

# ================= SESSION STATE =================
if "history" not in st.session_state:
    st.session_state.history = []

# ================= CHAT INPUT =================
with st.form("chat_form", clear_on_submit=True):
    question = st.text_input("Ask any question")
    submitted = st.form_submit_button("Submit")

    if submitted and question.strip():
        answer = ask_assistant(question)
        st.session_state.history.append({
            "user": question,
            "assistant": answer
        })

# ================= DISPLAY CHAT =================
st.markdown("---")
for chat in reversed(st.session_state.history):
    st.markdown(f"**🧑 You:** {chat['user']}")
    st.markdown(f"**🤖 BrainWave AI:** {chat['assistant']}")
    st.markdown("---")

# ================= HIDE STREAMLIT UI =================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
