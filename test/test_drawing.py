from coldtype.test import *
from coldtype.midi.controllers import LaunchControlXL


@renderable(bg=1, rstate=1)
def draw1(r, rs):
    nxl = LaunchControlXL(rs.midi)
    current = DATPen()
    strokes = DATPens()
    #wdth = nxl(20)*150
    overall_angle = nxl(40)*360-180
    overall_width = nxl(50)*200-100
    editing = rs.keylayer == Keylayer.Editing

    spine = [[], [], []]

    def draw_item(item, midi=None, add_to_spine=True):
        if item:
            p = item.position
            _nxl = LaunchControlXL(midi or item.midi)
            angle = _nxl(10)*-180-180
            wdth = _nxl(20)*150+5
            nib = _nxl(30)*20+1
            if not editing or True:
                angle += overall_angle
                wdth += overall_width
            to = DATPen()
            ps = [p.project(angle-180, wdth), p.project(angle, wdth)]
            to.line(ps).s(0).sw(nib)
            ps.insert(1, p)
            if add_to_spine:
                for i, p in enumerate(ps):
                    spine[i].append(p)
            return to

    for g in rs.input_history.strokes(lambda g: g.action == "down" and g.keylayer == Keylayer.Editing):
        #for item in g:
        strokes += draw_item(g[0])
    
    if editing:
        current.record(draw_item(rs.input_history.last(), rs.midi, add_to_spine=False))

    spines = DATPenSet()
    if spine[0]:
        spines = DATPenSet([
            DATPen().line(spine[0]).f(None).s(0).sw(5),
            DATPen().line(spine[1]).f(None).s(0).sw(10),
            DATPen().line(spine[2]).f(None).s(0).sw(5),
        ])

    return (DATPenSet([
        DATPen().rect(r.inset(5)).f(None).s(0).sw(5) if editing else DATPen().rect(r).f(1),
        current.s(0.5).sw(10),
        spines,
        (DATPens([strokes])
            .s(hsl(0.7) if editing else 0)
            .color_phototype(r, blur=5, cut=190)
            .img_opacity(0.5 if editing else 1))]))