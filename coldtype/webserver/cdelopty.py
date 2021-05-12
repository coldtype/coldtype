import json
from drafting.geometry import Rect

def _parse(el, depth=0, chain=False):
    out = []
    chaining = False

    for idx, e in enumerate(el):
        if idx == 0:
            if e == "ø":
                return ""
            elif e == "R":
                out.append("Rect")
            elif e == "P":
                out.append("DATPen")
            elif e == "Ps":
                out.append("DATPens")
            elif e == "S":
                out.append("StSt")
            elif e in ["hsl", "rgb"]: # general whitelist?
                out.append(e)
            else:
                if not chain:
                    out.append(f".{e}")
                else:
                    t = "    " * depth
                    out.append(f"\n{t}.{e}")
            out.append("(")
        elif e == ".":
            chaining = True
            out.append(")")
        elif isinstance(e, str) or isinstance(e, int) or isinstance(e, float):
            if e == "®":
                e = "r"
            elif isinstance(e, str) and "=" not in e and not e.startswith("."):
                if "\n" in e:
                    e = f"\"\"\"{e}\"\"\""
                else:
                    e = f"\"{e}\""
            
            if isinstance(e, str) and e.startswith("."):
                out[-1] += e
            elif idx < 2:
                out.append(str(e))
            else:
                if out[0] == "StSt" and idx == 2:
                    out.append(f", font_cache.get({e}, DEFAULT_FONT)")
                else:
                    out.append(f", {e}")
        elif isinstance(e, dict):
            out.append(f", **{e}")
        elif e is None:
            out.append(None)
        else:
            parsed = _parse(e, depth+1, out[0] == "DATPen" or out[0] == "DATPens" or out[0] == "StSt")
            parsed = "".join([str(el) for el in parsed])
            out.append(parsed)

    if not chaining:
        out.append(")")
    return "".join([str(el) for el in out])


def parse(tree):
    if isinstance(tree, str):
        data = json.loads(tree)
    else:
        data = json.loads(json.dumps(tree))
    
    out = []
    for el in data:
        out.append("(" + _parse(el) + ")")

    to_eval = "[" + ",\n ".join(out) + "]"
    return to_eval

def evalcdel(tree,
    r=Rect(1080, 1080),
    font_cache={},
    DEFAULT_FONT=None):
    from drafting.color import hsl, rgb
    from coldtype.pens.datpen import DATPen, DATPens
    from coldtype.text import StSt, StyledString, Style
    return eval(parse(tree))

if __name__ == "__main__":
    test = [
        ["P", ".",
            ["oval", ["R", 500, 500, ".", ["inset", 50]]],
            ["f", ["hsl", 0.3, "a=0.5"]],
            ["align", "®"]
        ],
        ["S", "COOL", "ColdtypeObviously", 12, {"wdth":0.5},
            ".",
            ["pen"],
            ["align", "®"]]
    ]

    print(evalcdel(test))