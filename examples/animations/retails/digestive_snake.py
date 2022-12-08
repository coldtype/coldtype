from coldtype import *

r = Rect(1920, 500)

track = (P()
    .vl([
        ('moveTo', ((-342, 68),)),
        ('curveTo', ((-162, 68), (-108, 217), (140, 217.0))),
        ('curveTo', ((381, 217), (454, 98), (639, 98))),
        ('curveTo', ((843, 98), (925, 217), (1106, 217))),
        ('curveTo', ((1322, 217), (1426, 68.0), (1656, 68))),
        ('endPath', ())])
    .scale(0.25)
    .fssw(None, 1, 1)
    .repeat(3)
    .align(r)
    .translate(0, -20))

def ds(e1):
    # 52.98 is a magic number for this string
    # uncomment the 119-rendered static at the bottom
    # to calibrate for a different string/font
    return StSt("Digestive", "Digestive", 52.98, wdth=e1, ro=1)

minw = ds(0).ambit(tx=1).point("SE").x
maxw = ds(1).ambit(tx=1).point("SE").x

def render_snake(f):
    e, l = f.e("eeio", 2, loop_info=1)
    dps = ds(e)

    offset = 0
    if l in [1, 3]:
        offset = maxw - dps.ambit(tx=1).point("SE").x
    
    offset += math.floor(l/2)*(maxw-minw)
    dps.distributeOnPath(track, offset=offset)
    return dps

@animation(rect=(1920,500), timeline=120, bg=hsl(0, l=0.97))
def render(f):
    now = render_snake(f)
    return (P(
            P(f.a.r).scale(0.3).fssw(-1, -1, 2),
            P(f.a.r).scale(0.25).fssw(-1, -1, 2),
            (track.copy()
                .fssw(None, hsl(0.65, l=0.9), 15)
                .translate(0, -8)),
            #render_snake(Frame(119, f.a)).f(0),
            now.f(hsl(0.9, l=0.6, s=0.7)))
        .translate(0, -30)
        .scale(4.1)
        .align(f.a.r))