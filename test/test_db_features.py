from db_preamble import *
from coldtype import StyledString
from fontParts.fontshell import RGlyph

def test_styled_fitting():
    newPage(1000, 1000)
    fill(0)
    rect(*Rect.page())
    ss = StyledString("COMPRESSION".upper(),
        fontFile=f"~/Library/Fonts/ObviouslyVariable.ttf",
        fontSize=50,
        variations=dict(wdth=1, wght=0, scale=True),
        features=dict(ss01=False),
        tracking=30)
    count = 22
    translate(0, 6)
    for x in range(count):
        w = 100+(pow(1-x/count, 2))*900
        if False:
            print("BEFORE wdth", ss.variations.get("wdth"),
                "width", ss.width(), ss.tracking)
        ss.fit(w)
        if False:
            print("AFTER wdth", ss.variations.get("wdth"),
                "width", ss.width(), ss.tracking, ss.tries)
        fill(random(), 0.5, 1, 1)
        fill(1)
        ss.drawBotDraw(removeOverlap=False)
        translate(30, ss.fontSize-5)
        if False: # also draw a coretext string?
            fill(random(), 0.5, 1, 0.15)
            bp = BezierPath()
            bp.text(ss.formattedString(), (0, 0))
            bp.translate(4, -74)
            drawPath(bp)

def test_curve_fitting():
    newPage(1000, 1000)
    g = RGlyph()
    gp = g.getPen()
    gp.moveTo((100, 100))
    gp.curveTo((540, 250), (430, 750), (900, 900))
    gp.endPath()
    bp = BezierPath()
    g.draw(bp)
    fill(None)
    stroke(1, 0, 0.5, 0.1)
    strokeWidth(10)
    drawPath(bp)
    ss = StyledString("hello world, what’s happening?",
        fontFile="~/Library/Fonts/NikolaiV0.2-BoldCondensed.otf",
        fontSize=100,
        tracking=7)
    ss.addPath(g)
    fill(0, 0.5, 1)
    stroke(None)
    ss.drawBotDraw()

def test_box_fitting():
    import cProfile
    if False:
        p = cProfile.Profile()
        p.enable()
    else:
        p = None
    
    newPage(1000, 1000)
    
    grid(Rect.page(), color=(1, 0, 0.5, 0.35))
    ss = StyledString("YES — NO".upper(),
        fontFile="~/Library/Fonts/ObviouslyVariable.ttf",
        fontSize=353,
        tracking=0,
        space=120,
        features=dict(ss01=False),
        increments=dict(wdth=1),
        variations=dict(wdth=1,wght=1,scale=True),
        align="CC",
        )
    
    r = Rect.page().take(900, "centerx").take(600, "centery")
    stroke(0, 0.5)
    strokeWidth(10)
    fill(None)
    rect(*r)
    strokeWidth(1)
    fill(0, 0.5, 1, 0.95)
    ss.place(r.inset(0, 0))
    ss.drawBotDraw(removeOverlap=True)
    
    if False:
        bp = BezierPath()
        bp.text(ss.formattedString(), (0, 0))
        bp.removeOverlap()
        drawPath(bp)
    
    if p:
        p.disable()
        p.print_stats(sort='time')

def test_cff_var():
    newPage()
    ss = StyledString("Hello, world",
        #fontFile="~/Type/fonts/fonts/AdobeBlack2VF.otf",
        fontFile="~/Type/fonts/fonts/AdobeVFPrototype.otf",
        fontSize=150,
        variations=dict(wght=0, scale=True),
        )
    ss.place(Rect.page())
    fill(0)
    ss.drawBotDraw()

test_styled_fitting()
test_curve_fitting()
test_box_fitting()
test_cff_var()