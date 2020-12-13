from coldtype.test import *
from pprint import pprint

def to_code(self):
    t = None
    if self._tag and self._tag != "?":
        t = self._tag
    out = "(DATPen()"
    if t:
        out += f"\n    .tag(\"{t}\")"
    for mv, pts in self.value:
        out += "\n"
        if len(pts) > 0:
            spts = ", ".join([f"{(x, y)}" for (x, y) in pts])
            out += f"    .{mv}({spts})"
        else:
            out += f"    .{mv}()"
    for k, v in self.attrs.get("default").items():
        if v:
            if k == "fill":
                out += f"\n    .f({v.to_code()})"
            elif k == "stroke":
                out += f"\n    .s({v['color'].to_code()})"
                out += f"\n    .sw({v['weight']})"
            else:
                print("No code", k, v)
    out += ")"
    return out

DATPen.to_code = to_code

code_version = None

@renderable()
def to_code(r):
    dp = (DATPen()
        .oval(r.inset(50))
        .f(hsl(0.65, s=0.6, l=0.7))
        .s(0)
        .sw(5)
        .tag("circle"))
    
    global code_version
    code_version = dp.round_to(1).to_code()
    print(code_version)
    return dp

@renderable()
def from_code(r):
    if code_version:
        dp = eval(code_version)
        #pprint(dp.value)
        return dp