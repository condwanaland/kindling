import mimetypes
import smtplib
from email.message import EmailMessage


def load_credentials():
    """Load private email credentials only when an email action needs them."""
    import auth_secrets

    return auth_secrets.Creds


def init_email(recipient_emails=None, credentials=None) -> EmailMessage:
    credentials = credentials or load_credentials()
    message = EmailMessage()
    message["From"] = credentials.sender_email
    if recipient_emails is None:
        recipient_emails = [credentials.recipient_email]
    elif isinstance(recipient_emails, str):
        recipient_emails = [recipient_emails]
    message["To"] = ", ".join(recipient_emails)
    return message


def send_email(message, credentials=None) -> None:
    credentials = credentials or load_credentials()
    mail_server = smtplib.SMTP_SSL("smtp.gmail.com")
    mail_server.login(credentials.sender_email, credentials.sender_pword)
    mail_server.send_message(message)
    mail_server.quit()


def add_attachment(message: EmailMessage, path: str, filename: str) -> None:
    file_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
    maintype, subtype = file_type.split("/", 1)

    with open(path, "rb") as file:
        message.add_attachment(
            file.read(),
            maintype=maintype,
            subtype=subtype,
            filename=filename,
        )


def message_size(message: EmailMessage) -> int:
    return len(message.as_bytes())


def has_attachments(message: EmailMessage) -> bool:
    return message.is_multipart() and bool(message.get_payload())


def attachment_count(message: EmailMessage) -> int:
    if not message.is_multipart():
        return 0
    return len(message.get_payload())
