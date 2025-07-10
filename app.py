import streamlit as st
from PIL import Image
import exifread
import PyPDF2
import docx
import io

def analyze_image(file):
    img = Image.open(file)
    file.seek(0)
    tags = exifread.process_file(file, details=False)
    metadata = {tag: str(tags[tag]) for tag in tags}
    return metadata

def analyze_pdf(file):
    reader = PyPDF2.PdfReader(file)
    info = reader.metadata
    return dict(info)

def analyze_docx(file):
    doc = docx.Document(file)
    core_props = doc.core_properties
    return {
        "Author": core_props.author,
        "Title": core_props.title,
        "Subject": core_props.subject,
        "Created": core_props.created
    }

def calculate_risk_score(metadata):
    score = 0
    sensitive_keys = ['gps', 'author', 'email', 'location', 'address']
    for key in metadata:
        key_lower = key.lower()
        if any(s in key_lower for s in sensitive_keys):
            score += 25
    return min(score, 100)

def show_recommendations(score):
    if score == 0:
        return "✅ Your file is safe — no sensitive metadata found."
    elif score <= 50:
        return "⚠️ Moderate risk. Consider stripping metadata before sharing."
    else:
        return "🚨 High risk! Remove or anonymize metadata before sharing this file."

# Streamlit Web UI
st.title("🔐 Personal Metadata Risk Analyzer")

uploaded_file = st.file_uploader("Upload an image, PDF, or DOCX file", type=["jpg", "jpeg", "png", "pdf", "docx"])
if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1].lower()
    metadata = {}

    if file_type in ['jpg', 'jpeg', 'png']:
        metadata = analyze_image(uploaded_file)
    elif file_type == 'pdf':
        metadata = analyze_pdf(uploaded_file)
    elif file_type == 'docx':
        metadata = analyze_docx(uploaded_file)

    st.subheader("📋 Extracted Metadata")
    st.json(metadata)

    score = calculate_risk_score(metadata)
    st.subheader(f"🔐 Privacy Risk Score: {score} / 100")
    st.info(show_recommendations(score))
