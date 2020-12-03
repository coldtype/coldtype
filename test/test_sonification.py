from coldtype.test import *
import wave, struct, math, random, pickle


"""
Run in terminal: `coldtype test/test_sonification.py`

After a render_all (aka hitting the `a` key in the viewer app),
this code will render individual wave files for each letter,
to the test/test_sonification/ folder

Those waves can then be played back in any DAW and should
be visible on an x/y scope (like this one http://goodhertz.co/midside-matrix)
"""

Style.RegisterShorthandPrefix("≈", "~/Type/fonts/fonts")

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

def animate_letter(f, fn):
    e = f.a.progress(f.i, loops=2, easefn="qeio").e
    ie = 1 - e
    txt, style = fn(e, ie)
    c = (StyledString(txt, style)
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

tl = Timeline(90)

@sonification(tl, "_T.wav")
def t(f):
    return animate_letter(f,
        lambda e, ie: ("T", Style("≈/ObviouslyVariable.ttf",
            1000-ie*250, wdth=ie, wght=e)))

@sonification(tl, "_Y.wav")
def y(f):
    return animate_letter(f,
        lambda e, ie: ("Y", Style("≈/_wdths/CoFoPeshkaV0.4_Variable.ttf",   
            1000-e*250, wdth=e, wght=e)))

@sonification(tl, "_P.wav")
def p(f):
    return animate_letter(f,
        lambda e, ie: ("P", Style("≈/CheeeVariable.ttf",
            1000, grvt=ie, yest=e)))

@sonification(tl, "_E.wav")
def e(f):
    return animate_letter(f,
        lambda e, ie: ("E", Style("≈/SwearCilatiVariable.ttf",
            1000, wght=e)))