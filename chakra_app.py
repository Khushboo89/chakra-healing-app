import streamlit as st
import uuid
import os
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Chakra Healing Portal", page_icon="🌀")

REPORT_FOLDER = "reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)

# =====================================================
# SESSION STATE
# =====================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# =====================================================
# CHAKRA QUESTIONS
# =====================================================
chakras = {
    "Muladhara (Root)": [
        "I feel physically safe and supported in my daily life.",
        "I maintain basic routines consistently.",
        "Financial stress rarely affects me.",
        "I feel comfortable in my body.",
        "I trust life to meet my basic needs."
    ],
    "Svadhisthana (Sacral)": [
        "I allow emotions to flow freely.",
        "I experience joy without guilt.",
        "I feel emotionally connected in relationships.",
        "I express creativity freely.",
        "I feel comfortable with intimacy."
    ],
    "Manipura (Solar Plexus)": [
        "I take action confidently.",
        "I assert my needs clearly.",
        "I complete what I start.",
        "I trust my decisions.",
        "I feel in control of my life."
    ],
    "Anahata (Heart)": [
        "I give and receive love easily.",
        "I forgive without suppressing emotions.",
        "I feel emotionally open and balanced.",
        "I maintain healthy boundaries.",
        "I feel compassion without exhaustion."
    ],
    "Vishuddha (Throat)": [
        "I express myself clearly.",
        "I speak my truth comfortably.",
        "I communicate honestly.",
        "My words align with actions.",
        "I feel heard."
    ],
    "Ajna (Third Eye)": [
        "I trust intuition.",
        "I observe thoughts calmly.",
        "I see patterns clearly.",
        "I balance logic and intuition.",
        "I feel mentally clear."
    ],
    "Sahasrara (Crown)": [
        "I feel spiritually connected.",
        "I feel guided in life.",
        "I trust higher intelligence.",
        "I feel life has meaning.",
        "I integrate spirituality daily."
    ]
}

# =====================================================
# INTERPRETATION LOGIC
# =====================================================
def interpret(score):
    if score <= 1:
        return "Blocked"
    elif score <= 2:
        return "Underactive"
    elif score <= 3:
        return "Balanced"
    else:
        return "Overactive"

def generate_interpretation(results):
    lowest = min(results, key=results.get)
    highest = max(results, key=results.get)
    name = st.session_state.get("name", "Beautiful Soul")

    return (
        f"{name}, your strongest energy center is {highest}. "
        f"The chakra needing most alignment is {lowest}. "
        f"By gently working on {lowest}, your entire energy system "
        f"will naturally harmonize and strengthen."
    )

# =====================================================
# WATERMARK FUNCTION
# =====================================================
def add_watermark(canvas_obj, doc):
    if os.path.exists("mandala.png"):
        width, height = A4
        canvas_obj.saveState()
        canvas_obj.setFillAlpha(0.05)
        canvas_obj.drawImage(
            "mandala.png",
            width / 6,
            height / 4,
            width=400,
            preserveAspectRatio=True,
            mask='auto'
        )
        canvas_obj.restoreState()

# =====================================================
# PDF GENERATOR
# =====================================================
def generate_pdf(results):

    filename = f"{REPORT_FOLDER}/Chakra_Report_{uuid.uuid4().hex[:8].upper()}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("<b>Chakra Assessment Report</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    # User Info
    elements.append(Paragraph(f"Name: {st.session_state.name}", styles["Normal"]))
    elements.append(Paragraph(f"Age: {st.session_state.age}", styles["Normal"]))
    elements.append(Paragraph(f"Phone: {st.session_state.phone}", styles["Normal"]))
    elements.append(Paragraph(f"Location: {st.session_state.location}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%d-%m-%Y')}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Table
    table_data = [["Chakra", "Average", "Status"]]

    for chakra, avg in results.items():
        table_data.append([chakra, avg, interpret(avg)])

    table = Table(table_data, colWidths=[200, 70, 90])

    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.black),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (1,1), (-1,-1), 'CENTER')
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    # Chart (No Overlap)
    drawing = Drawing(500, 250)
    chart = VerticalBarChart()
    chart.x = 60
    chart.y = 60
    chart.height = 140
    chart.width = 380

    chart.data = [[v for v in results.values()]]

    short_names = [
        "Root", "Sacral", "Solar",
        "Heart", "Throat", "Third Eye", "Crown"
    ]

    chart.categoryAxis.categoryNames = short_names
    chart.categoryAxis.labels.angle = 45
    chart.categoryAxis.labels.fontSize = 8

    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 4
    chart.valueAxis.valueStep = 1

    chakra_colors = [
        colors.red,
        colors.orange,
        colors.yellow,
        colors.green,
        colors.blue,
        colors.indigo,
        colors.violet
    ]

    for i in range(len(chakra_colors)):
        chart.bars[(0, i)].fillColor = chakra_colors[i]

    drawing.add(chart)
    elements.append(drawing)
    elements.append(Spacer(1, 20))

    # Primary Healing Focus
    lowest = min(results, key=results.get)
    elements.append(Paragraph(
        f"<b>Primary Healing Focus:</b> {lowest}",
        styles["Heading2"]
    ))
    elements.append(Spacer(1, 12))

    # Interpretation
    elements.append(Paragraph(
        "<b>Personalized Energy Interpretation</b>",
        styles["Heading2"]
    ))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(generate_interpretation(results), styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Disclaimer
    elements.append(Paragraph(
        "<i>Disclaimer: This report is intended for holistic self-awareness "
        "and personal development purposes only and does not replace "
        "medical or psychological advice.</i>",
        styles["Normal"]
    ))

    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)

    return filename

# =====================================================
# USER REGISTRATION
# =====================================================
st.title("🌀 Chakra Healing Energy Portal")

if not st.session_state.authenticated:

    st.header("Energy Receiver Registration")

    name = st.text_input("Full Name")
    age = st.number_input("Age", 1, 100)
    phone = st.text_input("Phone Number")
    location = st.text_input("Location")

    if st.button("Generate Access"):
        if not name or not phone or not age:
            st.error("Name, Age and Phone are required.")
        else:
            password = name[0].upper() + phone[-3:] + str(age)
            st.session_state.password = password
            st.session_state.name = name
            st.session_state.age = age
            st.session_state.phone = phone
            st.session_state.location = location
            st.success(f"Your access password: {password}")

    if "password" in st.session_state:
        entered = st.text_input("Enter Password", type="password")
        if st.button("Unlock Assessment"):
            if entered == st.session_state.password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")

# =====================================================
# QUESTIONNAIRE
# =====================================================
if st.session_state.authenticated:

    st.header("📋 Chakra Questionnaire")

    results = {}

    for chakra, questions in chakras.items():
        st.subheader(chakra)
        scores = []
        for q in questions:
            score = st.slider(q, 0, 4, 2, key=f"{chakra}_{q}")
            scores.append(score)
        results[chakra] = round(sum(scores) / len(scores), 2)

    if st.button("Generate Premium Energy Report"):
        pdf_path = generate_pdf(results)

        with open(pdf_path, "rb") as f:
            st.download_button(
                "Download Report",
                f,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf"
            )

        st.success("Premium Report Generated Successfully 🌿")
