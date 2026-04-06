
def norm(value, start, stop):
    return start + (stop-start) * value

def lerp(start, stop, amt):
    return float(amt-start) / float(stop-start)

def interp_dict(v, a, b=None):
    if not isinstance(a, dict):
        return norm(v, a, b)

    if b is None:
        a, b = a[0], a[1]
    
    out = dict()
    for k, _v in a.items():
        if hasattr(a[k], "interp"):
            out[k] = a[k].interp(v, b[k])
        elif isinstance(a[k], str):
            out[k] = b[k]
        else:
            out[k] = norm(v, a[k], b[k])
    return out

def loopidx(lst, idx):
    return lst[idx % len(lst)]