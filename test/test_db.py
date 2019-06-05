from db_preamble import *
from random import randint

nostra = "~/Library/Fonts/Nostrav0.9-Stream.otf"
forma = "~/Library/Fonts/FormaDJRBannerExtraLightItalic.otf"
rainer = "~/Library/Fonts/Rainer_v0.2-Bold.otf"
gig = "~/Library/Fonts/GigV0.2-Regular.otf"
bild = "~/Library/Fonts/BildVariableV2-VF.ttf"

in_db = True
try:
    newPage(1000, 1000)
except:
    from drawBot import *
    in_db = False

fill(0)
rect(*Rect.page())

ssv = coldtype.StyledString("VECTORIZED", fontFile=forma, fontSize=200, rect=Rect.page())

ss0 = coldtype.StyledString("Freetype".upper(), fontFile=bild, fontSize=400, rect=Rect.page().offset(0, 100).inset(-20, 0))

ss1 = coldtype.StyledString("Harfbuzz Shaping",
    fontFile="~/Type/fonts/fonts/ObviouslyVariable.ttf",
    fontSize=300,
    tracking=0,
    features=dict(ss01=False),
    variations=(dict(wght=0.5, slnt=1, wdth=1, scale=True)),
    rect=Rect.page().offset(0, -100))

ss2 = coldtype.StyledString("&", fontFile=nostra, fontSize=500, rect=Rect.page())

with savedState():
    fill(1, 1, 0)
    translate(3, 0)
    ssv.drawBotDraw()
fill(1)
ss0.drawBotDraw()
fill(0, 0.5, 1)
ss1.drawBotDraw()
fill(1, 0, 0.5)
ss2.drawBotDraw()

fill(0)
ssv.drawBotDraw()

if not in_db:
    print("Not in drawBot")
    