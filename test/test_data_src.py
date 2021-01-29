from coldtype.test import *

# should be run as coldtype test/test_data_src.py -sc test/_test_data_src_src.py

TXT:Path = __sibling__("_test_data_src_src.txt")

r = (5140, 2844)
r = (700, 300)

@renderable(r, watch_soft=[TXT])
def stub(r):
    return (DATPens([
        (DATPen()
            .rect(r.inset(15))
            .f(hsl(0.75, 1, 0.3))),
        (StyledString(TXT.read_text(),
            Style(recmono, 100))
            .pen()
            .f(hsl(0.17, 1, 0.8))
            .align(r, th=0))])
        .color_phototype(r, blur=7, cut=170, cutw=3))
