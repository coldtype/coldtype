from coldtype.test import *
import wave, struct, math, random, pickle


"""
Run in terminal: `coldtype examples/animations/sonification.py`

After a render_all (aka hitting the `a` key in the viewer app),
this code will render individual wave files for each letter,
to the examples/animations/renders/sonification folder

Those waves can then be played back in any DAW and should
be visible on an x/y scope (like this one http://goodhertz.com/midside-matrix)
"""

class sonification(animation):
    def __init__(self, timeline, filename, samples_per_frame=1, **kwargs):
        self.filename = filename
        self.samples_per_frame = samples_per_frame
        super().__init__(fmt="pickle", timeline=timeline, **kwargs)
    
    def package(self):
        sampleRate = 48000.0 # hertz
        obj = wave.open(str(self.output_folder.parent / self.filename), 'w')
        obj.setnchannels(2)
        obj.setsampwidth(2)
        obj.setframerate(sampleRate)

        for pp in sorted(self.output_folder.glob("*.pickle")):
            pen:DATPen = (pickle
                .load(open(pp, "rb"))[0]
                .scale(-1, 1)
                .rotate(-45)
                .translate(-500, -500)
                .removeOverlap()
                .flatten(1))
    
            left, right = [], []
            for (_, pts) in pen.value:
                if len(pts) > 0:
                    left.append(pts[0][0])
                    right.append(pts[0][1])
            
            for x in range(0, self.samples_per_frame):
                for idx, l in enumerate(left):
                    data = struct.pack('<h', int(l)*24)
                    obj.writeframesraw(data)
                    data = struct.pack('<h', int(right[idx])*24)
                    obj.writeframesraw(data)
            
        obj.close()
        print("/wrote-wav:", self.name, self.filename)

def animate_letter(f, l):
    e = f.a.progress(f.i, loops=2, easefn="qeio").e
    c = (StSt(l, Font.ColdtypeObviously(),
        fontSize=1000-(1-e)*250, wdth=1-e, wght=e)
        .align(f.a.r)
        .fssw(-1, 0, 2)
        .pen()
        .removeOverlap()
        #.explode()[0] # do this to knock out counters
        )
    return c

tl = Timeline(60)
l = "E"

@sonification(tl, f"_{l}.wav")
def letter(f): return animate_letter(f, l)