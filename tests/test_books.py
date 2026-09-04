import os

import pytest

from files import books as books_module
from files import constants
from files import kindle_utils


def configure_paths(monkeypatch, tmp_path, create_library=True):
    working_directory = tmp_path / "working"
    library = tmp_path / "library"
    landing = tmp_path / "landing"
    if create_library:
        library.mkdir()
    landing.mkdir()

    monkeypatch.setattr(
        constants.FilePaths,
        "WORKING_DIR",
        f"{working_directory}{os.sep}",
    )
    monkeypatch.setattr(constants.FilePaths, "CALIBRE_LIBRARY", str(library))
    monkeypatch.setattr(constants.FilePaths, "CALIBRE_LANDING", str(landing))
    return working_directory, library


def test_finds_only_new_sendable_epubs(monkeypatch, tmp_path):
    working_directory, library = configure_paths(monkeypatch, tmp_path)
    working_directory.mkdir()

    existing_book = library / "Existing" / "Existing.epub"
    new_book = library / "New" / "New.epub"
    original_book = library / "New" / "original_epub.epub"
    trashed_book = library / ".caltrash" / "Trash" / "Trash.epub"
    for book in [existing_book, new_book, original_book, trashed_book]:
        book.parent.mkdir(parents=True, exist_ok=True)
        book.write_bytes(b"book")

    kindle_utils.write_file(
        working_directory / constants.FilePaths.PREVIOUS,
        [str(existing_book)],
    )

    books = books_module.Books(str(library))

    assert books.new_books == [str(new_book)]
    assert books.new_books_names == ["New.epub"]
    assert books.num_new_books() == 1


def test_cleanup_records_books_backs_up_baseline_and_removes_current(
    monkeypatch,
    tmp_path,
):
    working_directory, library = configure_paths(monkeypatch, tmp_path)
    working_directory.mkdir()
    previous_file = working_directory / constants.FilePaths.PREVIOUS
    previous_file.write_text("previous.epub\n")
    new_book = library / "New.epub"
    new_book.write_bytes(b"book")

    books = books_module.Books(str(library))
    current_file = working_directory / constants.FilePaths.CURRENT
    books.cleanup()

    assert not current_file.exists()
    assert (working_directory / constants.FilePaths.NEW).read_text() == (
        f"{new_book}\n"
    )
    assert previous_file.read_text() == f"{new_book}\n"
    backups = list(working_directory.glob("book_list.txt.*.bak"))
    assert len(backups) == 1
    assert backups[0].read_text() == "previous.epub\n"


def test_initial_setup_creates_working_directory_and_empty_baseline(
    monkeypatch,
    tmp_path,
):
    working_directory, _ = configure_paths(monkeypatch, tmp_path)

    books_module.Books.initial_setup()

    assert working_directory.is_dir()
    assert (working_directory / constants.FilePaths.PREVIOUS).read_text() == ""


def test_initial_setup_rejects_missing_calibre_library(monkeypatch, tmp_path):
    configure_paths(monkeypatch, tmp_path, create_library=False)

    with pytest.raises(Exception, match="Calibre library not found"):
        books_module.Books.initial_setup()
