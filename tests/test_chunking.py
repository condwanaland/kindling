import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from files import chunking


@pytest.fixture
def credentials():
    return SimpleNamespace(
        sender_email="sender@example.com",
        sender_pword="secret",
        recipient_email="usual@kindle.com",
        alternate_recipient_email="alternate@kindle.com",
    )


def test_load_credentials_is_lazy(monkeypatch, credentials):
    monkeypatch.setitem(
        sys.modules,
        "auth_secrets",
        SimpleNamespace(Creds=credentials),
    )

    assert chunking.load_credentials() is credentials


@pytest.mark.parametrize(
    ("recipients", "expected"),
    [
        (None, "usual@kindle.com"),
        ("one@kindle.com", "one@kindle.com"),
        (["one@kindle.com", "two@kindle.com"], "one@kindle.com, two@kindle.com"),
    ],
)
def test_init_email_handles_supported_recipient_forms(
    credentials,
    recipients,
    expected,
):
    message = chunking.init_email(recipients, credentials=credentials)

    assert message["From"] == credentials.sender_email
    assert message["To"] == expected
    assert not chunking.has_attachments(message)
    assert chunking.attachment_count(message) == 0


def test_add_attachment_sets_filename_mime_type_and_payload(tmp_path, credentials):
    book = tmp_path / "Book.epub"
    book.write_bytes(b"epub contents")
    message = chunking.init_email(credentials=credentials)

    chunking.add_attachment(message, str(book), "Renamed.epub")

    attachment = next(message.iter_attachments())
    assert attachment.get_filename() == "Renamed.epub"
    assert attachment.get_content_type() == "application/epub+zip"
    assert attachment.get_payload(decode=True) == b"epub contents"
    assert chunking.has_attachments(message)
    assert chunking.attachment_count(message) == 1
    assert chunking.message_size(message) == len(message.as_bytes())


def test_add_attachment_falls_back_to_binary_mime_type(tmp_path, credentials):
    book = tmp_path / "Book.unknown-extension"
    book.write_bytes(b"contents")
    message = chunking.init_email(credentials=credentials)

    chunking.add_attachment(message, str(book), book.name)

    attachment = next(message.iter_attachments())
    assert attachment.get_content_type() == "application/octet-stream"


def test_send_email_logs_in_sends_and_quits(monkeypatch, credentials):
    mail_server = Mock()
    smtp_ssl = Mock(return_value=mail_server)
    monkeypatch.setattr(chunking.smtplib, "SMTP_SSL", smtp_ssl)
    message = chunking.init_email(credentials=credentials)

    chunking.send_email(message, credentials=credentials)

    smtp_ssl.assert_called_once_with("smtp.gmail.com")
    mail_server.login.assert_called_once_with("sender@example.com", "secret")
    mail_server.send_message.assert_called_once_with(message)
    mail_server.quit.assert_called_once_with()
