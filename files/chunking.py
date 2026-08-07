from email.message import EmailMessage
import auth_secrets as S
import mimetypes
import smtplib

def init_email(recipient_emails=None) -> EmailMessage:
    message = EmailMessage()
    message['From'] = S.Creds.sender_email
    if recipient_emails is None:
        recipient_emails = [S.Creds.recipient_email]
    elif isinstance(recipient_emails, str):
        recipient_emails = [recipient_emails]
    message['To'] = ", ".join(recipient_emails)
    return message

def send_email(message) -> None:
    mail_server = smtplib.SMTP_SSL('smtp.gmail.com')
    #mail_server.set_debuglevel(1)
    mail_server.login(S.Creds.sender_email, S.Creds.sender_pword)
    mail_server.send_message(message)
    mail_server.quit()


def add_attachment(message: EmailMessage, path: str, filename: str) -> None:
    file_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
    maintype, subtype = file_type.split("/", 1)

    with open(path, "rb") as f:
        message.add_attachment(
            f.read(),
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
