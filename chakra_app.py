import streamlit as st
import uuid
import pandas as pd
import os
from datetime import datetime
import yagmail

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib import colors

# =========================
# 🔐 ENVIRONMENT VARIABLES
# =========================

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

HEALER_NAME = "Free Spirit9191"
HEALER_EMAIL = GMAIL_USER  # healer receives reports

if not GMAIL_USER or not GMAIL_APP_PASSWORD:
    st.error(
        "❌ Email credentials missing.\n\n"
        "Please set GMAIL_USER and GMAIL_APP_PASSWORD in Streamlit Secrets."
    )
    st.stop()

# =========================
# 📁 FILE CONFIG
# =========================

DATA_FILE = "users.csv"
REPORT_FOLDER = "reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)

# =========================
# 📄 USER DATA HANDLING
# =========================

def load_users():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(
        columns=["user_id", "name", "email", "phone", "service_count"]
    )

def save_users(df):
    df.to_csv(DATA_FILE, index=False)

users_df = load_users()

# =========================
# ✉️ EMAIL FUNCTIONS
# =========================

def send_password_email(receiver_email, receiver_name, password, service_count, user_id):
    yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASSWORD)

    subject = "Chakra Assessment Access Credentials"

    body = f"""
Hello {receiver_name},

Your access password for the Chakra Healing Web App is:

{password}

Session Number: {service_count}
User ID: {user_id}

Please keep this information secure.

With gratitude,
{HEALER_NAME}
"""

    yag.send(to=receiver_email, subject=subject, contents=body)

def send_report_to_healer(pdf_path, receiver_name):
    yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASSWORD)
    yag.send(
        to=HEALER_EMAIL,
        subject="New Chakra Assessment Report",
        contents=f"A new chakra report has been generated for {receiver_name}.",
        attachments=pdf_path
    )

# =========================
# 🌀 STREAMLIT UI CONFIG
# =========================

st.set_page_config(
    page_title="Chakra Healing Web App",
    layout="centered"
)

st.title("🌀 Chakra Healing Web App")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# =========================
# 🧍 USER REGISTRATION
# =========================

st.header("🌿 Energy Receiver Registration")

name = st.text_input("Full Name *")
email = st.text_input("Email Address *")
phone = st.text_input("Phone Number *")

if st.button("Proceed"):
    if not name or not email or not phone:
        st.error("All fields are required.")
    else:
        existing = users_df[
            (users_df["email"] == email) | (users_df["phone"] == phone)
        ]

        if not existing.empty:
            user = existing.iloc[0]
            service_count = int(user["service_count"]) + 1
            user_id = user["user_id"]
            users_df.loc[existing.index, "service_count"] = service_count
        else:
            user_id = str(uuid.uuid4())[:8].upper()
            service_count = 1
            users_df.loc[len(users_df)] = [
                user_id, name, email, phone, service_count
            ]

        save_users(users_df)

        password = (
            name[0].upper()
            + phone[-3:]
            + "FS9191ER"
            + str(service_count)
        )

        send_password_email(email, name, password, service_count, user_id)

        st.success("✅ Password sent to your email.")

        st.session_state.generated_password = password
        st.session_state.user_name = name
        st.session_state.user_id = user_id
        st.session_state.service_count = service_count

# =========================
# 🔐 PASSWORD VERIFICATION
# =========================

if "generated_password" in st.session_state:
    st.header("🔐 Enter Access Password")
    entered = st.text_input("Password", type="password")

    if st.button("Unlock Chakra Assessment"):
        if entered == st.session_state.generated_password:
            st.session_state.authenticated = True
        else:
            st.error("Incorrect password.")

# =========================
# 🧘 CHAKRA ASSESSMENT
# =========================

if st.session_state.authenticated:
    st.header("🧘 Chakra Energy Assessment")

    chakras = {
        "Muladhara (Root)": ["I feel physically safe and supported in my daily life.", "I maintain basic routines consistently.", "Financial stress rarely affects me.", "I feel comfortable in my body.", "I trust life to meet my basic needs."],
        "Svadhisthana (Sacral)": ["I allow emotions to flow freely.", "I experience joy without guilt.", "I feel emotionally connected in relationships.", "I express creativity freely.", "I feel comfortable with intimacy."],
        "Manipura (Solar Plexus)": ["I take action confidently.", "I assert my needs clearly.", "I complete what I start.", "I trust my decisions.", "I feel in control of my life."],
        "Anahata (Heart)": ["I give and receive love easily.", "I forgive without suppressing emotions.", "I feel emotionally open and balanced.", "I maintain healthy boundaries.", "I feel compassion without exhaustion."],
        "Vishuddha (Throat)": ["I express myself clearly.", "I speak my truth comfortably.", "I communicate honestly.", "My words align with actions.", "I feel heard."],
        "Ajna (Third Eye)": ["I trust my intuition.", "I observe thoughts calmly.", "I see patterns clearly.", "I balance logic and intuition.", "I feel mentally clear."],
        "Sahasrara (Crown)": ["I feel spiritually connected", "I feel guided in life.", "I trust higher intelligence.", "I feel life has meaning.", "I integrate spirituality daily."]
    }

    results = {}

    for chakra, questions in chakras.items():
        st.subheader(chakra)
        scores = [st.slider(q, 0, 4, 2) for q in questions]
        results[chakra] = round(sum(scores) / len(scores), 2)

    # =========================
    # 📄 PDF REPORT
    # =========================

    def generate_pdf():
        file_path = f"{REPORT_FOLDER}/Chakra_Report_{st.session_state.user_id}.pdf"
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Chakra Energy Assessment Report", styles["Title"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Energy Receiver: {st.session_state.user_name}", styles["Normal"]))
        elements.append(Paragraph(f"User ID: {st.session_state.user_id}", styles["Normal"]))
        elements.append(Paragraph(f"Session: {st.session_state.service_count}", styles["Normal"]))
        elements.append(Paragraph(f"Date: {datetime.now().strftime('%d-%m-%Y')}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        table_data = [["Chakra", "Score"]] + [[c, v] for c, v in results.items()]
        elements.append(Table(table_data))
        elements.append(Spacer(1, 20))

        drawing = Drawing(420, 250)
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 40
        chart.height = 180
        chart.width = 320
        chart.data = [[results[c] for c in results]]
        chart.categoryAxis.categoryNames = list(results.keys())
        chart.categoryAxis.labels.angle = 45
        chart.categoryAxis.labels.dy = -15
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 4
        chart.valueAxis.valueStep = 1
        chart.bars[0].fillColor = colors.teal

        drawing.add(chart)
        elements.append(drawing)

        doc.build(elements)
        return file_path

    if st.button("📄 Generate & Send Report"):
        pdf = generate_pdf()
        send_report_to_healer(pdf, st.session_state.user_name)

        st.success("✅ Report generated and emailed to healer.")
        st.download_button(
            "⬇ Download PDF",
            open(pdf, "rb"),
            file_name=os.path.basename(pdf)
        )
