from coldtype import *

at = AsciiTimeline(1, 30, """
                                                                                        <
            [.big        ]
*Oh,        hello.        • 
                            *This       ≈some           ≈t  +e  +x  +t +.            •  
                                  is            timed
""")

def styler(c):
    if "big" in c.styles:
        return c.text.upper(), Style(Font.MutatorSans(), 100, wght=1)
    else:
        return c.text, Style(Font.RecursiveMono(), 100)

@animation((1080, 540), tl=at, offset=0)
def timedWords(f):
    return (f.t.words.currentGroup()
        .pens(f, styler)
        #.printh()
        .cond(f.t.words.styles.ki("big").on(),
            lambda p: p.f(hsl(0.9)))
        .lead(30)
        .xalign(f.a.r)
        .align(f.a.r)
        .removeFutures())

# RENDERABLES = [
#     timedWords.viewOffset(30)
# ]