from coldtype import *

curves = DefconFont(__sibling__("media/digestivecurves.ufo"))
df = Font.Find("Digestive")

r = Rect(1920, 500)
track = DATPen()
curves["path1"].draw(track)
track_path = track.scale(0.25)
track = (track_path.copy()
    .fssw(None, 1, 1)
    .repeat(3)
    .align(r)
    .translate(0, -20))

def ds(e1):
    # 52.998 is a magic number for this string
    return StSt("Digestive", df, 52.98, wdth=e1, ro=1)

minw = ds(0).getFrame(th=1).point("SE").x
maxw = ds(1).getFrame(th=1).point("SE").x

def render_snake(f, fi):
    at1 = f.a.progress(fi, loops=2, easefn="ceio")
    dps = ds(at1.e)

    if at1.loop_phase == 1:
        offset = maxw - dps.getFrame(th=1).point("SE").x
    else:
        offset = 0
    
    offset += math.floor(at1.loop/2)*(maxw-minw)
    dps.distributeOnPath(track, offset=offset)
    return dps

@animation(rect=(1920,500), timeline=120, bg=hsl(0, l=0.97))
def render(f):
    now = render_snake(f, f.i)
    return DPS([
        DP(f.a.r).scale(0.3).fssw(None, 0, 2),
        DP(f.a.r).scale(0.25).fssw(None, 0, 2),
        (track.copy()
            .fssw(None, hsl(0.65, l=0.9), 15)
            .translate(0, -8)),
        #render_snake(f, 119).f(0),
        now.f(hsl(0.9, l=0.6, s=0.7)),
    ]).translate(0, -30).scale(4.1).align(f.a.r)