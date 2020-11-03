from coldtype import *
from defcon import Font

curves = Font(sibling(__file__, "media/digestivecurves.ufo"))
df = "~/Type/fonts/fonts/_wdths/DigestiveVariable.ttf"

def ds(e1, e2):
    # 128, -50 on size
    return StyledString("Digestive", Style(df, 186-0*e2, fill=1, tu=0+0*e1, wdth=e1, ro=1, bs=0*(1-e2))).pens()

def render_snake(f, fi):
    a:Animation = f.a
    at1 = a.progress(fi, loops=10, easefn="ceio")
    at2 = a.progress(fi, loops=10, easefn="ceio")

    track = DATPen()
    curves["path1"].draw(track)
    track.scaleToRect(f.a.r).align(f.a.r, th=1, tv=1).translate(0, -20).f(None).s(1).sw(1).scale(1.15)
    t = track.copy()
    track.repeat(3)#.scale(1.15)
    dps:DATPenSet = ds(at1.e, at2.e)

    minw = ds(0, 0).getFrame(th=1).point("SE").x
    maxw = ds(1, 1).getFrame(th=1).point("SE").x

    if at1.loop_phase == 1:
        offset = maxw-dps.getFrame(th=1).point("SE").x
    else:
        offset = 0
    
    offset += math.floor(at1.loop/2)*(maxw-minw)

    dps.distributeOnPath(track, offset=offset).reversePens()

    return t, dps

t = Timeline(350, storyboard=[0, 20, 349])

@animation(rect=(1920,500), timeline=t)
def render(f):
    test = False
    if test:
        _, zero = render_snake(f, 0)
    track, now = render_snake(f, f.i)
    bg = hsl(0, l=0.97)
    return DATPenSet([
        DATPen().rect(f.a.r).f(bg),
        DATPenSet([
            zero.f(hsl(0.1, l=0.8)) if test else DATPen(),
            track.f(None).s(hsl(0.65, l=0.9)).sw(15).translate(0, -8),
            now.f(hsl(0.9, l=0.6, s=0.7))#.understroke(s=bg, sw=5),
            #track.copy().translate(0, 180),
        ]).translate(0, -30)
    ])