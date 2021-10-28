from coldtype import *
from .source_file_adjacent import * #INLINE

@animation()
def test_src_animation(f):
    return (StSt("COLDTYPE",
        "assets/ColdtypeObviously-VF.ttf",
        wdth=f.e("linear", 1))
        .align(f.a.r))