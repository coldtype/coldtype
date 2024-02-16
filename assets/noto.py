#!/usr/bin/env python

from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

zipurl = "https://noto-website-2.storage.googleapis.com/pkgs/Noto-unhinted.zip"

print("> Downloading the noto fonts (this may take a while)...")

with urlopen(zipurl) as zipresp:
    with ZipFile(BytesIO(zipresp.read())) as zfile:
        zfile.extractall("assets/Noto-unhinted")

