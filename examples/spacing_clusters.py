from coldtype import *

# https://brill.com/page/BrillFontDownloads/Download-The-Brill-Typeface

font = Font.Find("Brill-Bold")

@renderable((540, 540), bg=0)
def spaced_clusters(r:Rect):
    txt = (StSt("Ae̞ø̞", font, 200, cluster=True, postTracking=200)
        .f(1)
        .align(r, tx=1))
    
    assert txt[-1].data("glyphName") == "oslash+uni031E"
    
    return (P(P(txt.copy().ambit()).f(hsl(0.9)), txt))
