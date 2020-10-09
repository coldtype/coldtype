from coldtype.pens.datpen import DATPen
from coldtype.pens.dp_auto_abbrev import *
from coldtype.color import *

def end():
    return ["end"]

def skip(*instructions):
    return ["skip"]

def build(*instructions):
    dp = DATPen()
    for fn, *args in instructions:
        if fn == "end":
            return dp
        elif fn == "skip":
            continue
        else:
            dp = getattr(dp, fn)(*args)
    return dp

ß = build