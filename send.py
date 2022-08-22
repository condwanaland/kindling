import smtplib
import mimetypes
from email.message import EmailMessage
import secrets as S
import kindle_utils as K
import constants as C
import importlib
importlib.reload(K)
importlib.reload(S)

new_books = K.read_file(C.FilePaths.WORKING_DIR + C.FilePaths.NEW)

books = K.process_list(new_books)

print(books)

message = EmailMessage()
sender = S.Creds.email
recipient = S.Creds.email
message['From'] = sender
message['To'] = recipient
message['Subject'] = 'Learning to send email from medium.com'
body = """Hello
I am learning to send emails using Python!!!"""
message.set_content(body)
mime_type, _ = mimetypes.guess_type(books[0]) 
mime_type, mime_subtype = mime_type.split('/')
with open(books[0], 'rb') as file:
 message.add_attachment(file.read(),
 maintype=mime_type,
 subtype=mime_subtype,
 filename='Skeleton Key - Anthony Horowitz.epub')
print(message)
mail_server = smtplib.SMTP_SSL('smtp.gmail.com')
mail_server.set_debuglevel(1)
mail_server.login(S.Creds.email, S.Creds.pword)
mail_server.send_message(message)
mail_server.quit()