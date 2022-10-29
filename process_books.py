#!/usr/bin/env python3

import os
import glob
import constants as C
import time

os.system("open -a Calibre")

while(True):
    files = glob.glob(C.FilePaths.CALIBRE_LANDING + "/*")
    length = len(files)
    if length == 0:
        break
    elif length > 0:
        time.sleep(5)
        continue
    else:
        raise Exception("check landing page")


os.system("osascript -e 'quit app \"calibre\"'")
