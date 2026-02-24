import streamlit as st
import uuid
import os
import base64
from datetime import datetime

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.units import inch

st.set_page_config(page_title="Chakra Healing Portal", page_icon="🌀")

def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

SENDGRID_API_KEY = get_secret("SENDGRID_API_KEY")
FROM_EMAIL = get_secret("FROM_EMAIL")
HEALER_EMAIL = get_secret("HEALER_EMAIL")

HEALER_NAME = "Free Spirit9191"
HEALER_CONTACT = "9960699113"

REPORT_FOLDER = "reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)

def send_email_with_attachment(to_emails, subject, body, file_path):
    if not SENDGRID_API_KEY:
        st.warning("Email not configured.")
        return False
    try:
        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        attachment = Attachment(
            FileContent(encoded),
            FileName(os.path.basename(file_path)),
            FileType("application/pdf"),
            Disposition("attachment"),
        )

        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_emails,
            subject=subject,
            plain_text_content=body,
        )

        message.attachment = attachment

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

def chakra_status(score):
    if score <= 1:
        return "Blocked"
    elif 1 < score < 2:
        return "Underactive"
    elif 2 <= score <= 3:
        return "Balanced"
    else:
        return "Overactive"

chakra_focus = {
    "Muladhara (Root)": "Grounding, routine, financial stability.",
    "Svadhisthana (Sacral)": "Emotional expression, creativity.",
    "Manipura (Solar Plexus)": "Confidence, boundaries, action.",
    "Anahata (Heart)": "Forgiveness, compassion.",
    "Vishuddha (Throat)": "Truthful expression, communication.",
    "Ajna (Third Eye)": "Clarity, awareness.",
    "Sahasrara (Crown)": "Spiritual integration."
}

chakra_colors = {
    "Muladhara (Root)": colors.red,
    "Svadhisthana (Sacral)": colors.orange,
    "Manipura (Solar Plexus)": colors.yellow,
    "Anahata (Heart)": colors.green,
    "Vishuddha (Throat)": colors.blue,
    "Ajna (Third Eye)": colors.indigo,
    "Sahasrara (Crown)": colors.violet
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.title("🌀 Chakra Healing Energy Portal")

if not st.session_state.authenticated:
    st.header("Energy Receiver Registration")
    name = st.text_input("Full Name")
    age = st.number_input("Age", 1, 100)
    location = st.text_input("Location")
    email = st.text_input("Email")
    phone = st.text_input("Phone")

    if st.button("Generate Access"):
        if not name or not email or not phone:
            st.error("All fields required.")
        else:
            password = name[0].upper() + phone[-3:] + "FS9191"
            st.session_state.password = password
            st.success("Password generated.")

    if "password" in st.session_state:
        entered = st.text_input("Enter Password", type="password")
        if st.button("Unlock Assessment"):
            if entered == st.session_state.password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")

if st.session_state.authenticated:
    st.header("Chakra Assessment")
    results = {}
    for chakra in chakra_focus.keys():
        score = st.slider(chakra, 0.0, 4.0, 2.0, 0.1)
        results[chakra] = round(score, 2)

    def generate_pdf():
        client_id = uuid.uuid4().hex[:8].upper()
        filename = f"{REPORT_FOLDER}/Chakra_Report_{client_id}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        if os.path.exists("logo.png"):
            logo = Image("logo.png", width=2.5*inch, height=2.5*inch)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 20))

        elements.append(Paragraph("<b>Chakra Assessment Report</b>", styles["Title"]))
        elements.append(Spacer(1, 20))

        elements.append(Paragraph(f"Name: {name}", styles["Normal"]))
        elements.append(Paragraph(f"Age: {age}", styles["Normal"]))
        elements.append(Paragraph(f"Location: {location}", styles["Normal"]))
        elements.append(Spacer(1, 20))

        table_data = [["Chakra", "Score", "Status", "Focus"]]
        for chakra, score in results.items():
            table_data.append([chakra, score, chakra_status(score), chakra_focus[chakra]])

        table = Table(table_data, colWidths=[120, 50, 80, 180])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.black),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ]))

        elements.append(table)
        doc.build(elements)
        return filename

    if st.button("Generate Premium Energy Report"):
        pdf_path = generate_pdf()
        with open(pdf_path, "rb") as f:
            st.download_button("Download Report", f, file_name=os.path.basename(pdf_path))
        st.success("Report Generated Successfully 🌿")
