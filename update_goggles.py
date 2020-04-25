#!/usr/bin/env python

from shutil import copytree, copy2
from pathlib import Path

fg_src_dir = Path("~/Goodhertz/fontgoggles/Lib/fontgoggles").expanduser()
fg_dst_dir = Path(__file__).parent / "coldtype/fontgoggles"

fg_dst_dir.mkdir(exist_ok=True)

copy2(fg_src_dir.parent.parent / "LICENSE.txt", fg_dst_dir / "LICENSE.txt")
(fg_dst_dir / "README.md").write_text("This is an automated import of github.com/goodhertz/fontgoggles, to avoid hosting this code on pypi itself")

for submodule in ["compile", "font", "misc"]:
    copytree(fg_src_dir / submodule, fg_dst_dir / submodule, dirs_exist_ok=True)
    for pyf in (fg_dst_dir / submodule).glob("**/*.py"):
        if pyf.stem in ["unicodeNameList"]:
            pyf.unlink()
        else:
            pycode = pyf.read_text()
            pycode = pycode.replace(""""fontgoggles.font""", """"coldtype.fontgoggles.font""")
            pycode = pycode.replace(""""fontgoggles.compile""", """"coldtype.fontgoggles.compile""")
            pyf.write_text(pycode)