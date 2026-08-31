import os
import smtplib

from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv


# ======================================================
# LOAD ENVIRONMENT VARIABLES
# ======================================================

load_dotenv()


def send_email():

    # ==================================================
    # EMAIL CONFIGURATION
    # ==================================================

    sender = (
        os.getenv("EMAIL_USER")
        or os.getenv("EMAIL_SENDER")
    )

    password = (
        os.getenv("EMAIL_PASS")
        or os.getenv("EMAIL_PASSWORD")
    )

    receiver = (
        os.getenv("EMAIL_TO")
        or os.getenv("EMAIL_RECEIVER")
    )

    smtp_host = os.getenv(
        "SMTP_HOST",
        "smtp.gmail.com",
    )

    smtp_port = int(
        os.getenv(
            "SMTP_PORT",
            "587",
        )
    )

    # ==================================================
    # VALIDATE CONFIGURATION
    # ==================================================

    if not sender:

        raise EnvironmentError(
            "Falta EMAIL_USER o EMAIL_SENDER."
        )

    if not password:

        raise EnvironmentError(
            "Falta EMAIL_PASS o EMAIL_PASSWORD."
        )

    if not receiver:

        raise EnvironmentError(
            "Falta EMAIL_TO o EMAIL_RECEIVER."
        )

    # ==================================================
    # LOAD HTML REPORT
    # ==================================================

    report_path = "data/report.html"

    if not os.path.exists(
        report_path
    ):

        raise FileNotFoundError(
            f"No existe {report_path}"
        )

    with open(
        report_path,
        "r",
        encoding="utf-8",
    ) as file:

        html_content = file.read()

    # ==================================================
    # CREATE EMAIL
    # ==================================================

    # "related" permite que el HTML
    # pueda mostrar imágenes inline
    # mediante Content-ID.
    message = MIMEMultipart(
        "related"
    )

    message["Subject"] = (
        "IT Tech Daily Report"
    )

    message["From"] = sender

    message["To"] = receiver

    # ==================================================
    # HTML ALTERNATIVE
    # ==================================================

    alternative = MIMEMultipart(
        "alternative"
    )

    html_part = MIMEText(
        html_content,
        "html",
        "utf-8",
    )

    alternative.attach(
        html_part
    )

    message.attach(
        alternative
    )

    # ==================================================
    # ATTACH INFOGRAPHIC
    # ==================================================

    infographic_path = (
        "data/infographic.png"
    )

    if os.path.exists(
        infographic_path
    ):

        print(
            "\nAdjuntando infografía..."
        )

        with open(
            infographic_path,
            "rb",
        ) as file:

            image = MIMEImage(
                file.read(),
                _subtype="png",
            )

        # Este ID debe coincidir con:
        #
        #     src="cid:infographic"
        #
        # utilizado en report_generator.py

        image.add_header(
            "Content-ID",
            "<infographic>",
        )

        image.add_header(
            "Content-Disposition",
            "inline",
            filename="infographic.png",
        )

        message.attach(
            image
        )

    else:

        print(
            "\nNo se encontró "
            "data/infographic.png"
        )

    # ==================================================
    # SEND EMAIL
    # ==================================================

    try:

        print(
            "\nConectando con SMTP..."
        )

        with smtplib.SMTP(
            smtp_host,
            smtp_port,
        ) as server:

            server.ehlo()

            server.starttls()

            server.ehlo()

            server.login(
                sender,
                password,
            )

            server.sendmail(
                sender,
                receiver,
                message.as_string(),
            )

        print(
            "\nCorreo enviado correctamente."
        )

    except Exception as exc:

        print(
            "\nError enviando correo:"
        )

        print(
            str(exc)
        )

        raise
