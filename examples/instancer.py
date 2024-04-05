from coldtype import *

src = Font.JetBrainsMono()

@renderable((1080, 540), bg=1)
def viewer(r):
    txt = "“Hello World” øö ĦĦĦ 123"
    textface = StyledString(txt, Style(src, 62, wght=1, ss02=1))
    instance = textface.instance(ººsiblingºº("JBMono-custom.otf"), freeze=1, freeze_suffix="Custom")
    subsetted = instance.subset(ººsiblingºº("JBMono-custom-subset.woff2"))

    return (P(
        textface.pens(),
        StSt(txt, instance, 62),
        StSt(txt, subsetted, 62),
        )
        .f(0)
        .stack(10)
        .align(r))