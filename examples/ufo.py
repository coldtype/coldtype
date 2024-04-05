from coldtype import *

fs = Font.Find(r"Cold.*_CompressedBlackItalic\.ufo", "assets")

@renderable((1080, 540))
def scratch(r):
    return StSt("CDELOPTY", fs, 300).align(r)
