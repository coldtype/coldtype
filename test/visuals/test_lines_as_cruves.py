from coldtype.test import *

fnt = Font.Cacheable("assets/ColdtypeObviously_CompressedBlackItalic.otf")

def lines_to_curves(pen):
    # is the closePath case unnecessary if preceded by fully_close_path?
    mvpt = None
    lstpt = None
    for idx, (mv, pts) in enumerate(pen.value):
        if mv == "moveTo":
            if mvpt:
                pass # do something?
            mvpt = pts[0]
            lstpt = pts[0]
        elif mv == "lineTo":
            line = Line(lstpt, pts[0])
            pen.value[idx] = ("curveTo",
                (line.t(0.25), line.t(0.75), line.end))
            lstpt = pts[-1]
        elif mv == "curveTo":
            lstpt = pts[-1]
        elif mv == "closePath":
            if lstpt != mvpt:
                line = Line(lstpt, mvpt)
                pen.value[idx] = ("curveTo",
                    (line.t(0.25), line.t(0.75), line.end))

#@animation(timeline=60)
def test_lines_to_curves_simple(f):
    #rpo = DP
    r = f.a.r
    rpo = DP().oval(r.inset(300))
    rpo.add_pt_t(0, 0.5)
    rp = DP(r.inset(250))#.record(rpi.reverse())
    rp.add_pt_t(0, 0.5)
    rp.ch(lines_to_curves)
    rpi = rp.interpolate(f.e(1), rpo)
    return DPS([
        rpi.f(hsl(0.8, 1, 0.8)),
        rpi.copy().f(None).s(0).sw(1),
        rpi.copy().skeleton(scale=3).f(hsl(0.6, 1))
    ])

@animation(timeline=60)
def test_lines_to_curves_complex(f):
    dpa = StSt("Y", fnt, 1000).align(f.a.r)[0].fully_close_path()
    dpb = StSt("C", fnt, 1000).align(f.a.r)[0].fully_close_path()
    
    ml = max([len(dpa.value), len(dpb.value)])
    #print(">", ml)
    for dp in [dpa, dpb]:
        while len(dp.value) < ml:
            #print(dp.glyphName, len(dp.value))
            dp.add_pt_t(0, 0.5)
    
    dpa.ch(lines_to_curves).pvl()
    dpb.ch(lines_to_curves).pvl()
    #pprint(dpa.value[-1])
    #pprint(dpb.value[-1])
    return DPS([
        dpa.copy().skeleton(scale=1).translate(-300, 0),
        dpb.copy().skeleton(scale=1).translate(300, 0),
        dpa.interpolate(f.e(1), dpb).f(hsl(0.3))
    ])