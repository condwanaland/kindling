#!/usr/bin/env python3

import constants as C
import glob
import os
import kindle_utils
import importlib
importlib.reload(kindle_utils)
importlib.reload(C)


files = glob.glob(C.FilePaths.CALIBRE_LIBRARY + '/**/*.epub', recursive=True)

kindle_utils.write_file(C.FilePaths.WORKING_DIR, files, C.FilePaths.CURRENT)
current_file = kindle_utils.read_file(C.FilePaths.WORKING_DIR + C.FilePaths.CURRENT)


previous_file = kindle_utils.read_file(C.FilePaths.WORKING_DIR + C.FilePaths.PREVIOUS)

new_books = list(set(current_file) - set(previous_file))

kindle_utils.write_file(C.FilePaths.WORKING_DIR, new_books, C.FilePaths.NEW)
print(new_books)

# Need to then clean up state. Not sure when this should be run
kindle_utils.write_file(C.FilePaths.WORKING_DIR, current_file, C.FilePaths.PREVIOUS)
os.remove(C.FilePaths.WORKING_DIR + C.FilePaths.CURRENT)



