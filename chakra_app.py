import streamlit as st
import uuid
import pandas as pd
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# ReportLab imports for PDF generation
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib import colors

# =====================================================
# 🛠️ CONFIGURATION - CHANGE YOUR DETAILS HERE
# =====================================================
# These keys must match exactly what you type in Streamlit Secrets
try:
    SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]
    FROM_EMAIL       = st.secrets["FROM_EMAIL"]
    HEALER_EMAIL     = st.secrets["HEALER_EMAIL"]
except Exception:
    st.error("❌ Secrets Missing! Please add SENDGRID_API_KEY, FROM_EMAIL, and HEALER_EMAIL to Streamlit Secrets.")
    st.stop()

HEALER_NAME = "Free Spirit9191"
# =====================================================

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="Chakra Healing Web App",
    page_icon="🌀",
    layout="centered"
)

# ----------------------------------
# EMAIL FUNCTION (SENDGRID)
# ----------------------------------
def send_email_via_sendgrid(receiver_email, subject, body):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=receiver_email,
        subject=subject,
        plain_text_content=body
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        return True
    except Exception as e:
        st.error(f"❌ Email sending failed. Check your API Key and Verified Sender status. Error: {e}")
        return False

# ----------------------------------
# FILE & DATA CONFIG
# ----------------------------------
DATA_FILE = "users.csv"
REPORT_FOLDER = "reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)

def load_users():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["user_id", "name", "email", "phone", "service_count"])

def save_users(df):
    df.to_csv(DATA_FILE, index=False)

users_df = load_users()

# ----------------------------------
# UI - REGISTRATION
# ----------------------------------
st.title("🌀 Chakra Healing Web App")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.header("Energy Receiver Registration")
name = st.text_input("Full Name *")
email = st.text_input("Email Address *")
phone = st.text_input("Phone Number *")

if st.button("Proceed"):
    if not name or not email or not phone:
        st.error("All fields are required.")
    else:
        existing = users_df[(users_df["email"] == email) | (users_df["phone"] == phone)]

        if not existing.empty:
            user = existing.iloc[0]
            service_count = int(user["service_count"]) + 1
            user_id = user["user_id"]
            users_df.loc[existing.index, "service_count"] = service_count
        else:
            user_id = str(uuid.uuid4())[:8].upper()
            service_count = 1
            users_df.loc[len(users_df)] = [user_id, name, email, phone, service_count]

        save_users(users_df)

        password = name[0].upper() + phone[-3:] + "FS9191ER" + str(service_count)
        
        subject = "🌿 Your Chakra Healing Access Details"
        body = f"Hello {name},\n\nYour access password is: {password}\nUser ID: {user_id}\nSession: {service_count}\n\nWarm regards,\n{HEALER_NAME}"

        if send_email_via_sendgrid(email, subject, body):
            st.success("✅ Password has been sent to your email.")
            st.session_state.generated_password = password
            st.session_state.user_name = name
            st.session_state.user_id = user_id
            st.session_state.service_count = service_count

# ----------------------------------
# UI - PASSWORD CHECK & ASSESSMENT
# ----------------------------------
if "generated_password" in st.session_state and not st.session_state.authenticated:
    st.divider()
    st.header("🔐 Enter Access Password")
    entered = st.text_input("Password", type="password")

    if st.button("Unlock Chakra Assessment"):
        if entered == st.session_state.generated_password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")

if st.session_state.authenticated:
    st.header("🧘 Chakra Energy Assessment")

    chakras = {
        "Muladhara (Root)": ["I feel physically safe.", "I maintain routines.", "Financial stress is low.", "I feel comfortable in my body.", "I trust life."],
        "Svadhisthana (Sacral)": ["Emotions flow freely.", "I experience joy.", "I feel connected.", "I express creativity.", "I am comfortable with intimacy."],
        "Manipura (Solar Plexus)": ["I take action confidently.", "I assert needs clearly.", "I complete tasks.", "I trust my decisions.", "I feel in control."],
        "Anahata (Heart)": ["I give and receive love.", "I forgive easily.", "I am balanced.", "Healthy boundaries.", "Compassion without exhaustion."],
        "Vishuddha (Throat)": ["I express clearly.", "I speak my truth.", "I communicate honestly.", "Words align with actions.", "I feel heard."],
        "Ajna (Third Eye)": ["I trust intuition.", "I observe calmly.", "I see patterns.", "Logic/Intuition balance.", "Mental clarity."],
        "Sahasrara (Crown)": ["Spiritually connected.", "I feel guided.", "Trust higher intelligence.", "Life has meaning.", "Integrated spirituality."]
    }

    results = {}
    for chakra, questions in chakras.items():
        st.subheader(chakra)
        scores = [st.slider(q, 0, 4, 2, key=f"{chakra}_{i}") for i, q in enumerate(questions)]
        results[chakra] = round(sum(scores) / len(scores), 2)

    def generate_pdf():
        file_path = f"{REPORT_FOLDER}/Chakra_Report_{st.session_state.user_id}.pdf"
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = [Paragraph("Chakra Energy Assessment Report", styles["Title"]), Spacer(1, 12)]
        elements.append(Paragraph(f"Receiver: {st.session_state.user_name} (ID: {st.session_state.user_id})", styles["Normal"]))
        elements.append(Paragraph(f"Date: {datetime.now().strftime('%d-%m-%Y')}", styles["Normal"]))
        elements.append(Spacer(1, 12))
        
        table_data = [["Chakra", "Score"]] + [[c, v] for c, v in results.items()]
        elements.append(Table(table_data))
        
        drawing = Drawing(400, 200)
        chart = VerticalBarChart()
        chart.data = [[results[c] for c in results]]
        chart.categoryAxis.categoryNames = list(results.keys())
        chart.valueAxis.valueMax = 4
        chart.bars[0].fillColor = colors.teal
        drawing.add(chart)
        elements.append(drawing)
        doc.build(elements)
        return file_path

    if st.button("📄 Generate & Notify Healer"):
        pdf_path = generate_pdf()
        h_subject = f"New Chakra Report: {st.session_state.user_name}"
        h_body = f"User {st.session_state.user_name} finished session {st.session_state.service_count}. View PDF in the reports folder."
        
        if send_email_via_sendgrid(HEALER_EMAIL, h_subject, h_body):
            st.success("✅ Healer notified!")
            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF", f, file_name=os.path.basename(pdf_path))
