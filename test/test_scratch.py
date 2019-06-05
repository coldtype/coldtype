from db_preamble import *

from defcon import Glyph
from fontParts.fontshell import RGlyph
from fontTools.pens.recordingPen import RecordingPen, replayRecording
from booleanOperations.booleanGlyph import BooleanGlyph
from coldtype import StyledString


fp = os.path.expanduser("~/Library/Fonts")
faces = [
    [f"{fp}/ObviouslyVariable.ttf", dict(wdth=250, wght=200)],
    [f"{fp}/Cheee_Variable.ttf", dict(temp=250, grvt=200, yest=250)],
    [f"{fp}/VulfMonoLightItalicVariable.ttf", dict(wdth=500)],
]

def test_timing():
    txt = "Hello"
    font_size = 72
    for font_path, axes in faces:
        print("FONT", font_path)
        print("VARIATIONS", axes)
        t1 = time.process_time()
        hbs = Harfbuzz(font_path, upem=font_size)
        frames = hbs.setText(axes=axes, txt=txt)
        w1 = frames[-1].frame.point("SE").x
        l1 = time.process_time() - t1
        t2 = time.process_time()
        fs = FormattedString(txt, font=font_path, fontSize=font_size, fontVariations=axes)
        w2 = fs.size()[0]
        l2 = time.process_time() - t2
        print("DIFF: w={:.2f}, t={:.2f}".format(w1 - w2, l2 / l1))
        print("----------")

def test_styled_string(t, f, v):
    newPage(1500, 500)
    fill(1)
    rect(*Rect.page())
    translate(40, 100)
    ss = StyledString(t,
        fontFile=f,
        fontSize=300,
        features=dict(palt=True),
        variations=v,
        tracking=0)
    
    g = ss.asGlyph(removeOverlap=False)
    #drawBezierSkeleton(g, labels=False, handles=True, f=False, r=1, randomize=True)
    fill(0, 0.5, 1, 0.5)
    drawBezier(g)
    rp1 = RecordingPen()
    g.draw(rp1)
    if True:
        with savedState():
            for f in ss._frames:
                fill(None)
                strokeWidth(1)
                stroke(1, 0.5, 0, 0.5)
                rect(*f.frame.inset(0, 0))
    if False:
        with savedState():
            bp = BezierPath()
            ss.drawToPen(bp, useTTFont=True)
            fill(None)
            stroke(0, 0.5, 1)
            strokeWidth(0.5)
            drawPath(bp)
    if True: # also draw a coretext string?
        bp = BezierPath()
        bp.text(ss.formattedString(), (0, 0))
        #drawBezierSkeleton(bp, labels=False, handles=True, randomize=True, f=False, r=1)
        rp2 = RecordingPen()
        bp.drawToPen(rp2)
        
        if True:
            bg1 = BooleanGlyph()
            bg2 = BooleanGlyph()
            g.draw(bg1.getPen())
            bp.drawToPen(bg2.getPen())
            bg = bg1.xor(bg2)
            stroke(1, 0, 0.5)
            strokeWidth(2)
            fill(None)
            drawBezier(bg)
        
        if False:
            try:
                for i, (t1, pts1) in enumerate(rp1.value):
                    t2, pts2 = rp2.value[i]
                    if t1 != t2:
                        print("MOVE <<<<<<<<<<<<")
                        print("ft", t1)
                        print("ct", t2)
                        print(pts1)
                        print(pts2)
                    elif pts1 != pts2:
                        print("PTS <<<<<<<<<<<<")
                        print("ft", t1)
                        print("ct", t2)
                        print(pts1)
                        print(pts2)
            except:
                pass


#t = "ٱلْـحَـمْـدُ للهِ‎"
t = "الحمراء"
#t = "رَقَمِيّ"
#t = "ن"
f = "~/Type/fonts/fonts/BrandoArabic-Black.otf"
#f = "~/Type/fonts/fonts/29LTAzal-Display.ttf"
test_styled_string(t, f, dict())

t = "Beastly"
f = f"{fp}/Beastly-72Point.otf"
#f = f"{fp}/SourceSerifPro-Black.ttf"
#f = f"{fp}/framboisier-bolditalic.ttf"
test_styled_string(t, f, dict())

t = "PROGRAM"
f = f"{fp}/ObviouslyVariable.ttf"
v = dict(wdth=151, wght=151)
f = f"{fp}/RoslindaleVariableItalicBeta-VF.ttf"
v = dict(ital=0.6, slnt=-8)
#f = f"{fp}/BildVariableV2-VF.ttf"
#v = dict(wdth=80)
test_styled_string(t, f, v)

t = "フィルター"
f = "~/Library/Application Support/Adobe/CoreSync/plugins/livetype/.r/.35716.otf"
#f = "/Users/robstenson/Type/fonts/fonts/PixelMplus12-Bold.ttf"
#test_styled_string(t, f, dict())

t = "你好"
#f = "/Library/Fonts/NISC18030.ttf"
#f = "~/Type/fonts/fonts/unifont-10.0.07.ttf"
f = "~/Type/fonts/fonts/Robrush.otf"
test_styled_string(t, f, dict())

t = "Default"
f = "~/Library/Fonts/FormaDJRTextItalic.otf"
#f = "~/Goodhertz/plugin-builder/juce/assets/FormaDJRText-Italic.ttf"
test_styled_string(t, f, dict())

if True:
    newPage()
    t = "Yessir"
    f = "~/Library/Fonts/FormaDJRTextItalic.otf"
    #f = "~/Goodhertz/plugin-builder/juce/assets/FormaDJRText-Italic.ttf"
    #f = "~/Goodhertz/plugin-builder/juce/assets/FormaGHZText-Medium.ttf"
    ss = StyledString(t, fontFile=f, fontSize=300)
    ss.place(Rect.page())
    grid(Rect.page(), color=(1, 0, 0.5, 0.25))
    fill(0, 0.5, 1)
    ss.drawBotDraw()
    