#!/usr/bin/env python3

import constants as C
import glob
import kindle_utils
import importlib
importlib.reload(kindle_utils)
importlib.reload(C)


converted_books = "/Users/conorneilson/Documents/Books/Calibre Library"

files = glob.glob(converted_books + '/**/*.epub', recursive=True)

kindle_utils.write_file(C.FilePaths.WORKING_DIR, files, C.FilePaths.CURRENT)
current_file = kindle_utils.read_file(C.FilePaths.WORKING_DIR + C.FilePaths.CURRENT)

previous_file = kindle_utils.read_file(C.FilePaths.WORKING_DIR + C.FilePaths.PREVIOUS)

new_books = list(set(current_file) - set(previous_file))

kindle_utils.write_file(C.FilePaths.WORKING_DIR, new_books, C.FilePaths.NEW)
print(new_books)





