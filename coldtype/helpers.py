from pathlib import Path

from defcon import Font as DefconFont
from coldtype.text.reader import normalize_font_path


def loopidx(lst, idx):
    return lst[idx % len(lst)]

def norm(value, start, stop):
    return start + (stop-start) * value

def interp_dict(v, a, b):
    out = dict()
    for k, _v in a.items():
        out[k] = norm(v, a[k], b[k])
    return out

def sibling(root, file):
    return Path(root).parent.joinpath(file)

def raw_ufo(path):
    return DefconFont(normalize_font_path(path))