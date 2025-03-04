from coldtype import *
from coldtype.tool import parse_inputs
from runpy import run_path

import inspect

if __as_config__:
    raise ColdtypeCeaseConfigException()

args = parse_inputs(__inputs__, dict(
    path=[None, Path, "Must provide file path"]))

res = run_path(args["path"])
_renderables = []

for k, v in res.items():
    docstring = inspect.getdoc(v)
    if docstring and "---\n@example" in docstring:
       _renderables.append(exec("from coldtype import *;from coldtype.renderable.renderable import example\n" + docstring.split("---")[-1]))

@renderable((800, 20), watch=[args["path"]])
def updater(r):
    return None