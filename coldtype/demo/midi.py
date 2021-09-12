from coldtype import *
from coldtype.time.midi import MidiReader
from coldtype.tool import parse_inputs

if __as_config__:
    raise ColdtypeCeaseConfigException()

args = parse_inputs(__inputs__, dict(
    file=[None, str, "Must provide midi file"],
    duration=[None, int],
    bpm=[None, float],
    fps=[None, float],
    log=[True, bool],
    w=1080,
    h=1080))

mr = MidiReader(
    Path(args["file"]).expanduser(),
    duration=args["duration"],
    fps=args["fps"],
    bpm=args["bpm"])

dst = Path(args["file"]).parent
custom_folder = Path(args["file"]).name + ".midiview/renders"

if args["log"]:
    print("="*20)
    print("> Path:", mr.midi_path)
    print(f"> Note Range: {mr.min}-{mr.max}")
    print("> Duration:", mr.duration)
    print(f"> BPM/FPS: {mr.bpm}/{mr.fps}")
    print(f"> Track Count: {len(mr.tracks)}")
    print("="*20)

r = args["rect"]
xo = 47

def build_display():
    rt, rd = r.divide(30, "N")
    wu = (rd.w - xo) / int(mr.duration)

    valid_notes = set()
    for t in mr.tracks:
        for n in t.notes:
            valid_notes.add(n.note)

    valid_notes = sorted(valid_notes)
    rows = rd.subdivide(len(valid_notes), "S")

    out = PS([
        (P().line(rd.subtract(xo, "W").ew)
            .fssw(-1, hsl(0.65, 1, 0.8), 1))])

    for idx, vn in enumerate(valid_notes):
        out += P(rows[idx]).f(hsl(0.65+idx*0.5, 1, a=0.05))
        out += P().line(rows[idx].es).fssw(-1, hsl(0.65, 1, 0.8), 1)
        out += StSt(f"{vn}", Font.RecursiveMono(), 20).align(rows[idx].take(xo, "W")).f(hsl(0.65))

    for tidx, t in enumerate(mr.tracks):
        for n in t.notes:
            out += (P(rows[valid_notes.index(n.note)]
                    .take(n.duration*wu, "W"))
                .translate(xo+n.on*wu, 0)
                .f(hsl(0.5+tidx*0.1+n.idx*0.02)))
    
    return rt, rd, out

rt, rd, static = build_display()

@animation(r,
    timeline=mr,
    dst=dst,
    custom_folder=custom_folder,
    bg=1,
    render_bg=1)
def midi(f):
    return PS([
        static,
        (P().line(r.ew)
            .translate(f.e("l", rng=(xo, rd.w)), 0)
            .fssw(-1, 0, 1))])