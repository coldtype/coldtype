from coldtype.animation import *

def render(f):
    at = f.a.progress(f.i, loops=1, easefn="eeio")
    c1, c2 = f.a.r.inset(0, 50).divide(0.15+at.e*0.7, "maxy") #= f.a.r.take(750-550*at.e, "maxy").take(350+at.e*(f.a.r.w-350), "centerx")
    c1 = c1.inset(20, 5)
    c2 = c2.inset(20, 5)
    #c1 = c1.take((1-at.e)*0.75+0.25, "maxy") #.take(350+at.e*(f.a.r.w-350), "centerx")
    #c2 = c2.take((at.e)*0.75+0.25, "miny") #c2.take(350+(1-at.e)*(f.a.r.w-350), "centerx")
    s = Style("≈/OhnoFatfaceVariable.ttf", fitHeight=c1.h, t=-25, wdth=1, wght=1, ro=1, opsz=at.e)
    modern = StyledString("STACKED&", s).fit(c1)
    justified = StyledString("JUSTIFIED", Style("≈/OhnoFatfaceVariable.ttf", fitHeight=c2.h, t=-25, wdth=1, wght=1, opsz=1-at.e, ro=1, fill=(0, 0, 1))).fit(c2)
    #jazz = StyledString("JAZZ", Style("≈/BancoPro.otf", 100))
    #quartet = StyledString("QUARTET", Style("≈/OhnoFatfaceVariable.ttf", 110, wdth=1, opsz=0.5, ro=1)).fit(column.take(0.33, "minx"))
    # TODO concept of a spacer/furniture?
    dps = DATPenSet().extend([
        modern.pens(),
        #DATPen().addFrame(Rect(50, 50)),
        #jazz.pens(),
        #DATPen().addFrame(Rect(50, 50)),
        #quartet.pens()
        ])
    dps.align(c1)
    #lockup = Lockup([modern, jazz, quartet])
    #dps = Slug("modern jazz quartet".upper(), Style("≈/BancoPro.otf", 250, wdth=1, opsz=0.75, ro=1)).pens().align(column).f(1)
    dps[0].trackToRect(c1, pullToEdges=1)
    m = dps[0][0].copy().pen()

    dps2 = justified.pens().align(c2).trackToRect(c2, pullToEdges=1)
    #dps[1].trackToRect(column.take(0.33, "centerx"))
    #dps[0].trackToRect(column.take(0.3, "minx"))
    dps.f(0, 1, 0)
    #dps = dps.flatten().mmap(lambda idx, p: p.f(0, 1, 0) if idx%2 == 0 else p.f(0, 0, 1))#.pen().f(1)
    #dps2.mmap(lambda idx, p: p.f(0, 1, 0) if idx%2 == 1 else p.f(0, 0, 1))#.pen().f(1)
    return [
        #dps,
        #dps.copy().removeOverlap().f(0, 1, 0).s(1, 0, 0).sw(5),
        #DATPen().rect(column.take(0.33, "centerx")).f(1, 0, 0.5, 0.25),
        #lockup.pens().align(column).trackToRect(column).f(1)
        dps.flatten().reversePens().interleave(lambda p: p.s(1, 0, 0).sw(12)),
        dps2.reversePens().interleave(lambda p: p.s(1, 0, 0).sw(12)),
        #DATPen().rect(column).f(1, 0, 0.5, 0.75),
        #DATPen().rect(m.getFrame(th=0)).f(0, 1, 1, 0.75),
        #m
    ]

timeline = Timeline(100, storyboard=[0, 25, 50])
animation = Animation(render, timeline=timeline)