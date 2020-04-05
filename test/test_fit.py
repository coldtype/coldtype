from coldtype import *

@renderable()
def test_fit(r):
    return StyledString("ABC", Style("≈/ObviouslyVariable.ttf", 500, wdth=1)).fit(r.w).pens().f("random").align(r)