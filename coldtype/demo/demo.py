from coldtype import *

@animation((800, 200), timeline=60, bg=1)
def demo(f):
    return (Glyphwise("COLDTYPE", lambda x:
        Style(Font.ColdtypeObviously(), 150
            , wdth=f.adj(-x.i*15).e("eeo", 1)))
        .align(f.a.r)
        .f(0))