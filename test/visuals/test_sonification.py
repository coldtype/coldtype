from coldtype.test import *
import wave, struct, math, random, pickle


"""
Run in terminal: `coldtype test/test_sonification.py`

After a render_all (aka hitting the `a` key in the viewer app),
this code will render individual wave files for each letter,
to the test/renders/test_sonification folder

Those waves can then be played back in any DAW and should
be visible on an x/y scope (like this one http://goodhertz.co/midside-matrix)
"""

class sonification(animation):
    def __init__(self, timeline, filename, samples_per_frame=1, **kwargs):
        self.filename = filename
        self.samples_per_frame = samples_per_frame
        super().__init__(fmt="pickle", timeline=timeline, **kwargs)
    
    def package(self, filepath, output_folder:Path):
        sampleRate = 48000.0 # hertz
        obj = wave.open(str(output_folder.parent / self.filename), 'w')
        obj.setnchannels(2)
        obj.setsampwidth(2)
        obj.setframerate(sampleRate)

        for pp in sorted(output_folder.glob("*.pickle")):
            pen:DATPen = (pickle
                .load(open(pp, "rb"))
                .scale(-1, 1)
                .rotate(-45)
                .translate(-500, -500)
                .removeOverlap()
                .flatten(1))
    
            left, right = [], []
            for (mv, pts) in pen.value:
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

def animate_letter(f, l):
    e = f.a.progress(f.i, loops=2, easefn="qeio").e
    c = (StyledString(l,
        Style(co, 1000-(1-e)*250, wdth=1-e, wght=e))
        .pens()
        .align(f.a.r)
        .f(None)
        .s(0)
        .sw(2)
        .pen()
        .removeOverlap()
        #.explode()[0] # do this to knock out counters
        )
    return c

tl = Timeline(60)

@sonification(tl, "_T.wav")
def t(f): return animate_letter(f, "T")

@sonification(tl, "_Y.wav")
def y(f): return animate_letter(f, "Y")

@sonification(tl, "_P.wav")
def p(f): return animate_letter(f, "P")

@sonification(tl, "_E.wav")
def e(f): return animate_letter(f, "E")