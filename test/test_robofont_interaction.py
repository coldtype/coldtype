from coldtype import *
from fontTools.pens.recordingPen import RecordingPen
from coldtype.midi.controllers import LaunchControlXL
import json

datafile = Path("~/robofont-coldtype.json").expanduser()
tl = Timeline(50)

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
        .vl(data["layers"]["narrowester"]["value"]))
    dp_md = (DATPen()
        .vl(data["layers"]["background"]["value"]))

    #return ,
    #    f.a.progress(f.i, loops=1, easefn="eeio").e)

    return (DATPen.Interpolate(
        [dp_fg, dp_md, dp_bg],
        f.a.progress(f.i, loops=1, easefn="eeio").e)
        .f(1)
        .scale(0.7).translate(-50, 100)
        #.translate(300, 200)
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