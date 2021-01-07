from coldtype.test import *
from coldtype.midi.controllers import LaunchControlXL

scratch = raw_ufo("~/Type/ex1/scratch/scratch.ufo")


@renderable(bg=1, rstate=1, watch=[scratch.path])
def draw1(r, rs):
    nxl = LaunchControlXL(rs.midi)
    current = DATPen()
    strokes = DATPens()
    #wdth = nxl(20)*150
    overall_angle = nxl(40)*360-180
    overall_width = nxl(50)*200-100
    editing = rs.keylayer == Keylayer.Editing

    def draw_item(item, midi=None):
        if item:
            p = item.position
            _nxl = LaunchControlXL(midi or item.midi)
            angle = _nxl(10)*-90-90
            wdth = _nxl(20)*150+5
            nib = _nxl(30)*20+1
            if not editing or True:
                angle += overall_angle
                wdth += overall_width
            to = DATPen()
            to.line([p.project(angle-180, wdth), p.project(angle, wdth)]).s(0).sw(nib)
            return to

    for g in rs.input_history.strokes(lambda g: g.action == "down" and g.keylayer == Keylayer.Editing and len(g) > 1):
        for item in g:
            strokes += draw_item(item)
    
    if editing:
        current.record(draw_item(rs.input_history.last(), rs.midi))
    
    dp = DATPen().glyph(scratch["s.2"]).align(r).scale(1.3)
    bbp = dp.to_cbp()[0]
    bbp.addExtremes()
    dp2 = DATPen.from_cbp([bbp])
    dp2.value = dp2.value[0:]
    from pprint import pprint
    pprint(dp2.value)

    return dp2.skeleton()
    return dp2.f(None).s(0).sw(5)

    return (DATPenSet([
        DATPen().rect(r.inset(5)).f(None).s(0).sw(5) if editing else DATPen().rect(r).f(1),
        current.s(0.5).sw(10),
        (DATPens([strokes])
            .s(hsl(0.7) if editing else 0)
            .color_phototype(r, blur=5, cut=190)
            .img_opacity(0.5 if editing else 1))]))