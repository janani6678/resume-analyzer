import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import base64
import os
from bs4 import BeautifulSoup

# ========== 🔐 API Configuration ==========
genai.configure(api_key="AIzaSyBpyN4E2UYQc2O6R1mrG1batGhgB3Wo2aU")  # Replace with your Gemini API key

# ========== 🎨 Background Styling ==========
def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .main > div {{
            background-color: rgba(255, 255, 255, 0.85);
            padding: 30px;
            border-radius: 12px;
        }}
        h1, h3, label, p, div {{
            color: #000000 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

set_background("background.jpg")  # Ensure this file is present in the same directory

# ========== 📄 PDF Text Extraction ==========
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

# ========== 🤖 Gemini Resume Enhancement ==========
def generate_resume_with_gemini(resume_text, job_description):
    prompt = f"""
    You are an expert resume writer.
    Rewrite the following resume to match the job description.
    - Remove all markdown formatting (no **, no headers)
    - Keep it simple, readable, and ATS-friendly
    - Align experience and skills with job requirements

    Resume:
    {resume_text}

    Job Description:
    {job_description}
    """
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.replace("**", "").strip()

# ========== 🧼 Clean Gemini HTML Output ==========
def clean_resume_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup.find_all(style=True):
        styles = tag['style'].split(';')
        new_styles = [s for s in styles if 'color' not in s.lower()]
        tag['style'] = ';'.join(new_styles)
    return str(soup)

# ========== 💾 Save PDF from Text ==========
def save_text_as_pdf(text, filename="Optimized_Resume.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 50

    for line in text.split("\n"):
        if y < 50:
            c.showPage()
            y = height - 50
        c.setFont("Helvetica", 11)
        c.drawString(50, y, line)
        y -= 15

    c.save()
    return filename

# ========== 🚀 Streamlit UI ==========
st.markdown("<h1 style='text-align:center;'>📊 Resume Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Upload your resume and job description to get an optimized version</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📄 Upload Your Resume (PDF only)", type=["pdf"])
if uploaded_file:
    st.success("✅ Resume uploaded successfully!")

job_description = st.text_area("📝 Paste the Job Description below:")

if st.button("✨ Generate Optimized Resume"):
    if not uploaded_file or not job_description.strip():
        st.error("❌ Please upload a resume and enter a job description.")
    else:
        with st.spinner("Processing with Gemini..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            improved_resume = generate_resume_with_gemini(resume_text, job_description)

            # Clean output and display
            cleaned_html = clean_resume_html(improved_resume)
            st.markdown("---")
            st.markdown("### ✅ Optimized Resume")
            st.markdown(
                f"""
                <div style='background-color:#ffffff; color:#000000; padding:20px; border-radius:10px;'>
                    {cleaned_html}
                </div>
                """,
                unsafe_allow_html=True
            )

            # Offer PDF download
            pdf_file_path = save_text_as_pdf(improved_resume)
            with open(pdf_file_path, "rb") as pdf_file:
                b64 = base64.b64encode(pdf_file.read()).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="Optimized_Resume.pdf"><button style="margin-top:20px;">📥 Download Optimized Resume as PDF</button></a>'
                st.markdown(href, unsafe_allow_html=True)
