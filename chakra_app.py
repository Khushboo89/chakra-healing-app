import streamlit as st
import uuid
import pandas as pd
import os
from datetime import datetime

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib import colors

# ==========================
# CONFIG
# ==========================
st.set_page_config(page_title="Chakra Healing App", page_icon="🌀")

try:
    SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]
    FROM_EMAIL = st.secrets["FROM_EMAIL"]
    HEALER_EMAIL = st.secrets["HEALER_EMAIL"]
except Exception:
    st.error("❌ Missing Streamlit Secrets. Please configure SENDGRID_API_KEY, FROM_EMAIL, HEALER_EMAIL.")
    st.stop()

HEALER_NAME = "Free Spirit9191"
DATA_FILE = "users.csv"
REPORT_FOLDER = "reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)

# ==========================
# EMAIL FUNCTION (ROBUST)
# ==========================
def send_email(receiver_email, subject, body):
    try:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=receiver_email,
            subject=subject,
            plain_text_content=body,
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        if response.status_code == 202:
            return True
        else:
            st.error(f"SendGrid Error: {response.status_code}")
            st.code(response.body)
            return False

    except Exception as e:
        st.error(f"SendGrid Exception: {e}")
        return False


# ==========================
# USER STORAGE
# ==========================
def load_users():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["user_id", "name", "email", "phone", "service_count"])

def save_users(df):
    df.to_csv(DATA_FILE, index=False)

users_df = load_users()

# ==========================
# SESSION INIT
# ==========================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ==========================
# APP UI
# ==========================
st.title("🌀 Chakra Healing Energy Portal")

# ==========================
# REGISTRATION
# ==========================
if not st.session_state.authenticated:

    st.header("Energy Receiver Registration")

    name = st.text_input("Full Name *")
    email = st.text_input("Email *")
    phone = st.text_input("Phone *")

    if st.button("Generate Access"):

        if not name or not email or not phone:
            st.error("⚠ All fields required.")
            st.stop()

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

        subject = "Your Chakra Healing Access Credentials"
        body = f"""
Hello {name},

Your Chakra Healing Access Details:

User ID: {user_id}
Session Number: {service_count}
Password: {password}

With Light & Energy,
{HEALER_NAME}
"""

        success = send_email(email, subject, body)

        if success:
            st.success("✅ Password sent to your email.")
            st.session_state.generated_password = password
        else:
            st.error("❌ Email failed. Please check SendGrid configuration.")
            st.stop()

    if "generated_password" in st.session_state:
        st.subheader("Enter Password")
        entered = st.text_input("Password", type="password")

        if st.button("Unlock Assessment"):
            if entered == st.session_state.generated_password:
                st.session_state.authenticated = True
                st.success("Access Granted")
                st.rerun()
            else:
                st.error("Incorrect password.")


# ==========================
# CHAKRA ASSESSMENT
# ==========================
if st.session_state.authenticated:

    st.header("Chakra Assessment")

    chakras = {
        "Root": ["I feel safe.", "I feel grounded.", "Financial stress is low."],
        "Heart": ["I give love freely.", "I forgive easily.", "Healthy relationships."],
        "Crown": ["I feel spiritually guided.", "Life has meaning.", "Trust divine flow."]
    }

    results = {}

    for chakra, questions in chakras.items():
        st.subheader(chakra)
        scores = []
        for q in questions:
            score = st.slider(q, 0, 4, 2)
            scores.append(score)
        results[chakra] = round(sum(scores) / len(scores), 2)

    # ==========================
    # PDF GENERATION
    # ==========================
    def generate_pdf():
        filename = f"{REPORT_FOLDER}/Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Chakra Energy Report", styles["Title"]))
        elements.append(Spacer(1, 20))

        table_data = [["Chakra", "Score"]]
        for chakra, score in results.items():
            table_data.append([chakra, score])

        elements.append(Table(table_data))
        elements.append(Spacer(1, 30))

        drawing = Drawing(400, 200)
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.height = 125
        chart.width = 300
        chart.data = [[v for v in results.values()]]
        chart.categoryAxis.categoryNames = list(results.keys())
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 4
        chart.bars[0].fillColor = colors.teal

        drawing.add(chart)
        elements.append(drawing)

        doc.build(elements)
        return filename

    if st.button("Generate Energy Report"):
        pdf_path = generate_pdf()

        healer_subject = "New Chakra Assessment Completed"
        healer_body = "A new chakra session has been completed."

        send_email(HEALER_EMAIL, healer_subject, healer_body)

        with open(pdf_path, "rb") as f:
            st.download_button(
                "Download Your Chakra Report",
                f,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf"
            )

        st.success("Report Generated Successfully!")
