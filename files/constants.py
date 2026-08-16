import os


class FilePaths:
    WORKING_DIR = "/Users/cneilson/Documents/Books/email-dev/"
    CALIBRE_LIBRARY = "/Users/cneilson/Documents/Books/Calibre Library"
    CALIBRE_LANDING = "/Users/cneilson/Documents/Books/Calibre Landing"
    EPUB_EXPORT_ROOT = os.path.expanduser("~/Documents/Books")
    CURRENT = "current_file.txt"
    PREVIOUS = "book_list.txt"
    NEW = "new_books.txt"
