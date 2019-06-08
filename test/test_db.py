from db_preamble import *
from random import randint

nostra = "~/Library/Fonts/Nostrav0.9-Stream.otf"
forma = "~/Library/Fonts/FormaDJRBannerExtraLightItalic.otf"
bild = "~/Library/Fonts/BildVariableV2-VF.ttf"

in_db = True
try:
    newPage(1000, 1000)
except:
    from drawBot import *
    in_db = False

fill(0)
rect(*Rect.page())

ss0 = coldtype.StyledString("Freetype".upper(), fontFile=bild, fontSize=400, rect=Rect.page().offset(0, 90).inset(-20, 0))

ss1 = coldtype.StyledString("Harfbuzz Shaping",
    fontFile="~/Type/fonts/fonts/ObviouslyVariable.ttf",
    fontSize=300,
    tracking=0,
    features=dict(ss01=False),
    variations=(dict(wght=0.75, slnt=1, wdth=1, scale=True)),
    rect=Rect.page().offset(0, -90))

ss2 = coldtype.StyledString("&", fontFile=nostra, fontSize=500, rect=Rect.page())

fill(1, 1, 0)
ss2.drawBotDraw()
stroke(1)
strokeWidth(4)
fill(None)
ss0.drawBotDraw(removeOverlap=True)
stroke(None)
fill(0, 0.5, 1)
ss1.drawBotDraw()
fill(1, 0, 0.5)
translate(4, 4)
ss2.drawBotDraw()

saveImage("~/Desktop/coldtype.pdf")