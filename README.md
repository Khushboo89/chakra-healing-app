# 🌿 Chakra Healing App

A Streamlit-based chakra healing registration app that sends secure access details via SendGrid email.

## 🚀 Features
- Free SendGrid email integration
- Secure password generation
- Streamlit Cloud compatible
- No SMTP required

## 🔐 Secrets Setup (Streamlit Cloud)

Add the following in **App → Settings → Secrets**:

```toml
SENDGRID_API_KEY = "SG_xxxxxxxxxxxxx"
FROM_EMAIL = "youremailaddress@gmail.com"


## Local Setup
pip install -r requirements.txt
streamlit run app.py

## Deployment
Deploy easily on Streamlit Cloud by adding secrets.

## Disclaimer
For spiritual and wellness purposes only.
