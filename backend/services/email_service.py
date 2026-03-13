# email_service.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

conf = ConnectionConfig(
    MAIL_USERNAME="johncarlsantos30@gmail.com",
    MAIL_PASSWORD="ajsbstffzfgupwpa",  
    MAIL_FROM="johncarlsantos30@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

async def send_otp_email(email: str, otp: str):
    message = MessageSchema(
        subject="Password Reset OTP",
        recipients=[email],
        body=f"""
        <h3>Password Reset</h3>
        <p>Your OTP is: <strong>{otp}</strong></p>
        <p>Expires in 5 minutes. Do not share this code.</p>
        """,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message)