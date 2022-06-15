from coldtype.geometry.rect import Rect


def parse_inputs(inputs, defaults):
    defaults["rect"] = [
        Rect(1080, 1080),
        lambda xs: Rect([int(x) for x in str(xs).split(",")])]

    defaults["preview_only"] = [False, bool]
    defaults["log"] = [False, bool]

    parsed = {}
    if not isinstance(inputs, dict):
        for idx, input in enumerate(inputs):
            if "=" in input:
                k, v = input.split("=")
                parsed[k] = v
            else:
                parsed[list(defaults.keys())[idx]] = input
    else:
        parsed = {**inputs}

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
            if defaults[k][0] is None and v is None:
                pass
            else:
                if isinstance(v, str):
                    if defaults[k][1] == bool:
                        out[k] = bool(eval(v))
                    else:
                        out[k] = defaults[k][1](v)
                else:
                    if k == "rect":
                        out[k] = Rect(v)
                    else:
                        out[k] = v
        else:
            print(f"> key {k} not recognized")
    
    return out