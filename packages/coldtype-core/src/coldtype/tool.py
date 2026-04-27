from pathlib import Path

from coldtype.geometry.rect import Rect
from coldtype.text.font import Font


def fmt_path(path: Path) -> str:
    try:
        return "~/" + str(path.relative_to(Path.home()))
    except ValueError:
        return str(path)


def print_font_results(results, selected=None):
    maxsys = max([len(f.system_name) for f in results])
    maxpat = max([len(fmt_path(f.path)) for f in results])
    print("")
    print(f"     # {'Name':<{maxsys}} Path")
    print(f"   {'-'*(maxsys+maxpat+7)}")
    for idx, result in enumerate(results):
        if idx == selected:
            print(f"➡️  {idx:>{3}} {result.system_name:<{maxsys}} {fmt_path(result.path)}")
        else:
            print(f"   {idx:>{3}} {result.system_name:<{maxsys}} {fmt_path(result.path)}")
    print("\n")


def parse_inputs(inputs, defaults, ui=True, positional=True):
    if ui is not None and ui is not False:
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
                        sized = v.split(":")
                        if len(sized) > 1:
                            out["fontSize"] = int(sized[1])
                        
                        v = sized[0]
                        vs = v.split("@")
                        fnt_idx = 0
                        if len(vs) > 1:
                            fnt_idx = int(vs[1])
                        fonts = Font.ListAll(vs[0])
                        if len(fonts) == 0:
                            print(f"\n\n‼️ Search \"{v}\" returned no fonts ‼️\n")
                            out[k] = Font.ColdtypeObviously()
                        else:
                            out["fonts"] = fonts
                            print_font_results(fonts, fnt_idx)
                            out[k] = fonts[fnt_idx]
                            font_variations = out[k].variations()
                    elif k == "rect":
                        if v == "max":
                            out[k] = ui.get("monitor").scale(2).inset(200).square().zero()
                        else:
                            out[k] = eval(f"Rect({v})")
                        #raise Exception("IMPLEMENT MAX with screen size")
                    elif defaults[k][1] == bool:
                        out[k] = bool(eval(v))
                    else:
                        out[k] = defaults[k][1](v)
                else:
                    if k == "rect":
                        print("ALSO HERE")
                        out[k] = Rect(v)
                    else:
                        out[k] = v
        else:
            if k in font_variations:
                out["font_variations"][k] = float(v)
            else:
                print(f"> key {k} not recognized")

    return out