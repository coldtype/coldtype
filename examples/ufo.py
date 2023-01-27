from coldtype import *

fs = Font.Find(r"Cold.*_CompressedBlackItalic\.ufo", "assets")

@animation((1080, 540))
def scratch(f):
    return StSt("CDELOPTY", fs, 100).align(f.a.r)
