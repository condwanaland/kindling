import datetime
import os
import tempfile
import unittest

from files.process_books import save_epubs


class SaveEpubsTest(unittest.TestCase):
    def test_saves_every_epub_without_overwriting_duplicate_names(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            first_source = os.path.join(temporary_directory, "first")
            second_source = os.path.join(temporary_directory, "second")
            export_root = os.path.join(temporary_directory, "exports")
            os.makedirs(first_source)
            os.makedirs(second_source)

            first_book = os.path.join(first_source, "Example.epub")
            second_book = os.path.join(second_source, "Example.epub")
            with open(first_book, "w") as book:
                book.write("first")
            with open(second_book, "w") as book:
                book.write("second")

            export_folder = save_epubs(
                [first_book, second_book],
                export_root,
                now=datetime.datetime(2026, 8, 16, 14, 30, 5),
            )

            self.assertEqual(
                export_folder,
                os.path.join(export_root, "Kindle Export 2026-08-16_143005"),
            )
            self.assertEqual(
                sorted(os.listdir(export_folder)),
                ["Example (2).epub", "Example.epub"],
            )
            with open(os.path.join(export_folder, "Example.epub")) as book:
                self.assertEqual(book.read(), "first")
            with open(os.path.join(export_folder, "Example (2).epub")) as book:
                self.assertEqual(book.read(), "second")

    def test_creates_a_unique_folder_for_repeated_timestamp(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            now = datetime.datetime(2026, 8, 16, 14, 30, 5)
            first_folder = save_epubs([], temporary_directory, now=now)
            second_folder = save_epubs([], temporary_directory, now=now)

            self.assertNotEqual(first_folder, second_folder)
            self.assertEqual(second_folder, f"{first_folder} (2)")


if __name__ == "__main__":
    unittest.main()
