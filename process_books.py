#!/usr/bin/env python3

import os
import glob
import constants as C
import time

os.system("open -a Calibre")
print("Waiting for Calibre to convert...")
time.sleep(5)

while(True):
    files = glob.glob(C.FilePaths.CALIBRE_LANDING + "/*")
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
