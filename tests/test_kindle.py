import copy
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import kindle


@pytest.fixture
def credentials():
    return SimpleNamespace(
        sender_email="sender@example.com",
        sender_pword="secret",
        recipient_email="usual@kindle.com",
        alternate_recipient_email="alternate@kindle.com",
    )


def make_book_collection(tmp_path, contents):
    paths = []
    names = []
    for number, content in enumerate(contents, start=1):
        book = tmp_path / f"Book {number}.epub"
        book.write_bytes(content)
        paths.append(str(book))
        names.append(book.name)
    return SimpleNamespace(new_books=paths, new_books_names=names)


def configure_email_mocks(monkeypatch, credentials):
    sent_messages = []
    monkeypatch.setattr(kindle.K, "load_credentials", lambda: credentials)
    monkeypatch.setattr(kindle.K, "send_email", sent_messages.append)
    return sent_messages


def test_prompt_prints_books_and_help_then_retries_invalid_input():
    responses = iter(["p", "help", "what", " Y "])
    output = []

    action = kindle.prompt_for_action(
        2,
        ["One.epub", "Two.epub"],
        input_func=lambda _: next(responses),
        output_func=output.append,
    )

    assert action == "y"
    assert output == [
        ["One.epub", "Two.epub"],
        kindle.HELP_TEXT,
        "unrecognised input, please try again",
    ]


@pytest.mark.parametrize(
    ("action", "expected"),
    [
        ("y", ["usual@kindle.com"]),
        ("a", ["alternate@kindle.com"]),
        ("b", ["usual@kindle.com", "alternate@kindle.com"]),
    ],
)
def test_recipient_emails_for_send_actions(credentials, action, expected):
    assert kindle.recipient_emails_for(action, credentials) == expected


def test_recipient_emails_rejects_non_send_action(credentials):
    with pytest.raises(ValueError, match="Unsupported send action"):
        kindle.recipient_emails_for("s", credentials)


def test_send_books_sends_one_final_batch(tmp_path, monkeypatch, credentials):
    books = make_book_collection(tmp_path, [b"first", b"second"])
    sent_messages = configure_email_mocks(monkeypatch, credentials)

    kindle.send_books(books, [credentials.recipient_email], output_func=lambda _: None)

    assert len(sent_messages) == 1
    assert kindle.K.attachment_count(sent_messages[0]) == 2
    assert [
        attachment.get_filename()
        for attachment in sent_messages[0].iter_attachments()
    ] == books.new_books_names


def test_send_books_splits_on_attachment_limit(tmp_path, monkeypatch, credentials):
    books = make_book_collection(tmp_path, [b"first", b"second"])
    sent_messages = configure_email_mocks(monkeypatch, credentials)

    kindle.send_books(
        books,
        [credentials.recipient_email],
        max_attachments=1,
        output_func=lambda _: None,
    )

    assert len(sent_messages) == 2
    assert [kindle.K.attachment_count(message) for message in sent_messages] == [1, 1]


def test_send_books_splits_on_encoded_message_size(
    tmp_path,
    monkeypatch,
    credentials,
):
    books = make_book_collection(tmp_path, [b"a" * 500, b"b" * 500])
    sent_messages = configure_email_mocks(monkeypatch, credentials)
    base_message = kindle.K.init_email([credentials.recipient_email])
    first_message = copy.deepcopy(base_message)
    kindle.K.add_attachment(first_message, books.new_books[0], books.new_books_names[0])
    combined_message = copy.deepcopy(first_message)
    kindle.K.add_attachment(
        combined_message,
        books.new_books[1],
        books.new_books_names[1],
    )
    limit = (
        kindle.K.message_size(first_message)
        + kindle.K.message_size(combined_message)
    ) // 2

    kindle.send_books(
        books,
        [credentials.recipient_email],
        max_email_bytes=limit,
        output_func=lambda _: None,
    )

    assert len(sent_messages) == 2
    assert [kindle.K.attachment_count(message) for message in sent_messages] == [1, 1]


def test_send_books_rejects_single_oversized_book(
    tmp_path,
    monkeypatch,
    credentials,
):
    books = make_book_collection(tmp_path, [b"too large"])
    sent_messages = configure_email_mocks(monkeypatch, credentials)

    with pytest.raises(ValueError, match="cannot fit"):
        kindle.send_books(
            books,
            [credentials.recipient_email],
            max_email_bytes=1,
            output_func=lambda _: None,
        )

    assert sent_messages == []


