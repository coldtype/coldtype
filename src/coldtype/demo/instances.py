from coldtype import *
from coldtype.tool import parse_inputs
from pprint import pprint

if __as_config__:
    raise ColdtypeCeaseConfigException()

args = parse_inputs(ººinputsºº, dict(
    font=[None, str, "Must provide font"]))

font = Font.Find(args["font"])

print(f"=== {font.path.name} ===")
pprint(font.instances(scaled=False))

@renderable((1080, 1080), bg=0)
def scratch(r):
    instances = font.instances()
    if not instances:
        return None
    
    return (P().enumerate(instances.keys(), lambda x:
        P(
            StSt(x.el, font, 80, instance=x.el),
            StSt(f"({x.el})", Font.JBMono(), 30))
            .stack(10)
            .index(0, λ.t(20, 0)))
        .stack(10)
        .scaleToRect(r.inset(20), shrink_only=True)
        .align(r)
        .f(1))
