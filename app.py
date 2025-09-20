import streamlit as st
import pdfplumber
from docx import Document
import requests

# --- Page Setup ---
st.set_page_config(page_title="Resume Scanner AI", page_icon="🧠")
st.title("🧠 Resume Scanner AI")
st.write("Paste the Job Description and upload your Resume to get AI-powered feedback.")

# --- UI Inputs ---
job_description = st.text_area("📌 Job Description", height=200)
resume_file = st.file_uploader("📎 Upload Resume (.pdf or .docx)", type=["pdf", "docx"])

# --- Resume Text Extraction ---
def extract_text(file):
    if file.name.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif file.name.endswith('.docx'):
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        return ""

# --- LLM Call to Hugging Face ---
def get_feedback_from_llm(jd, resume):
    prompt = f"""
You are a resume screening assistant. Compare the following resume and job description.

Job Description:
{jd}

Resume:
{resume}

1. Match percentage (0–100)
2. Missing keywords or skills
3. Suggestions to improve resume
4. Highlight strong alignment areas

Respond in structured markdown.
"""
    response = requests.post(
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
        headers={"Content-Type": "application/json"},
        json={"inputs": prompt}
    )

    try:
        output = response.json()
        if isinstance(output, list) and 'generated_text' in output[0]:
            return output[0]['generated_text']
        elif isinstance(output, dict) and 'generated_text' in output:
            return output['generated_text']
        else:
            return "⚠️ No response generated. Try simplifying the resume or JD."
    except Exception as e:
        return f"⚠️ Error fetching response: {e}"

# --- Analyze Button ---
if st.button("🚀 Analyze Match"):
    if not job_description or not resume_file:
        st.warning("Please provide both the Job Description and Resume.")
    else:
        with st.spinner("Analyzing resume..."):
            resume_text = extract_text(resume_file)
            feedback = get_feedback_from_llm(job_description, resume_text)
            st.markdown("### 📊 Match Analysis")
            st.markdown(feedback if feedback else "⚠️ No feedback received. Try again with a shorter resume or JD.")
