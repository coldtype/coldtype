from coldtype import *
from coldtype.interpolation import interp_dict
from coldtype.time.nle.ascii import AsciiTimeline

def state(self:AsciiTimeline, fi, len=8, lines=None, easefn="eeio"):
    for c1, c2 in self.enumerate(lines=lines, pairs=True):
        start, end = c1.end, c2.start
        if c2.start < c1.end:
           end += self.duration
           if fi < c1.start:
               fi += self.duration

        t = Timeable(
            end-len,
            start+len,
            name=f"_transition_{c1.name}/{c2.name}",
            timeline=self)
        if t.now(fi):
            return interp_dict(t.at(fi).e(easefn, 0), self.states[c1.name], self.states[c2.name])
        elif (c1.start + len) <= fi < (c1.end - len):
            return self.states[c1.name]
    
    return list(self.states.values())[0]

def kf(self:AsciiTimeline, fi, easefn="eeio", lines=None):
    for c1, c2 in self.enumerate(lines=lines, pairs=True):
        start, end = c1.start, c2.start
        if c2.start < c1.end:
           end += self.duration
           if fi < c1.start:
               fi += self.duration

        t = Timeable(start, end,
            name=f"_kf_{c1.name}/{c2.name}",
            timeline=self)
        if t.now(fi):
            return interp_dict(t.at(fi).e(easefn, 0), self.states[c1.name], self.states[c2.name])
    
    return list(self.states.values())[0]

AsciiTimeline.state = state
AsciiTimeline.kf = kf

at = AsciiTimeline(1, 30, """
                                       <
0     0 1       2    3      0    3 4
""", states={
    "0": dict(wdth=0, rotate=0, tu=300),
    "1": dict(wdth=1, rotate=15, tu=-150),
    "2": dict(wdth=0.25, rotate=-15, tu=350),
    "3": dict(wdth=0.75, rotate=0, tu=-175),
    "4": dict(wdth=0.5, rotate=25, tu=100)})

@animation(timeline=at, bg=1, rect=(1500, 300))
def render(f):
    return (StSt("COLDTYPE",
        Font.ColdtypeObviously(),
        250, fill=0,
        **at.kf(f.i, easefn="qeio"),
        r=1, ro=1)
        .align(f.a.r)
        .f(0)
        .understroke(s=1, sw=15))