import datetime
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from files import process_books


def test_save_epubs_preserves_duplicate_filenames(tmp_path):
    first_source = tmp_path / "first"
    second_source = tmp_path / "second"
    first_source.mkdir()
    second_source.mkdir()
    first_book = first_source / "Example.epub"
    second_book = second_source / "Example.epub"
    first_book.write_text("first")
    second_book.write_text("second")

    export_folder = process_books.save_epubs(
        [str(first_book), str(second_book)],
        str(tmp_path / "exports"),
        now=datetime.datetime(2026, 8, 16, 14, 30, 5),
    )

    export_path = tmp_path / "exports" / "Kindle Export 2026-08-16_143005"
    assert export_folder == str(export_path)
    assert sorted(path.name for path in export_path.iterdir()) == [
        "Example (2).epub",
        "Example.epub",
    ]
    assert (export_path / "Example.epub").read_text() == "first"
    assert (export_path / "Example (2).epub").read_text() == "second"


def test_save_epubs_creates_unique_folder_for_repeated_timestamp(tmp_path):
    now = datetime.datetime(2026, 8, 16, 14, 30, 5)

    first_folder = process_books.save_epubs([], str(tmp_path), now=now)
    second_folder = process_books.save_epubs([], str(tmp_path), now=now)

    assert second_folder == f"{first_folder} (2)"


def test_save_epubs_raises_when_a_source_book_is_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        process_books.save_epubs(
            [str(tmp_path / "missing.epub")],
            str(tmp_path / "exports"),
        )


@pytest.mark.parametrize(("return_code", "expected"), [(0, True), (1, False)])
def test_open_folder_reports_command_result(monkeypatch, return_code, expected):
    run = Mock(return_value=SimpleNamespace(returncode=return_code))
    monkeypatch.setattr(process_books.subprocess, "run", run)

    assert process_books.open_folder("/export folder") is expected
    run.assert_called_once_with(["open", "/export folder"], check=False)


def test_check_landing_counts_entries(tmp_path):
    (tmp_path / "one.epub").write_bytes(b"one")
    (tmp_path / "two.mobi").write_bytes(b"two")

    assert process_books.check_landing(str(tmp_path)) == 2


def test_calibre_convert_opens_waits_for_conversion_and_quits(monkeypatch):
    system = Mock()
    sleep = Mock()
    glob = Mock(side_effect=[["queued"], ["queued"], []])
    monkeypatch.setattr(process_books.os, "system", system)
    monkeypatch.setattr(process_books.time, "sleep", sleep)
    monkeypatch.setattr(process_books.glob, "glob", glob)

    process_books.calibre_convert("/landing")

    assert system.call_args_list == [
        call("open -a Calibre"),
        call("osascript -e 'quit app \"calibre\"'"),
    ]
    assert sleep.call_count == 3
    assert glob.call_count == 3
