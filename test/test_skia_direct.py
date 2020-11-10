from coldtype import *

#@skia_direct((1080, 300))
def test_exception(r, canvas):
    raise Exception("Intentional Exception!")

@skia_direct((1080, 300))
def test_draw(r, canvas):
    canvas.drawString(
        "hello",
        0,
        r.h,
        skia.Font(skia.Typeface("Times"), 150),
        skia.Paint(AntiAlias=True, Color=hsl(0.9, s=1).skia()))