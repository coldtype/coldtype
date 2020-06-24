from drawBot import *
from random import random

fill(1, random(), 0.5)
oval(0, 0, 1000, 1000)

fill(random(), 1, 0.5)
fontSize(100)
text("Hallo", (250, 250))