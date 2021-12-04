from coldtype import *

at = AsciiTimeline(1, 30, """
                                                                        <
            big
*Oh,        hello.      
                    •                                               •
                        *This       ≈some           ≈t  +e +x  +t                 
                              is            timed
""")

def styler(c):
    if "big" in c.styles:
        return c.text.upper(), Style(Font.MutatorSans(), 100, wght=1)
    else:
        return c.text, Style(Font.RecursiveMono(), 100)

ct, styles = at.interpretClips(exclude=[1])

@animation((1080, 540), tl=at)
def timedWords(f):
    return (ct.currentGroup(f.i)
        .pens(f, styler, styles=styles)
        .lead(30)
        .xalign(f.a.r)
        .align(f.a.r)
        .removeFutures())