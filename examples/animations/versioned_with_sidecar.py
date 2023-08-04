from coldtype import *

root = __sibling__("../..").resolve()

"""
__VERSION__ is populated by VERSIONS
defined in *._versions.py versions of
this file
"""

@animation(bg=0)
def scratch_ƒVERSION(f):
    return (P(
        StSt(__VERSION__["key"], Font.RecMono(), 72),
        StSt(str(__VERSION__["file"].relative_to(root)), Font.RecMono(), 24),
        )
        .stack(20)
        .align(f.a.r)
        .rotate(f.e("l", 0, r=(0, 360))))
