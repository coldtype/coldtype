from coldtype import *
from fontTools.pens.recordingPen import RecordingPen
from coldtype.midi.controllers import LaunchControlXL
import json

datafile = Path("~/robofont-coldtype.json").expanduser()

@renderable(watch_soft=[datafile], rstate=1, bg=0)
def stub(r, rs):
    nxl = LaunchControlXL(rs.midi)
    #os.system(f"robofont -p {stub.codepath}")
    dp = DATPen()
    data = json.loads(datafile.read_text())
    dp.value = data["layers"]["foreground"]["value"]
    dp.align(r).scale(1.75)
    return [
        #(dp.copy().f(None).s(hsl(0.7, a=0.25)).sw(10)),
        (dp.copy()
            .f(1)
            .phototype(r, blur=1+nxl(10)*30, cut=int(nxl(20)*250), cutw=int(nxl(30)*30), fill=bw(0)))]

#if __name__ == "__main__":
#    cg = CurrentGlyph()
#    dp = RecordingPen()
#    cg.draw(dp)
#    print(dp.value)