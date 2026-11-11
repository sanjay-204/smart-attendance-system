import smtplib
from email.mime.text import MIMEText

EMAIL = "sanjay.m2021c@vitstudent.ac.in"
PASSWORD = "swgdtpsidxerzrea"

def send_email(to, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL
        msg["To"] = to

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)

        print(f"📧 Email sent to {to}")

    except Exception as e:
        print("❌ Email failed:", e)