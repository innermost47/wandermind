import os
from email.message import EmailMessage
from email.utils import formataddr
from dotenv import load_dotenv
import aiosmtplib
from config import ENVIRONMENT

load_dotenv()


async def send_email(recipient, subject, content):
    msg = EmailMessage()
    msg.set_content(content)

    msg["Subject"] = subject
    msg["From"] = formataddr(
        (os.environ.get("SMTP_FULL_NAME"), os.environ.get("SMTP_USERNAME"))
    )
    msg["To"] = recipient

    try:
        await aiosmtplib.send(
            msg,
            hostname=os.environ.get("SMTP_SERVER"),
            port=int(os.environ.get("SMTP_SERVER_PORT")),
            start_tls=True if ENVIRONMENT == "production" else False,
            username=os.environ.get("SMTP_USERNAME"),
            password=os.environ.get("SMTP_PASSWORD"),
        )
        print(f"Email sent successfully to: {recipient} with subject: {subject}")
    except Exception as e:
        print(
            f"Failed to send email to: {recipient} with subject: {subject}. Error: {str(e)}"
        )
        raise e


def get_email_for_account_creation(api_key, api_key_expiry_days=30):
    subject = "Votre clé d'API"
    email_body = f"""
    Bonjour,

    Votre compte a été créé avec succès. Voici votre clé d'api personnelle, à ne pas perdre, car elle est nécessaire pour vous connecter :

    Clé d'API : {api_key}

    Cette clé d'API a une durée de validité de {api_key_expiry_days} jours. Assurez-vous de la conserver en sécurité.

    Si vous avez des questions ou besoin d'assistance, n'hésitez pas à me contacter.

    Cordialement,

    {os.environ.get('EMAIL_SIGNATURE')}
    """
    return subject, email_body
