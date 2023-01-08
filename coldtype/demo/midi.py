from coldtype import *
from coldtype.timing.midi import MidiTimeline
from coldtype.tool import parse_inputs

if __as_config__:
    raise ColdtypeCeaseConfigException()

args = parse_inputs(__inputs__, dict(
    file=[None, str, "Must provide midi file"],
    duration=[None, int],
    bpm=[None, float],
    fps=[None, float],
    text=[True, bool],
    lookup=[None, {}]))

mr = MidiTimeline(
    Path(args["file"]).expanduser(),
    duration=args["duration"],
    fps=args["fps"],
    bpm=args["bpm"],
    lookup=args["lookup"])

dst = Path(args["file"]).parent
custom_folder = Path(args["file"]).name + ".midiview/renders"

if args["log"]:
    print("="*20)
    print("> Path:", mr.midi_path)
    print(f"> Note Range: {mr.min}-{mr.max}")
    print("> Duration:", mr.duration)
    print(f"> BPM/FPS: {mr.bpm}/{mr.fps}")
    print("="*20)

r = args["rect"]
xo = 47

def build_display():
    rt, rd = r.divide(30, "N")
    wu = (rd.w - xo) / int(mr.duration)

    valid_notes = set()
    for t in mr.timeables:
        valid_notes.add(int(t.name))

    valid_notes = sorted(valid_notes)
    rows = rd.subdivide(len(valid_notes), "S")

    out = PS([
        (P(rt).f(hsl(0.6, 1, 0.85))),
        (P().line(rd.subtract(xo, "W").ew)
            .fssw(-1, hsl(0.65, 1, 0.8), 1))])

    for idx, vn in enumerate(valid_notes):
        out += P(rows[idx]).f(1 if idx%2==0 else hsl(0.6, 1, 0.975))
        out += P().line(rows[idx].es).fssw(-1, hsl(0.65, 1, 0.8), 1)
        if args["text"]:
            out += StSt(f"{vn}", Font.RecursiveMono(), 20).align(rows[idx].take(xo, "W")).f(hsl(0.65))
        else:
            out += P().text(f"{vn}", Style("Monaco", 24, load_font=0), rows[idx].take(xo, "W").offset(8, rows[idx].h/2-21/2))

    for t in mr.timeables:
        t:Timeable
        i = valid_notes.index(int(t.name))
        tr = (rows[i].take(t.duration*wu, "W"))
        out += (P(tr)
            .translate(xo+t.start*wu, 0)
            .f(hsl(0.5+t.idx*0.02)))
    
    return rt, rd, out

rt, rd, static = build_display()

@animation(r,
    timeline=mr,
    dst=dst,
    custom_folder=custom_folder,
    bg=1,
    render_bg=1,
    preview_only=args["preview_only"])
def midi(f):
    px = f.e("l", 0, rng=(xo, rd.w))
    if args["text"]:
        frame = (StSt(str(f.i),
            Font.RecursiveMono(), 20)
            .align(rt.take(px-10, "W"), "E")
            .f(hsl(0.65)))
    else:
        frame = P().text("{:04d}".format(f.i),
            Style("Monaco", 18, load_font=0, fill=0),
            rt.offset(px-50, 8))

    return PS([
        static,
        frame,
        (P().line(r.ew)
            .translate(xo, 0)
            .fssw(-1, bw(0, 0.25), 1)),
        (P().line(r.ew)
            .translate(px, 0)
            .fssw(-1, 0, 1))])