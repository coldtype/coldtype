from coldtype.animation import *

def render(f):
    column = f.a.r.take(700, "centerx")
    modern = StyledString("MODERN", Style("≈/ObviouslyVariable.ttf", 95, wdth=1, wght=0.25, ro=1)).fit(column.take(0.33, "minx"))
    jazz = StyledString("JAZZ", Style("≈/BancoPro.otf", 100))
    quartet = StyledString("QUARTET", Style("≈/OhnoFatfaceVariable.ttf", 110, wdth=1, opsz=0.5)).fit(column.take(0.33, "minx"))
    # TODO concept of a spacer/furniture?
    dps = DATPenSet().extend([
        modern.pens(),
        DATPen().rect(Rect(50, 50)),
        jazz.pens(),
        DATPen().rect(Rect(50, 50)),
        quartet.pens()
        ])
    dps.distribute()
    dps.align(column)
    #lockup = Lockup([modern, jazz, quartet])
    #dps = Slug("modern jazz quartet".upper(), Style("≈/BancoPro.otf", 250, wdth=1, opsz=0.75, ro=1)).pens().align(column).f(1)
    #dps.scaleToRect(column)
    #dps.trackToRect(column)
    #dps[1].trackToRect(column.take(0.33, "centerx"))
    #dps[0].trackToRect(column.take(0.3, "minx"))
    return [
        DATPen().rect(column).f(1, 0, 0.5, 0.25),
        DATPen().rect(column.take(0.33, "centerx")).f(1, 0, 0.5, 0.25),
        #lockup.pens().align(column).trackToRect(column).f(1)
        dps.reversePens().f(1).interleave(lambda p: p.s(0).sw(10))
    ]

timeline = Timeline(100, storyboard=[0])
animation = Animation(render, timeline=timeline)