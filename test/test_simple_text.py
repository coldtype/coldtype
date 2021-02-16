from coldtype.test import *

@test()
def stub(r):
    dps = (StyledString("Yy",
        Style("~/Type/fonts/fonts/_script/MistralD.otf", 500))
        .pens()
        .align(r)
        )
    return dps
