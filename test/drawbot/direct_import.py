import sys
sys.path.insert(0, "/Users/robstenson/Goodhertz/coldtype")

from coldtype.drawbot import *

dp = (P()
    .define(r=Rect(100, 100), c=75)
    .gs("$r↗ ↘|$c|$r↓ ↙|$c|$r↖")
    .align(Rect(1000, 1000))
    .scale(5)
    .f(hsl(0.45))
    .ch(dbdraw))