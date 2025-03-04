from coldtype import *
from coldtype.tool import parse_inputs
from pprint import pprint
from itertools import combinations
from random import Random

if __as_config__:
    raise ColdtypeCeaseConfigException()

args = parse_inputs(__inputs__, dict(
    font=[None, str, "Must provide font"],
    font_size=[None, int],
    positions=[(0, 1), lambda xs: [float(x) for x in xs.split(",")]],
    stroke=[False, bool],
    text=["A", str],
    seed=[0, int],
    shuffle=[False, bool],
    animate=[True, bool]))

rnd = Random()
rnd.seed(args["seed"])

if isinstance(args["font"], str):
    args["font"] = Font.Find(args["font"])

dst = args["font"].path
custom_folder = dst.name + ".vfview/renders"

axes = args["font"].variations()
if args["log"]:
    pprint(axes)

possibles = []
for a in axes.keys():
    for x in args["positions"]:
        possibles.append([a, x])

valids = []
for c in combinations(possibles, len(axes.keys())):
    v = True
    for idx, a in enumerate(c):
        for jdx, a2 in enumerate(c):
            if idx != jdx and a[0] == a2[0]:
                v = False
    if v:
        valids.append(c)

axes_combos = []
for combo in valids:
    axs = {}
    for k, v in combo:
        axs[k] = v
    axes_combos.append(axs)

sq = math.floor(math.sqrt(len(axes_combos)))

r:Rect = args["rect"]
rs = r.inset(20).grid(sq, math.ceil(len(axes_combos)/sq))

if args["shuffle"]:
    rnd.shuffle(axes_combos)

@animation(r,
    timeline=60 if args["animate"] else 1,
    dst=dst,
    custom_folder=custom_folder,
    bg=0,
    render_bg=1,
    preview_only=args["preview_only"])
def vf(f):
    if args["animate"]:
        anim_combos = []
        for ac in axes_combos:
            anim_combo = {}
            for k, v in ac.items():
                anim_combo[k] = f.e("eeio", 1, rng=(v, v+1))
            anim_combos.append(anim_combo)
    else:
        anim_combos = axes_combos

    def txt(x):
        #return P(rs[x.i].inset(20))
        return P(
            StSt(args["text"], args["font"],
                args["font_size"] or rs[x.i].h-50,
                rv=1,
                **x.el)
                .align(rs[x.i], tx=0)
                .cond(args["stroke"],
                    lambda p: p.fssw(-1, 1, 2),
                    lambda p: p.f(1)),
            P().text(",".join(["{:0.2f}".format(v) for v in x.el.values()]),
                Style(Font.RecursiveMono(), 24, fill=bw(1, 0.5), load_font=0),
                rs[x.i].inset(50, 0)))

    return (P().enumerate(anim_combos, txt))