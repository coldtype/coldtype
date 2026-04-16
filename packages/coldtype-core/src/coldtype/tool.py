from coldtype.geometry.rect import Rect
from coldtype.text.font import Font


def parse_inputs(inputs, defaults, ui=True, positional=True):
    if ui:
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
            elif input in defaults.keys():
                parsed[input] = True
            elif positional:
                try:
                    parsed[list(defaults.keys())[idx]] = input
                except KeyError:
                    pass
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
    
    font_variations = {}
    out["font_variations"] = {}
    
    for k, v in parsed.items():
        if k in defaults:
            if defaults[k][0] is None and v is None:
                pass
            else:
                if isinstance(v, str):
                    if k == "font":
                        vs = v.split("@")
                        fnt_idx = 0
                        if len(vs) > 1:
                            fnt_idx = int(vs[1])
                        fonts = Font.List(vs[0])
                        if len(fonts) == 0:
                            print(f"\n\n‼️ Search \"{v}\" returned no fonts ‼️\n")
                            out[k] = Font.ColdtypeObviously()
                        else:
                            print(f"\nMatching Fonts ([{fnt_idx}] is selected):")
                            for idx, f in enumerate(fonts):
                                if idx == fnt_idx:
                                    print(f"  > [{idx}]", f)
                                else:
                                    print(f"    [{idx}]", f)
                            out[k] = Font.Cacheable(fonts[fnt_idx])
                            font_variations = out[k].variations()
                            # print("Matched:")
                            # print("="*len(str(out[k].path)))
                            # print(out[k].path)
                            # print("="*len(str(out[k].path)))
                    elif defaults[k][1] == bool:
                        out[k] = bool(eval(v))
                    else:
                        out[k] = defaults[k][1](v)
                else:
                    if k == "rect":
                        out[k] = Rect(v)
                    else:
                        out[k] = v
        else:
            if k in font_variations:
                out["font_variations"][k] = float(v)
            else:
                print(f"> key {k} not recognized")

    return out