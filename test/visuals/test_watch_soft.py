from coldtype.test import *

print("FULL RELOAD")

rec = Font.Cacheable("assets/RecMono-CasualItalic.ttf")
generic_txt = __sibling__("test_watch_scratch.txt")

@renderable((1000, 300), watch_soft=[generic_txt])
def stub(r):
    print("RENDER CALL")
    return (DATText(generic_txt.read_text(),
        Style(rec, 40, fill=hsl(0.7, 1)),
        r.inset(100)))