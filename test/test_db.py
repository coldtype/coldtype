import os
import sys
import importlib
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.realpath(dirname + "/.."))

import coldtype
importlib.reload(coldtype)

from furniture.geometry import Rect
from random import randint

nostra = "~/Library/Fonts/Nostrav0.9-Stream.otf"
forma = "~/Library/Fonts/FormaDJRTextRegular.otf"
rainer = "~/Library/Fonts/Rainer_v0.2-Bold.otf"
gig = "~/Library/Fonts/GigV0.2-Regular.otf"
bild = "~/Library/Fonts/BildVariableV2-VF.ttf"

newPage(1000, 1000)
fill(0)
rect(*Rect.page())

ss0 = coldtype.StyledString("Freetype".upper(), fontFile=bild, fontSize=400, rect=Rect.page().offset(0, 100).inset(-20, 0))

ss1 = coldtype.StyledString("Harfbuzz Shaping",
    fontFile="~/Type/fonts/fonts/ObviouslyVariable.ttf",
    fontSize=300,
    tracking=0,
    features=dict(ss01=True),
    variations=(dict(wght=1, slnt=1, wdth=1, scale=True)),
    rect=Rect.page().offset(0, -100))

ss2 = coldtype.StyledString("&", fontFile=nostra, fontSize=500, rect=Rect.page())

fill(1)
ss0.drawBotDraw()
fill(0, 0.5, 1)
ss1.drawBotDraw()
fill(1, 0, 0.5)
ss2.drawBotDraw()