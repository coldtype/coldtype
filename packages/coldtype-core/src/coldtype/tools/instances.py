"""
Display all available instances in variable font; click instance to see more info
"""

from coldtype import *
from coldtype.tool import parse_inputs
from pprint import pprint

if __as_config__:
    raise ColdtypeCeaseConfigException()

args = parse_inputs(ººinputsºº, dict(
    font=[None, str, "Must provide font"]))

font = args["font"]

instances = font.instances()
unscaled = font.instances(scaled=False)

if len(instances) > 0:
    print(f"=== {font.path.name} ===")
    print(f"=== {len(instances)} instances ===")
    print("")

    vectors = (P().enumerate(instances.keys(), lambda x:
        StSt(x.el, font, 80, instance=x.el)
            .data(
                instanceKey=x.el,
                instance=instances[x.el],
                unscaled=unscaled[x.el])
        ).stack(10))

    a = vectors.ambit()
    h = max(a.h, 1600)
    r = Rect(a.w*h/a.h, h)

    @ui(r.inset(-20).zero(), bg=0)
    def display(u):
        def print_instance(x):
            un = x.data("unscaled")
            divider = "-"*(len(str(un)) + len("Unscaled: ") + 3)
            print(divider)
            print(f" Instance: “{x.data('instanceKey')}”")
            print(" Scaled: ", x.data("instance"))
            print(" Unscaled: ", un)
            print(divider)
            print("")
            return x

        return (vectors
            .copy()
            .scaleToRect(r)
            .align(u.r)
            .f(1)
            .map(lambda p: p.cond(u.c.inside(p.ambit()), print_instance)))
