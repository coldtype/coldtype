from pathlib import Path
from defcon import Font as DefconFont
from drafting.text.reader import normalize_font_path, StyledString
from coldtype.pens.datpen import DATPens
from drafting.interpolation import norm, interp_dict, lerp
from random import Random


def loopidx(lst, idx):
    return lst[idx % len(lst)]

def sibling(root, file):
    return Path(root).parent.joinpath(file)

def raw_ufo(path):
    return DefconFont(normalize_font_path(path))

def ßhide(el):
    return None

def ßshow(el):
    return el

def cycle_idx(arr, idx):
    if idx < 0:
        return len(arr) - 1
    elif idx >= len(arr):
        return 0
    else:
        return idx

def random_series(start=0, end=1, seed=0, count=5000):
    rnd = Random()
    rnd.seed(seed)
    rnds = []
    for x in range(count):
        rnds.append(start+rnd.random()*(end-start))
    return rnds

def show_points(pen, style, offcurves=True, filter=lambda i: True):
    pt_labels = DATPens()
    if offcurves:
        def labeller(idx, x, y):
            if filter(idx):
                pt_labels.append(StyledString(str(idx), style).pen().translate(x, y))
        pen.map_points(labeller)
    else:
        for idx, (m, pts) in enumerate(pen.value):
            if len(pts) > 0 and filter(idx):
                pt_labels += StyledString(str(idx), style).pen().translate(*pts[-1])
    return pt_labels

_by_uni = None
_by_glyph = None
_class_lookup = None

def _populate_glyphs_unis():
    global _by_uni
    global _by_glyph
    global _class_lookup
    _by_uni = {}
    _by_glyph = {}
    _class_lookup = {}

    #try:
    if True:
        lines = (Path(__file__).parent.parent / "assets/glyphNamesToUnicode.txt").read_text().split("\n")

        for l in lines:
            if l.startswith("#"):
                continue
            l = l.split(" ")[:3]
            uni = int(l[1], 16)
            _by_uni[uni] = l[0]
            _by_glyph[l[0]] = uni
            _class_lookup[l[0]] = l[2]
    #except:
    #    pass

def uni_to_glyph(u):
    if not _by_uni:
        _populate_glyphs_unis()
    return _by_uni.get(u)
    
def glyph_to_uni(g):
    if not _by_glyph:
        _populate_glyphs_unis()
    return _by_glyph.get(g)

def glyph_to_class(g):
    if not _class_lookup:
        _populate_glyphs_unis()
    return _class_lookup.get(g)