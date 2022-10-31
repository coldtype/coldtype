from coldtype import *

@skia_direct((500, 300))
def direct_to_canvas(r, canvas):
    canvas.drawString(
        "hello",
        10,
        r.h-10,
        skia.Font(skia.Typeface("Times New Roman"), 150),
        skia.Paint(AntiAlias=True, Color=hsl(0.9, s=1).skia()))