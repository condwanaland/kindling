#!/Users/cneilson/.pyenv/versions/kindling/bin/python

import copy
import os
import sys
from typing import Callable

from files import books as B
from files import chunking as K
from files import constants as C
from files import process_books as P


MAX_EMAIL_BYTES = 25_000_000
MAX_ATTACHMENTS = 25

HELP_TEXT = """
'y' = send these books to your usual Kindle address.
'a' = send these books to the alternate Kindle address.
'b' = send these books to both Kindle addresses.
's' = do not send these books; save them to a new, dated folder instead.
'n' = terminate program but keep any unsent books ready to be sent next time.
'r' = do not send these books but mark them as sent so they wont be prompted to send again.
'p' = print the names of the new books to be sent.
"""


def prompt_for_action(
    number_of_books: int,
    book_names: list[str],
    input_func: Callable[[str], str] = input,
    output_func: Callable[[object], None] = print,
) -> str:
    """Prompt until the user chooses an action that ends the prompt loop."""
    while True:
        action = input_func(
            f"Found {number_of_books} new books, continue? "
            "(y/a/b/s/n/r/p/help) "
        ).strip().lower()

        if action in {"y", "a", "b", "s", "n", "r"}:
            return action
        if action == "p":
            output_func(book_names)
        elif action == "help":
            output_func(HELP_TEXT)
        else:
            output_func("unrecognised input, please try again")


def recipient_emails_for(action: str, credentials=None) -> list[str]:
    """Resolve a send action to its configured recipient addresses."""
    credentials = credentials or K.load_credentials()
    if action == "y":
        return [credentials.recipient_email]
    if action == "a":
        return [credentials.alternate_recipient_email]
    if action == "b":
        return [
            credentials.recipient_email,
            credentials.alternate_recipient_email,
        ]
    raise ValueError(f"Unsupported send action: {action}")


def _send_batch(message, output_func: Callable[[object], None], final=False) -> None:
    label = "final batch" if final else "batch"
    output_func(
        f"Sending {label} with {K.attachment_count(message)} attachments "
        f"at {K.message_size(message)} bytes"
    )
    K.send_email(message)


def send_books(
    books: B.Books,
    recipient_emails: list[str],
    max_email_bytes: int = MAX_EMAIL_BYTES,
    max_attachments: int = MAX_ATTACHMENTS,
    output_func: Callable[[object], None] = print,
) -> None:
    """Attach and send books in batches that stay within the email limits."""
    message = K.init_email(recipient_emails)

    for book, book_name in zip(books.new_books, books.new_books_names):
        if K.attachment_count(message) >= max_attachments:
            _send_batch(message, output_func)
            message = K.init_email(recipient_emails)

        attachment_size = os.path.getsize(book)
        candidate = copy.deepcopy(message)
        K.add_attachment(candidate, book, book_name)
        candidate_size = K.message_size(candidate)

        if candidate_size > max_email_bytes and K.has_attachments(message):
            _send_batch(message, output_func)
            message = K.init_email(recipient_emails)
            candidate = copy.deepcopy(message)
            K.add_attachment(candidate, book, book_name)
            candidate_size = K.message_size(candidate)

        if candidate_size > max_email_bytes:
            raise ValueError(
                f"{book_name} is {candidate_size} bytes as an email attachment "
                f"and cannot fit under the {max_email_bytes} byte limit"
            )

        output_func(
            f"Queued {book_name}: {attachment_size} file bytes, "
            f"{candidate_size} email bytes"
        )
        message = candidate

    if K.has_attachments(message):
        _send_batch(message, output_func, final=True)


def run(
    input_func: Callable[[str], str] = input,
    output_func: Callable[[object], None] = print,
) -> int:
    """Run the interactive book-processing workflow."""
    calibre_path = C.FilePaths.CALIBRE_LIBRARY
    landing_path = C.FilePaths.CALIBRE_LANDING

    if P.check_landing(landing_path):
        P.calibre_convert(landing_path)

    books = B.Books(calibre_path)
    number_of_books = books.num_new_books()
    if number_of_books == 0:
        output_func("No new books, exiting")
        return 0

    action = prompt_for_action(
        number_of_books,
        books.new_books_names,
        input_func=input_func,
        output_func=output_func,
    )

    if action == "n":
        output_func("exiting")
        return 0

    if action == "r":
        output_func("writing new baseline files")
        books.cleanup()
        output_func("exiting")
        return 0

    if action == "s":
        export_folder = P.save_epubs(
            books.new_books,
            C.FilePaths.EPUB_EXPORT_ROOT,
        )
        output_func(f"Saved {number_of_books} EPUBs to {export_folder}")
        books.cleanup()
        if not P.open_folder(export_folder):
            output_func(f"Could not open {export_folder} in Finder")
        output_func("exiting without sending email")
        return 0

    send_books(books, recipient_emails_for(action), output_func=output_func)
    books.cleanup()
    return 0


if __name__ == "__main__":
    sys.exit(run())
