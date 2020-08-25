from coldtype import *
from random import random
import drawBot as db

@drawbot_script(svg_preview=0)
def db_script_test(r):
    db.fill(1, random(), 0.5)
    db.oval(500, 500, 1000, 1000)

    db.fill(random(), random(), 0.5)
    db.fontSize(100)
    db.text("Hallo", (250, 250))