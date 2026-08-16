#!/usr/bin/env python3

import datetime
import glob
import os
import shutil
import time
from typing import Optional


def _unused_path(directory: str, filename: str) -> str:
    """Return a path that will not overwrite another exported book."""
    destination = os.path.join(directory, filename)
    if not os.path.exists(destination):
        return destination

    stem, extension = os.path.splitext(filename)
    copy_number = 2
    while True:
        destination = os.path.join(
            directory,
            f"{stem} ({copy_number}){extension}",
        )
        if not os.path.exists(destination):
            return destination
        copy_number += 1


def save_epubs(
    book_paths: list[str],
    destination_root: str,
    now: Optional[datetime.datetime] = None,
) -> str:
    """Copy books into a new, timestamped folder and return its path."""
    timestamp = (now or datetime.datetime.now()).strftime("%Y-%m-%d_%H%M%S")
    destination_root = os.path.expanduser(destination_root)
    os.makedirs(destination_root, exist_ok=True)

    base_folder = os.path.join(destination_root, f"Kindle Export {timestamp}")
    export_folder = base_folder
    copy_number = 2
    while os.path.exists(export_folder):
        export_folder = f"{base_folder} ({copy_number})"
        copy_number += 1
    os.makedirs(export_folder)

    for book_path in book_paths:
        destination = _unused_path(export_folder, os.path.basename(book_path))
        shutil.copy2(book_path, destination)

    return export_folder


def calibre_convert(landing_path: str) -> None:

    check_landing(landing_path)

    os.system("open -a Calibre")
    print("Waiting for Calibre to convert...")
    time.sleep(5)

    while(True):
        files = glob.glob(landing_path + "/*")
        length = len(files)
        if length == 0:
            print("converted all books")
            time.sleep(5) # In case of running jobs
            break
        elif length > 0:
            print("Waiting a bit longer...")
            time.sleep(5)
            continue
        else:
            raise Exception("check landing page")


    os.system("osascript -e 'quit app \"calibre\"'")

# Before opening calibre we should check if the landing directory is empty. If it is - no need to open. 
# Lets put this in a class. It can have check_landing and open_calibre methods

def check_landing(landing_path: str) -> int:
    files = glob.glob(landing_path + "/*")
    length = len(files)
    return length
