import sys
from pathlib import Path

from coldtype.color import normalize_color
from coldtype.geometry import Rect
from coldtype.text import *

from coldtype.animation.easing import ease
from coldtype.animation.timeline import Timeline
from coldtype.animation.premiere import PremiereTimeline, ClipGroup, ClipFlags, ClipType
from coldtype.animation.midi import MidiTimeline, MidiTrack, MidiNote

from random import random
import json
import math
import re


def sibling(root, file):
    return Path(root).parent.joinpath(file)


class AnimationFrame():
    def __init__(self, index, animation, layers):
        self.i = index
        self.a = animation
        self.layers = layers
        self.filepaths = {}

    def __repr__(self):
        return f"<AnimationFrame {self.i}>"


class AnimationTime():
    def __init__(self, t, loop_t, loop, easefn):
        self.t = t
        self.loop_t = loop_t
        self.loop = loop
        self.loop_phase = int(loop%2 != 0)
        self.e, self.s = self.ease(easefn)
    
    def ease(self, easefn):
        easer = easefn
        if not isinstance(easer, str):
            try:
                iter(easefn) # is-iterable
                if len(easefn) > self.loop:
                    easer = easefn[self.loop]
                elif len(easefn) == 2:
                    easer = easefn[self.loop % 2]
                elif len(easefn) == 1:
                    easer = easefn[0]
            except TypeError:
                pass
        return ease(easer, self.loop_t)


class Animation():
    def __init__(self, 
            render,
            rect=Rect(0, 0, 1920, 1080),
            timeline=None,
            bg=0,
            layers=["main"],
            watches=[]
        ):
        self.render = render
        self.rect = Rect(rect)
        self.r = self.rect
        self.cache = {}
        self.layers = layers
        self.watches = [str(w.expanduser().resolve()) for w in watches]
        self.sourcefile = None

        if hasattr(timeline, "storyboard"):
            self.timeline = timeline
        elif timeline:
            self.timeline = Timeline(timeline, 30)
        else:
            self.timeline = Timeline(1, 30)
        
        self.t = self.timeline # alias
        self.bg = normalize_color(bg)
        
    def _loop(self, t, times=1, cyclic=True):
        lt = t*times*2
        ltf = math.floor(lt)
        ltc = math.ceil(lt)
        if False:
            if ltc % 2 != 0: # looping back
                lt = 1 - (ltc - lt)
            else: # looping forward
                lt = ltc - lt
        lt = lt - ltf
        if cyclic and ltf%2 == 1:
            lt = 1 - lt
        return lt, ltf
    
    def progress(self, i, loops=0, cyclic=True, easefn="linear"):
        t = i / self.timeline.duration
        if loops == 0:
            return AnimationTime(t, t, 0, easefn)
        else:
            loop_t, loop_index = self._loop(t, times=loops, cyclic=cyclic)
            return AnimationTime(t, loop_t, loop_index, easefn)