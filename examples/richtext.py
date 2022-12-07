from coldtype import *
from coldtype.text.richtext import RichText

def styler(txt, styles):
    if "i" in styles:
        return txt, Style(Font.RecursiveMono(), 22)
    elif "h" in styles:
        return txt, Style(Font.MutatorSans(), 72, wght=1)
    return txt, Style(Font.RecursiveMono(), 42)

@renderable((1080, 200))
def highlight(r):
    return (RichText(r, "HELLO[h] World", styler)
        .xalign(r)
        .align(r, ty=1)
        .scale(1.5)
        .insert(0, lambda ps: P()
            .rect(ps[0][-1]
                .ambit(tx=1, ty=1)
                .inset(-10))
            .fssw(-1, hsl(0.7, a=0.3), 10)))

txt = """H [h]

Text
a smaller line [i]"""

@renderable((1080, 540))
def plainish(r):
    return (RichText(r, txt, styler, spacer="¶")
        .xalign(r)
        .align(r)
        .scale(2, tx=1)
        .f(0)
        .removeSpacers())

txt2 = """
Hello, [a]
WORLD
"""

@renderable((1080, 400))
def key_lookup_style(r):
    return (RichText(
        r, txt2, {
            "a": Style(Font.RecursiveMono(), 200, fill=hsl(0.9)),
            "default": Style(Font.MuSan(), 150, fill=bw(0), wght=1)})
        .xalign(r)
        .reversePens()
        .lead(20)
        .align(r))