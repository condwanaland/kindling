#!/usr/bin/env python3

import os
import smtplib
import sys
import mimetypes
from email.message import EmailMessage
import secrets as S
import books as B
import process_books as P
import constants as C
import chunking as K

calibre_path = C.FilePaths.CALIBRE_LIBRARY
landing_path = C.FilePaths.CALIBRE_LANDING

os.path.getsize(C.FilePaths.CALIBRE_LANDING)
os.path.getsize(C.FilePaths.CALIBRE_LIBRARY)

books_to_convert = P.check_landing(landing_path)
if books_to_convert != 0:
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

message = K.init_email()

total_size = 0
for (book, book_name) in zip(books.new_books, books.new_books_names):
    attachment_size = os.path.getsize(book)
    print(attachment_size)
    if attachment_size + total_size > 25000000:
        K.send_email(message)
        message = K.init_email()

    with open(book, 'rb') as f:
        file_data = f.read()
        file_type = mimetypes.guess_type(book)[0]
        message.add_attachment(file_data, maintype=file_type, subtype='epub', filename=book_name)
    
    total_size = total_size + attachment_size

K.send_email(message)

books.cleanup()
