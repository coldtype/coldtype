
def norm(value, start, stop):
    return start + (stop-start) * value

def lerp(start, stop, amt):
    return float(amt-start) / float(stop-start)

def interp_dict(v, a, b):
    out = dict()
    for k, _v in a.items():
        out[k] = norm(v, a[k], b[k])
    return out

def loopidx(lst, idx):
    return lst[idx % len(lst)]