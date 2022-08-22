#!/usr/bin/env python3

import os
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

books = K.process_list(new_books) # This removes the newline characters and empty elements


print(books)

book_names = []
for book in books:
    book_names.append(os.path.basename(book))


assert len(books) == len(book_names)

message = EmailMessage()
sender = S.Creds.sender_email
recipient = S.Creds.recipient_email
message['From'] = sender
message['To'] = recipient
body = """sent from python script"""
message.set_content(body)

for (book, book_name) in zip(books, book_names):
    with open(book, 'rb') as f:
        file_data = f.read()
        file_type = mimetypes.guess_type(book)[0]
        message.add_attachment(file_data, maintype=file_type, subtype='epub', filename=book_name)
"""
mime_type, _ = mimetypes.guess_type(books[0]) 
mime_type, mime_subtype = mime_type.split('/')
with open(books[0], 'rb') as file:
 message.add_attachment(file.read(),
 maintype=mime_type,
 subtype=mime_subtype,
 filename=name)
"""
print(message)
mail_server = smtplib.SMTP_SSL('smtp.gmail.com')
mail_server.set_debuglevel(1)
mail_server.login(S.Creds.sender_email, S.Creds.sender_pword)
mail_server.send_message(message)
mail_server.quit()