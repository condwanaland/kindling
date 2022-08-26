#!/usr/bin/env python3

import constants as C
import glob
import os
import kindle_utils
import importlib
importlib.reload(kindle_utils)
importlib.reload(C)


calibre_path = "/Users/conorneilson/Documents/Books/Calibre Library"

class GetFiles():
    
    files = glob.glob(calibre_path + '/**/*.epub', recursive=True)
    kindle_utils.write_file(C.FilePaths.WORKING_DIR + C.FilePaths.CURRENT, files)

    def __init__(self):
        self.current_file = C.FilePaths.WORKING_DIR + C.FilePaths.CURRENT
        self.previous_file = C.FilePaths.WORKING_DIR + C.FilePaths.PREVIOUS
        self.new_file = C.FilePaths.WORKING_DIR + C.FilePaths.NEW
        self.current_books = kindle_utils.read_file(self.current_file)
        self.previous_books = kindle_utils.read_file(self.previous_file)
        self.new_books = self.__get_new_books()
        self.new_books_names = self.__get_new_books_names()

    def __get_new_books(self):
        new_books = []
        for book in self.current_books:
            if book not in self.previous_books:
                new_books.append(book)
        #return self.new_books = new_books
        return new_books

    def __get_new_books_names(self):
        new_books_names = []
        for book in self.new_books:
            new_books_names.append(os.path.basename(book))
        return new_books_names

    def cleanup(self):
        kindle_utils.write_file(self.previous_file, self.current_books)
        os.remove(self.current_file)

    # def get_new_books_paths(self):
    #     new_books_paths = []
    #     for book in self.new_books:
    #         new_books_paths.append(book)
    #     return new_books_paths


Books = GetFiles()
print(Books.current_books)
print(Books.previous_books)
print(Books.new_books)
print(Books.new_books_names())
print(Books.get_new_books())
"""
files = glob.glob(converted_books + '/**/*.epub', recursive=True)

kindle_utils.write_file(C.FilePaths.WORKING_DIR, files, C.FilePaths.CURRENT)
current_file = kindle_utils.read_file(C.FilePaths.WORKING_DIR + C.FilePaths.CURRENT)


previous_file = kindle_utils.read_file(C.FilePaths.WORKING_DIR + C.FilePaths.PREVIOUS)

new_books = list(set(current_file) - set(previous_file))

kindle_utils.write_file(C.FilePaths.WORKING_DIR, new_books, C.FilePaths.NEW)
print(new_books)

# Need to then clean up state. Not sure when this should be run
kindle_utils.write_file(C.FilePaths.WORKING_DIR, current_file, C.FilePaths.PREVIOUS)
os.remove(C.FilePaths.WORKING_DIR + C.FilePaths.CURRENT)



"""
