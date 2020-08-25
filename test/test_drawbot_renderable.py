from coldtype import *
from random import random
import drawBot as db

@drawbot_script()
def db_script_test(r):
    db.fill(1, random(), 0.5)
    db.oval(0, 0, 1000, 1000)

    db.fill(random(), 1, 0.5)
    db.fontSize(100)
    db.text("Hallo", (250, 250))