from coldtype import *

@renderable()
def test_fit(r):
    return Slug("ABC", Style("≈/ObviouslyVariable.ttf", 500, wdth=1, wght=1, slnt=1, tu=-150, r=1)).fit(r.w-100).pens().f("random").align(r).understroke()