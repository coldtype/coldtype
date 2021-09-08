from coldtype.geometry.rect import Rect


def parse_inputs(inputs, defaults):
    parsed = {}
    for input in inputs:
        k, v = input.split("=")
        parsed[k] = v

    out = {}
    for k, v in defaults.items():
        if k in ["w", "h"]:
            out[k] = v
            defaults[k] = [v, int]
        else:
            out[k] = v[0]
            if k not in parsed and len(v) > 2:
                raise Exception(v[2])
    
    for k, v in parsed.items():
        if k in defaults:
            out[k] = defaults[k][1](v)
        else:
            print(f"> key {k} not recognized")
    
    if "w" in defaults and "h" in defaults:
        out["rect"] = Rect(out["w"], out["h"])
    return out