import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv


load_dotenv()


def send_email():

    sender = os.getenv(
        "EMAIL_SENDER"
    )

    password = os.getenv(
        "EMAIL_PASSWORD"
    )

    receiver = os.getenv(
        "EMAIL_RECEIVER"
    )

    with open(
        "data/report.html",
        "r",
        encoding="utf-8"
    ) as file:

        html_content = file.read()

    message = MIMEMultipart(
        "alternative"
    )

    message["Subject"] = (
        "IT Tech Daily Report"
    )

    message["From"] = sender

    message["To"] = receiver

    html_part = MIMEText(
        html_content,
        "html"
    )

    message.attach(
        html_part
    )

    try:

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        server.login(
            sender,
            password
        )

        server.sendmail(
            sender,
            receiver,
            message.as_string()
        )

        server.quit()

        print(
            "\nCorreo enviado correctamente"
        )

    except Exception as e:

        print(
            f"\nError enviando correo: {e}"
        )
