from files import kindle_utils


def test_write_and_read_file_round_trip(tmp_path):
    destination = tmp_path / "books.txt"

    kindle_utils.write_file(destination, ["first.epub", "second.epub"])

    assert kindle_utils.read_file(destination) == [
        "first.epub",
        "second.epub",
    ]


def test_write_empty_file(tmp_path):
    destination = tmp_path / "books.txt"

    kindle_utils.write_file(destination, [])

    assert destination.read_text() == ""
    assert kindle_utils.read_file(destination) == []


def test_read_file_normalizes_windows_line_endings(tmp_path):
    source = tmp_path / "books.txt"
    source.write_bytes(b"first.epub\r\nsecond.epub\r\n")

    assert kindle_utils.read_file(source) == ["first.epub", "second.epub"]
