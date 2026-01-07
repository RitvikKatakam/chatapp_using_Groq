import os
import streamlit as st
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# ================= LOAD ENV =================
load_dotenv()

# Safety check
if not os.getenv("GROQ_API_KEY"):
    st.error("❌ GROQ_API_KEY not found. Set it in .env or Streamlit Secrets.")
    st.stop()

# ================= INITIALIZE LLM =================
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

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

# ================= STREAMLIT UI =================
st.title("🤖 Grok API – ChatGroq Assistant")
st.caption("Powered by Groq")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

# Input form
with st.form("chat_form", clear_on_submit=True):
    question = st.text_input("Ask any question")
    submitted = st.form_submit_button("Submit")

    if submitted and question.strip():
        answer = ask_assistant(question)
        st.session_state.history.append((question, answer))

# Display chat history
st.markdown("---")
for q, a in reversed(st.session_state.history):
    st.markdown(f"**🧑 You:** {q}")
    st.markdown(f"**🤖 Assistant:** {a}")
    st.markdown("---")
