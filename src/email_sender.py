import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv


load_dotenv()


def send_email():

    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    receiver = os.getenv("EMAIL_TO")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not sender or not password or not receiver:
        raise EnvironmentError(
            "Faltan variables de entorno para el envío de correo: "
            "EMAIL_USER, EMAIL_PASS y EMAIL_TO son obligatorias."
        )

    with open("data/report.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    message = MIMEMultipart("alternative")
    message["Subject"] = "IT Tech Daily Report"
    message["From"] = sender
    message["To"] = receiver

    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, message.as_string())
        server.quit()
        print("\nCorreo enviado correctamente")
    except Exception as e:
        print(f"\nError enviando correo: {e}")
