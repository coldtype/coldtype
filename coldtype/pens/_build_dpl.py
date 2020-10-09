import inspect
from pathlib import Path
from coldtype.pens.datpen import DATPen, DATPenLikeObject, DATPenSet

if __name__ == "<run_path>":
    dp = "from coldtype.geometry import Rect, Edge\n\n"
    
    for name, routine in inspect.getmembers(DATPen, predicate=inspect.isroutine):
        if not name.startswith("_"):
            #print("---", name)
            #print(name)
            ps = []
            vs = []
            for k, p in inspect.signature(routine).parameters.items():
                if k == "self":
                    continue
                empty = p.default == inspect.Parameter.empty
                pa = p.name
                if not empty:
                    if isinstance(p.default, str):
                        print(">>>>>>>>>>>", p.default)
                        pa += f'="{p.default}"'
                    else:
                        pa += ("=" + str(p.default))
                elif p.name == "kwargs":
                    pa = "**kwargs"
                elif p.name == "args":
                    pa = "*args"
                ps.append(pa)
                vs.append(p.name)
            dp += f"def {name}({', '.join(ps)}):\n"
            dp += f"\treturn ['{name}', {', '.join(vs)}]\n\n"

            dp += f"def ø{name}({', '.join(ps)}):\n"
            dp += f"\treturn ['skip']\n\n"

            dp += f"def skip_{name}({', '.join(ps)}):\n"
            dp += f"\treturn ['skip']\n\n"
    
    (Path(__file__).parent / "dp_auto_abbrev.py").write_text(dp)
    #print(dp)
    
    #for name, routine in inspect.getmembers(DATPenSet, predicate=inspect.isroutine):
    #    if not name.startswith("__"):
    #        dps[name] = routine

import coldtype.pens.dp_auto_abbrev