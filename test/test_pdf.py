from coldtype.animation import *

def filename(f):
    return "test_pdf"

def render(f):
    return StyledString("This is a pdf".upper(), Style("ç/MutatorSans.ttf", 72, wght=0.2, fill=0)).pen().align(f.a.r)

animation = Animation(render, "Letter", bg=1, format="pdf", filename=filename)