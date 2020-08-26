from coldtype import *
from drawBot import *

@drawbot_script(svg_preview=1)
def db_script_test(r):
    fill(1, random(), 0.5)
    oval(500, 500, 1000, 1000)

    fill(random(), random(), 0.5)
    fontSize(100)
    text("Hallo", (250, 250))