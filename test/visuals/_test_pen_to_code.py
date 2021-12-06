from coldtype.test import *
from pprint import pprint
from textwrap import indent
from runpy import run_path

@renderable()
def to_code(r):
    dps = DATPens([
        (DATPen()
            .oval(r.inset(50))
            .f(hsl(0.65, 0.6, 0.7))
            .s(0)
            .sw(5)
            .tag("circle1")),
        (DATPen()
            .oval(r.inset(150))
            .f(hsl(0.75, 0.6, 0.7))
            .s(1)
            .sw(5)
            .tag("circle2")
            .add_data("circular", True)
            .add_data("cool", dict(very=True)))
    ]).tag("circles")

    __sibling__("_test_pen_to_code_output.py").write_text(dps.round_to(1).to_code())
    return dps

@renderable()
def from_code(r):
    gen_code = __sibling__("_test_pen_to_code_output.py")
    if gen_code.exists():
        dps = eval(gen_code.read_text())
        print(dps.tag())
        dps[1].f(hsl(0.05, l=0.6)).translate(50, 0)
        assert dps[1].data["circular"] == True
        assert dps[1].data["cool"]["very"] == True
        return dps