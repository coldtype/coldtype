from coldtype import *

@renderable()
def error(r):
    raise Exception("Exception!")