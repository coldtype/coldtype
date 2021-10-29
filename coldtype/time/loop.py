import math
from coldtype.interpolation import loopidx, interp_dict
from coldtype.time.timeable import Timing, Timeable, TimeableSet
from coldtype.time.timeline import Timeline


class LoopPhase():
    """
    Clip-like representation of a segment of a Loop, most likely retrieved from :meth:`~coldtype.time.loop.Loop.current_phase`

    * Standard ``Timeable`` available as ``.t``
    * ``.is_transition`` indicates if phase represents a transition
    """
    def __init__(self, is_transition:bool, i:int, timeable:Timeable):
        self.t = timeable
        self.i = i
        self.is_transition = is_transition
    
    def calc_state(self, states, e="eeio"):
        """
        Calculate progress of the loop phase, based on an easing fuction, ``e``

        * ``e=`` takes a mnemonic as enumerated in :func:`coldtype.time.easing.ease`
        """
        state = loopidx(states, self.t.index)
        if self.is_transition:
            next_state = loopidx(states, self.t.index+1)
            e = self.t.progress(self.i, easefn=e, to1=1).e
            state = interp_dict(e, state.copy(), next_state)
        return state
    
    calcState = calc_state


class Loop(Timeline):
    """
    Construct for quickly developing animations based on loop
    
    Can be used as a ``timeline=`` for an ``@animation``
    """
    def __init__(self, duration, transition_length, states,
        loop=1, fps=30, storyboard=[0]):

        self.timeables = []
        self.transitions = []

        super().__init__(duration, fps=fps, storyboard=storyboard)

        try:
            segment_count = len(states)
            self.states = states
        except:
            segment_count = states
            self.states = None

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
    
    def jumps(self):
        js = self._jumps
        for t in self.timeables:
            js.insert(-1, t.start+int(t.duration/2))
        return js
    
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
    
    def current_phase(self, i) -> LoopPhase:
        """
        Get current phase of the Loop as a ``LoopPhase``
        """
        return LoopPhase(*self.current_on_loop(i))
    
    currentPhase = current_phase
    
    def current_state(self, i, e="eeio") -> LoopPhase:
        """
        Get current state of the Loop as a dict (provided states were passed to init)
        """
        return LoopPhase(*self.current_on_loop(i)).calc_state(self.states, e)

    currentState = current_state