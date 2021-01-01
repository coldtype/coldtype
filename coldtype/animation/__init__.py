import math
from coldtype.helpers import loopidx, interp_dict
from coldtype.animation.timeable import Timing, Timeable, TimeableSet
from coldtype.animation.timeline import Timeline
from coldtype.animation.loop import Loop, LoopPhase


class Frame():
    def __init__(self, i, animation):
        self.i = i
        self.a = animation