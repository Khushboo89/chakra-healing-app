
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

# ================= CONFIG =================
try:
    SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]
    FROM_EMAIL = st.secrets["FROM_EMAIL"]
    HEALER_EMAIL = st.secrets["HEALER_EMAIL"]
except Exception:
    st.error("Missing Streamlit Secrets.")
    st.stop()

HEALER_NAME = "Free Spirit9191"

st.set_page_config(page_title="Chakra Healing Web App", page_icon="🌀")

def send_email(receiver_email, subject, body):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=receiver_email,
        subject=subject,
        plain_text_content=body,
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code == 202
    except Exception:
        return False

DATA_FILE = "users.csv"
REPORT_FOLDER = "reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)

def load_users():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["user_id","name","email","phone","service_count"])

def save_users(df):
    df.to_csv(DATA_FILE, index=False)

users_df = load_users()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.title("🌀 Chakra Healing Web App")
st.header("Energy Receiver Registration")

name = st.text_input("Full Name *")
email = st.text_input("Email *")
phone = st.text_input("Phone *")

if st.button("Proceed"):
    if not name or not email or not phone:
        st.error("All fields required.")
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
            users_df.loc[len(users_df)] = [user_id,name,email,phone,service_count]

        save_users(users_df)

        password = name[0].upper() + phone[-3:] + "FS9191ER" + str(service_count)

        subject = "Your Chakra Healing Access"
        body = f"""Hello {name},

User ID: {user_id}
Password: {password}
Session: {service_count}

{HEALER_NAME}
"""

        if send_email(email, subject, body):
            st.success("Password sent to your email.")
            st.session_state.generated_password = password
            st.session_state.user_name = name
            st.session_state.user_id = user_id
            st.session_state.service_count = service_count
        else:
            st.error("Email failed. Check SendGrid setup.")

if "generated_password" in st.session_state and not st.session_state.authenticated:
    st.header("Enter Password")
    entered = st.text_input("Password", type="password")
    if st.button("Unlock"):
        if entered == st.session_state.generated_password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")

if st.session_state.authenticated:
    st.header("Chakra Assessment")

    chakras = {
        "Root": ["I feel safe.","I maintain routines.","Financial stress low."],
        "Heart": ["I give love.","I forgive.","Healthy boundaries."],
        "Crown": ["I feel guided.","Life has meaning.","Spiritual trust."]
    }

    results = {}
    for chakra, questions in chakras.items():
        st.subheader(chakra)
        scores = [st.slider(q,0,4,2,key=f"{chakra}_{i}") for i,q in enumerate(questions)]
        results[chakra] = round(sum(scores)/len(scores),2)

    def generate_pdf():
        file_path = f"{REPORT_FOLDER}/Report_{st.session_state.user_id}.pdf"
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Chakra Report", styles["Title"]))
        elements.append(Spacer(1,12))

        table_data = [["Chakra","Score"]] + [[c,v] for c,v in results.items()]
        elements.append(Table(table_data))

        drawing = Drawing(400,200)
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
        return file_path

    if st.button("Generate Report"):
        pdf_path = generate_pdf()

        subject = f"New Chakra Report: {st.session_state.user_name}"
        body = f"User {st.session_state.user_name} completed session."

        send_email(HEALER_EMAIL, subject, body)

        with open(pdf_path, "rb") as f:
            st.download_button("Download PDF", f, file_name=os.path.basename(pdf_path))
