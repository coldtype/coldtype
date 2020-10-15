import inspect
from pathlib import Path
from coldtype.pens.datpen import DATPen, DATPenLikeObject, DATPenSet

def signature(routine):
    ps = []
    vs = []
    for k, p in inspect.signature(routine).parameters.items():
        if k == "self":
            continue
        empty = p.default == inspect.Parameter.empty
        pa = p.name
        if not empty:
            if isinstance(p.default, str):
                #print(">>>>>>>>>>>", p.default)
                pa += f'="{p.default}"'
            else:
                pa += ("=" + str(p.default))
        elif p.name == "kwargs":
            pa = "**kwargs"
        elif p.name == "args":
            pa = "*args"
        ps.append(pa)
        vs.append(p.name)
    return ps, vs

def write_alias(name, routine, aliasset):
    ps, vs = signature(routine)
    aliasset[name] = [ps, vs]
    
    txt = ""
    txt += f"def {name}({', '.join(ps)}):\n"
    txt += f"\treturn ['{name}', {', '.join(vs)}]\n\n"

    txt += f"def ø{name}({', '.join(ps)}):\n"
    txt += f"\treturn ['skip']\n\n"

    txt += f"def s_{name}({', '.join(ps)}):\n"
    txt += f"\treturn ['skip']\n\n"
    return txt

if __name__ == "<run_path>":
    dp = "from coldtype.geometry import Rect, Edge\n\n"
    
    dp_methods = {}
    dps_methods = {}
    
    for name, routine in inspect.getmembers(DATPen, predicate=inspect.isroutine):
        if not name.startswith("_"):
            dp += write_alias(name, routine, dp_methods)
    
    for name, routine in inspect.getmembers(DATPenSet, predicate=inspect.isroutine):
        if not name.startswith("_"):
            if dp_equivalent := dp_methods.get(name):
                ps, vs = signature(routine)
                eps, evs = dp_equivalent
                if not str(ps) == str(eps):
                    print("HELLO", name)
            else:
                dp += write_alias(name, routine, dps_methods)
    
    (Path(__file__).parent / "dp_auto_abbrev.py").write_text(dp)

    #from pprint import pprint
    #pprint(dp_methods)

import coldtype.pens.dp_auto_abbrev