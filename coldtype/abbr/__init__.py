from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.text.reader import StyledString, Style
from coldtype.abbr.dp_auto_abbrev import *
from coldtype.abbr.inst import Inst
from coldtype.color import *


def pen():
    return Inst("pen")

def pens():
    return Inst("pens")

def wrap():
    return Inst("wrap")

def fsw(f=None, s=None, sw=0):
    return Inst(
        "subinstructions",
        fill(f),
        stroke(s) if s else None,
        strokeWidth(sw) if sw > 0 else None)

def text(text):
    return Inst("text", text)

def font(fnt):
    return Inst("font", fnt)

def style(fontSize, **properties): # properties here could have some autocomplete?
    return Inst("style", {**dict(fontSize=fontSize), **properties})

G = Gradient