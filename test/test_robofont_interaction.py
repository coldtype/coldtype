from coldtype import *
from fontTools.pens.recordingPen import RecordingPen
from coldtype.midi.controllers import LaunchControlXL
import json

datafile = Path("~/robofont-coldtype.json").expanduser()
tl = Timeline(50)

@animation((1500, 1000), timeline=tl, watch_soft=[datafile], rstate=1, bg=1)
def stub(f, rs):
    r = f.a.r
    nxl = LaunchControlXL(rs.midi)
    #os.system(f"robofont -p {stub.codepath}")
    dp = DATPen()
    try:
        data = json.loads(datafile.read_text())
    except json.JSONDecodeError:
        pass

    ls = data["layers"]
    def get_l(l):
        if g := ls.get(l):
            return DATPen().vl(g["value"])
        else:
            return DATPen()
    
    dp_fg = get_l("foreground")
    dp_bg = get_l("narrowester")
    #dp_md = get_l("background")

    return (
        DATPen.Interpolate([dp_fg, dp_bg], f.a.progress(f.i, loops=1, easefn="ceio").e)
        .f(1)
        .scale(0.5, center=r.point("SW"))
        .translate(50, 100)
        .phototype(r,
            blur=1+nxl(10)*30,
            cut=int(nxl(20)*250),
            cutw=int(nxl(30)*30),
            fill=bw(0)))

#if __name__ == "__main__":
#    cg = CurrentGlyph()
#    dp = RecordingPen()
#    cg.draw(dp)
#    print(dp.value)