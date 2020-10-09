import inspect
from coldtype.pens.datpen import DATPen, DATPenLikeObject, DATPenSet

if __name__ == "<run_path>":
    
    for name, routine in inspect.getmembers(DATPen, predicate=inspect.isroutine):
        if not name.startswith("__"):
            print("----------------------------------")
            #print(name)
            ps = []
            vs = []
            for k, p in inspect.signature(routine).parameters.items():
                if k == "self":
                    continue
                empty = p.default == inspect.Parameter.empty
                pa = p.name
                if not empty:
                    pa += ("=" + str(p.default))
                ps.append(pa)
                vs.append(p.name)
            print(f"def {p.name}({', '.join(ps)}):")
            print(f"\treturn ['{p.name}', {', '.join(vs)}]")
    
    #for name, routine in inspect.getmembers(DATPenSet, predicate=inspect.isroutine):
    #    if not name.startswith("__"):
    #        dps[name] = routine