from coldtype import *
from random import randint

@renderable(rect=(1000, 300), bg=0.1)
def test_distribute_and_track(r):
    dps = DATPenSet()
    for x in range(0, 11):
        dps += DATPen().rect(Rect(100, 100)).f("hr",0.65,0.55).rotate(randint(-45, 45))
    return dps.distribute().track(-50).reversePens().understroke(s=1).align(r)