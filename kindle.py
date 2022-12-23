#!/usr/bin/env python3

import smtplib
import sys
import mimetypes
from email.message import EmailMessage
import secrets as S
import importlib
import books as B
import process_books as P
import constants as C
importlib.reload(B)

calibre_path = C.FilePaths.CALIBRE_LIBRARY
landing_path = C.FilePaths.CALIBRE_LANDING

P.calibre_convert(landing_path)

books = B.Books(calibre_path)
#books.new_books
num = books.num_new_books()

if num == 0:
    print("No new books, exiting")
    sys.exit()

cont = input(f"Found {num} new books, continue? (y/n/r)")

if cont == "n":
    print("exiting")
    sys.exit()
elif cont == "r":
    print("writing new baseline files")
    books.cleanup()
    print("exiting")
    sys.exit()

message = EmailMessage()
message['From'] = S.Creds.sender_email
message['To'] = S.Creds.recipient_email

for (book, book_name) in zip(books.new_books, books.new_books_names):
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
mail_server = smtplib.SMTP_SSL('smtp.gmail.com')
mail_server.set_debuglevel(1)
mail_server.login(S.Creds.sender_email, S.Creds.sender_pword)
mail_server.send_message(message)
mail_server.quit()
books.cleanup()