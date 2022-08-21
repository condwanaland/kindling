#!/usr/bin/env python3

import constants as C
import glob
import kindle_utils
import importlib
importlib.reload(kindle_utils)
importlib.reload(C)

converted_books = "/Users/conorneilson/Documents/Books/Calibre Library"

files = glob.glob(converted_books + '/**/*.epub', recursive=True)

kindle_utils.write_file(working_dir, files, C.KindleFileNames.CURRENT)
current_file = kindle_utils.read_file(working_dir + C.KindleFileNames.CURRENT)

previous_file = kindle_utils.read_file(working_dir + C.KindleFileNames.PREVIOUS)

new_books = list(set(current_file) - set(previous_file))

kindle_utils.write_file(working_dir, new_books, "new_books.txt")
print(new_books)





