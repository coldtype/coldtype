from coldtype import *
from fontTools.pens.recordingPen import RecordingPen
from coldtype.midi.controllers import LaunchControlXL
import json

datafile = Path("~/robofont-coldtype.json").expanduser()
tl = Timeline(30)

@animation(timeline=tl, watch_soft=[datafile], rstate=1, bg=1)
def stub(f, rs):
    r = f.a.r
    nxl = LaunchControlXL(rs.midi)
    #os.system(f"robofont -p {stub.codepath}")
    dp = DATPen()
    try:
        data = json.loads(datafile.read_text())
    except json.JSONDecodeError:
        pass
    dp_fg = (DATPen()
        .vl(data["layers"]["foreground"]["value"]))
    dp_bg = (DATPen()
        .vl(data["layers"]["background"]["value"]))
    return (dp_fg
        .interpolate(
            f.a.progress(f.i, loops=1, easefn="eeio").e,
            dp_bg)
        .f(1)
        .translate(300, 200)
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