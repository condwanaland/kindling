from email.message import EmailMessage
import auth_secrets as S
import smtplib

def init_email() -> EmailMessage:
    message = EmailMessage()
    message['From'] = S.Creds.sender_email
    message['To'] = S.Creds.recipient_email
    return message

def send_email(message) -> None:
    mail_server = smtplib.SMTP_SSL('smtp.gmail.com')
    mail_server.set_debuglevel(1)
    mail_server.login(S.Creds.sender_email, S.Creds.sender_pword)
    mail_server.send_message(message)
    mail_server.quit()