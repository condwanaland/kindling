#!/usr/bin/env python3

import os
import sys
import mimetypes
from files import books as B
from files import process_books as P
from files import constants as C
from files import chunking as K

calibre_path = C.FilePaths.CALIBRE_LIBRARY
landing_path = C.FilePaths.CALIBRE_LANDING

books_to_convert = P.check_landing(landing_path)
if books_to_convert != 0:
    P.calibre_convert(landing_path)

books = B.Books(calibre_path)
#books.new_books
num = books.num_new_books()

if num == 0:
    print("No new books, exiting")
    sys.exit()

while True:
    cont = input(f"Found {num} new books, continue? (y/n/r/p/help)")

    if cont == "n":
        print("exiting")
        sys.exit()
    elif cont == "r":
        print("writing new baseline files")
        books.cleanup()
        print("exiting")
        sys.exit()
    elif cont == "p":
        print(books.new_books_names)
        continue
    elif cont == "help":
        print("'y' = continue and send these books to kindle.")
        print("'n' = terminate program but keep any unsent books ready to be sent next time")
        print("'r' = do not send these books but mark them as sent so they wont be prompted to send again.")
        print("'p' = print the names of the new books to be sent.")
        continue
    elif cont == "y":
        break
    else:
        print("unrecognised input, please try again")
        continue

message = K.init_email()

total_size = 0
for (book, book_name) in zip(books.new_books, books.new_books_names):
    attachment_size = os.path.getsize(book)
    print(attachment_size)
    if attachment_size + total_size > 25000000:
        K.send_email(message)
        message = K.init_email()
        total_size = 0

    with open(book, 'rb') as f:
        file_data = f.read()
        file_type = mimetypes.guess_type(book)[0]
        message.add_attachment(file_data, maintype=file_type, subtype='epub', filename=book_name)
    
    total_size = total_size + attachment_size

K.send_email(message)

books.cleanup()
