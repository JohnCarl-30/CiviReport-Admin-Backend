# email_service.py
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")


async def send_otp_email(to_email: str, otp: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "CiviReport - Password Reset OTP"
    msg["From"] = MAIL_USERNAME
    msg["To"] = to_email

    html = f"""
    <h3>Password Reset</h3>
    <p>Your OTP is: <strong>{otp}</strong></p>
    <p>This code expires in 5 minutes. Do not share it.</p>
    """
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_USERNAME, to_email, msg.as_string())
        print(f"OTP email sent to {to_email}")
