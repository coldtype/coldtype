from coldtype import *

VERSIONS = {}
for file in sorted(ººsiblingºº(".").glob("*.py")):
    if not file.stem.startswith("_"):
        VERSIONS[file.stem] = dict(file=file)