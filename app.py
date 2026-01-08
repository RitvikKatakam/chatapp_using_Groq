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

def ask_assistant(question, docs=""):
    prompt = f"""{SYSTEM_PROMPT}

Reference Docs:
{docs}

User Question:
{question}
"""
    response = llm.invoke(prompt)
    return response.content

# ================= STREAMLIT UI =================
st.title("🤖 Grok API – ChatGroq Assistant")
st.caption("Powered by Groq")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

if "documents" not in st.session_state:
    st.session_state.documents = ""

# ================= FILE UPLOAD SECTION =================
st.subheader("📄 Add Documents / Files")

uploaded_file = st.file_uploader(
    "Upload a document (TXT, PDF, DOCX)",
    type=["txt", "pdf", "docx"]
)

if st.button("➕ Add to Knowledge Base"):
    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode("utf-8", errors="ignore")
            st.session_state.documents += "\n" + content
            st.success("✅ Document added successfully!")
        except Exception as e:
            st.error("❌ Failed to read file")
    else:
        st.warning("⚠️ Please upload a file first")

# ================= CHAT SECTION =================
with st.form("chat_form", clear_on_submit=True):
    question = st.text_input("Ask any question")
    submitted = st.form_submit_button("Submit")

    if submitted and question.strip():
        answer = ask_assistant(
            question,
            st.session_state.documents
        )
        st.session_state.history.append((question, answer))

# ================= DISPLAY CHAT HISTORY =================
st.markdown("---")
for q, a in reversed(st.session_state.history):
    st.markdown(f"**🧑 ME:** {q}")
    st.markdown(f"**🤖 Bot:** {a}")
    st.markdown("---")
