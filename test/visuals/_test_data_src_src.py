from pathlib import Path
from random import random
import datetime

INTERVAL = 1

TXT = Path(__file__).parent / "_test_data_src_src.txt"

def run():
    now = datetime.datetime.now()
    TXT.write_text("{:04d}/{:04d}".format(now.minute, now.second))