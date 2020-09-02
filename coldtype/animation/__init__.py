import math
from coldtype.helpers import loopidx, interp_dict
from coldtype.animation.timeable import Timing, Timeable, TimeableSet
from coldtype.animation.timeline import Timeline


class Frame():
    def __init__(self, i, animation, layers):
        self.i = i
        self.a = animation
        self.layers = layers


class LoopPhase():
    def __init__(self, is_transition, i, timeable):
        self.t = timeable
        self.i = i
        self.is_transition = is_transition
    
    def calc_state(self, states, e="eeio"):
        state = loopidx(states, self.t.index)
        if self.is_transition:
            next_state = loopidx(states, self.t.index+1)
            e = self.t.progress(self.i, easefn=e).e
            state = interp_dict(e, state.copy(), next_state)
        return state


class Loop(Timeline):
    def __init__(self, duration, segment_count, transition_length, loop=1, fps=30, storyboard=[0]):
        self.timeables = []
        self.transitions = []

        super().__init__(duration, fps=fps, storyboard=storyboard)

        idx = 0
        segment_count = int(math.floor(segment_count))
        segment_length = duration / segment_count
        segment_frames = int(math.floor(segment_length))
        leftover = duration % segment_frames

        for x in range(0, self.duration, segment_frames):
            if idx >= segment_count:
                continue

            start = x
            end = x + segment_frames
            if idx == segment_count-1:
                end += leftover
            
            self.timeables.append(Timeable(start, end, index=idx))

            if idx < segment_count - 1:
                tstart = end-transition_length
                tend = end+transition_length
                self.transitions.append(Timeable(tstart, tend, index=idx))
            
            idx += 1
        
        if loop:
            self.transitions.insert(0, Timeable(-transition_length, transition_length, index=-1))
            self.transitions.append(Timeable(self.duration-transition_length, self.duration+transition_length, index=idx-1))
    
    def current_clip(self, i):
        for t in self.timeables:
            if t.now(i):
                return t

    def current_transition(self, i):
        for t in self.transitions:
            if t.now(i):
                return t

    def current(self, i):
        clip = self.current_clip(i)
        transition = self.current_transition(i)
        if transition:
            return True, transition
        else:
            return False, clip

    def current_on_loop(self, i):
        if i < 0:
            i = self.duration + i
        is_transition, timeable = self.current(i)
        return is_transition, i, timeable
    
    def current_phase(self, i):
        return LoopPhase(*self.current_on_loop(i))