def workflow_books(paths=None):
    if paths is None:
        paths = ["/library/Book.epub"]
    return SimpleNamespace(
        new_books=paths,
        new_books_names=[path.rsplit("/", 1)[-1] for path in paths],
        num_new_books=Mock(return_value=len(paths)),
        cleanup=Mock(),
    )


def configure_workflow(monkeypatch, books, landing_count=0):
    check_landing = Mock(return_value=landing_count)
    convert = Mock()
    monkeypatch.setattr(kindle.P, "check_landing", check_landing)
    monkeypatch.setattr(kindle.P, "calibre_convert", convert)
    monkeypatch.setattr(kindle.B, "Books", Mock(return_value=books))
    return check_landing, convert


def test_run_exits_without_prompting_when_there_are_no_new_books(monkeypatch):
    books = workflow_books([])
    configure_workflow(monkeypatch, books)
    output = []

    result = kindle.run(
        input_func=lambda _: pytest.fail("input should not be requested"),
        output_func=output.append,
    )

    assert result == 0
    assert output == ["No new books, exiting"]
    books.cleanup.assert_not_called()


def test_run_converts_landing_books_before_honouring_no_send(monkeypatch):
    books = workflow_books()
    _, convert = configure_workflow(monkeypatch, books, landing_count=1)

    result = kindle.run(input_func=lambda _: "n", output_func=lambda _: None)

    assert result == 0
    convert.assert_called_once_with(kindle.C.FilePaths.CALIBRE_LANDING)
    books.cleanup.assert_not_called()


def test_run_reset_action_updates_baseline_without_sending(monkeypatch):
    books = workflow_books()
    configure_workflow(monkeypatch, books)
    send_books = Mock()
    monkeypatch.setattr(kindle, "send_books", send_books)

    kindle.run(input_func=lambda _: "r", output_func=lambda _: None)

    books.cleanup.assert_called_once_with()
    send_books.assert_not_called()


@pytest.mark.parametrize("folder_opened", [True, False])
def test_run_save_action_exports_cleans_up_and_opens_folder(
    monkeypatch,
    folder_opened,
):
    books = workflow_books()
    configure_workflow(monkeypatch, books)
    save_epubs = Mock(return_value="/exports/Kindle Export")
    open_folder = Mock(return_value=folder_opened)
    send_books = Mock()
    monkeypatch.setattr(kindle.P, "save_epubs", save_epubs)
    monkeypatch.setattr(kindle.P, "open_folder", open_folder)
    monkeypatch.setattr(kindle, "send_books", send_books)
    output = []

    kindle.run(input_func=lambda _: "s", output_func=output.append)

    save_epubs.assert_called_once_with(
        books.new_books,
        kindle.C.FilePaths.EPUB_EXPORT_ROOT,
    )
    books.cleanup.assert_called_once_with()
    open_folder.assert_called_once_with("/exports/Kindle Export")
    send_books.assert_not_called()
    assert any("Could not open" in line for line in output) is not folder_opened


def test_run_both_action_sends_then_updates_baseline(monkeypatch, credentials):
    books = workflow_books()
    configure_workflow(monkeypatch, books)
    send_books = Mock()
    monkeypatch.setattr(kindle, "send_books", send_books)
    monkeypatch.setattr(kindle.K, "load_credentials", lambda: credentials)

    kindle.run(input_func=lambda _: "b", output_func=lambda _: None)

    send_books.assert_called_once()
    assert send_books.call_args.args == (
        books,
        [credentials.recipient_email, credentials.alternate_recipient_email],
    )
    assert callable(send_books.call_args.kwargs["output_func"])
    books.cleanup.assert_called_once_with()


def test_run_does_not_update_baseline_when_sending_fails(monkeypatch, credentials):
    books = workflow_books()
    configure_workflow(monkeypatch, books)
    monkeypatch.setattr(kindle.K, "load_credentials", lambda: credentials)
    monkeypatch.setattr(
        kindle,
        "send_books",
        Mock(side_effect=RuntimeError("SMTP failed")),
    )

    with pytest.raises(RuntimeError, match="SMTP failed"):
        kindle.run(input_func=lambda _: "y", output_func=lambda _: None)

    books.cleanup.assert_not_called()
