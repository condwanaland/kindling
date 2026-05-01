#!/Users/cneilson/.pyenv/versions/kindling/bin/python

import os
import sys
import copy
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
        print(
            """
            'y' = continue and send these books to kindle.
            'n' = terminate program but keep any unsent books ready to be sent next time.
            'r' = do not send these books but mark them as sent so they wont be prompted to send again.
            'p' = print the names of the new books to be sent.
            """
        )
        continue
    elif cont == "y":
        break
    else:
        print("unrecognised input, please try again")
        continue

MAX_EMAIL_BYTES = 25_000_000
MAX_ATTACHMENTS = 25

message = K.init_email()
for (book, book_name) in zip(books.new_books, books.new_books_names):
    if K.attachment_count(message) >= MAX_ATTACHMENTS:
        print(
            f"Sending batch with {K.attachment_count(message)} attachments "
            f"at {K.message_size(message)} bytes"
        )
        K.send_email(message)
        message = K.init_email()

    attachment_size = os.path.getsize(book)
    candidate = copy.deepcopy(message)
    K.add_attachment(candidate, book, book_name)
    candidate_size = K.message_size(candidate)

    if candidate_size > MAX_EMAIL_BYTES and K.has_attachments(message):
        print(
            f"Sending batch with {K.attachment_count(message)} attachments "
            f"at {K.message_size(message)} bytes"
        )
        K.send_email(message)
        message = K.init_email()
        K.add_attachment(message, book, book_name)
        message_size = K.message_size(message)
        if message_size > MAX_EMAIL_BYTES:
            raise Exception(
                f"{book_name} is {message_size} bytes as an email attachment "
                f"and cannot fit under the {MAX_EMAIL_BYTES} byte limit"
            )
    elif candidate_size > MAX_EMAIL_BYTES:
        raise Exception(
            f"{book_name} is {candidate_size} bytes as an email attachment "
            f"and cannot fit under the {MAX_EMAIL_BYTES} byte limit"
        )
    else:
        print(f"Queued {book_name}: {attachment_size} file bytes, {candidate_size} email bytes")
        message = candidate

if K.has_attachments(message):
    print(
        f"Sending final batch with {K.attachment_count(message)} attachments "
        f"at {K.message_size(message)} bytes"
    )
    K.send_email(message)

books.cleanup()
