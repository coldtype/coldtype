from random import random
from coldtype.drawbot import *
from coldtype.text.reader import StyledString, Style, Font

mistral = Font.Find("MistralD.otf")

save = "test/drawbot/hello.pdf"

with new_drawing("letter", save_to=save) as (idx, r):
    s = (StyledString("Hello", Style(mistral, 300))
        .pens()
        .f(hsl(random(), s=1))
        .align(r))
    
    print(s.attrs)

    db.fill(*hsl(random(), l=0.3))
    db.rect(*s.ambit())
    s.chain(dbdraw)