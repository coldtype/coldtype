import sys
from pathlib import Path
sys.path.insert(0, str(Path("~/Goodhertz/coldtype").expanduser()))

from coldtype.drawbot import *

with new_page() as r:
    mistral = Font.Find("MistralD.otf")

    s = (StSt("Hello", mistral, 300)
        .f(hsl(0.3, s=1))
        .align(r))

    with db.savedState():
        db.fill(None)
        db.stroke(0)
        db.strokeWidth(2)
        db.rect(*s.ambit())

    s.chain(dbdraw)

    circle = (P()
        .oval(r.inset(200))
        .reverse()
        .rotate(0))
    s2 = (s
        .copy()
        .zero_translate()
        .distribute_on_path(circle)
        .chain(dbdraw))

    print(s.f())
    print(s2.f())

    db.fontSize(24)
    db.text("Mistral", s.ambit().inset(0, -50).ps, align="center")