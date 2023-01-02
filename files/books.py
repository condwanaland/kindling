#!/usr/bin/env python3

import constants as C
import glob
import os
import kindle_utils

class Books():

    def __init__(self, calibre_path: str) -> None:
        files = glob.glob(calibre_path + '/**/*.epub', recursive=True)
        kindle_utils.write_file(C.FilePaths.WORKING_DIR + C.FilePaths.CURRENT, files)
        
        self.current_file = C.FilePaths.WORKING_DIR + C.FilePaths.CURRENT
        self.previous_file = C.FilePaths.WORKING_DIR + C.FilePaths.PREVIOUS
        self.new_file = C.FilePaths.WORKING_DIR + C.FilePaths.NEW
        self.current_books = kindle_utils.read_file(self.current_file)
        self.previous_books = kindle_utils.read_file(self.previous_file)
        self.new_books = self.__process_book_list(self.__get_new_books()) # This is a mess. How to do it cleaner?
        #self.new_books = self.__get_new_books()
        self.new_books_names = self.__get_new_books_names()

    def __get_new_books(self) -> list:
        new_books = []
        for book in self.current_books:
            if book not in self.previous_books:
                new_books.append(book)
        #return self.new_books = new_books
        return new_books

    def __get_new_books_names(self) -> list:
        new_books_names = []
        for book in self.new_books:
            new_books_names.append(os.path.basename(book))
        return new_books_names

    def __process_book_list(self, booklist: list) -> list:
        processed_books = []
        for book in booklist:
            processed_books.append(book.strip())
        stripped_list = [x for x in processed_books if x]
        return stripped_list

    def num_new_books(self) -> list:
        new_books_count = len(self.new_books)
        return new_books_count

    def cleanup(self) -> None:
        print("Writing new 'previous' file")
        kindle_utils.write_file(self.previous_file, self.current_books)
        print("Removing last 'previous' file")
        os.remove(self.current_file)
        print("Successfully cleaned up")

    @staticmethod
    def initial_setup() -> None:
        if not os.path.exists(C.FilePaths.WORKING_DIR):
            os.makedirs(C.FilePaths.WORKING_DIR)
        if not os.path.exists(C.FilePaths.CALIBRE_LIBRARY):
            raise Exception("Calibre library not found")
        if not os.path.exists(C.FilePaths.WORKING_DIR + C.FilePaths.PREVIOUS):
            kindle_utils.write_file(C.FilePaths.WORKING_DIR + C.FilePaths.PREVIOUS, [])
        print("Successfully initialized")
