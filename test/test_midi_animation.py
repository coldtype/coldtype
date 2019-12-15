from coldtype.animation import *

def render(f):
    pass

mf = MidiTimeline.ReadFromFile(sibling(__file__, "test_midi/test_midi.mid"))
animation = Animation(render, (1920, 1080), bg=0)