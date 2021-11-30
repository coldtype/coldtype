from coldtype.time.timeable import Timeable, Easeable


class Timeline(Timeable):
    """
    General base class for any kind of timeline or sequence, in the NLE sense

    * ``fps`` is `frames-per-second`, and defaults to 30
    * ``storyboard`` is useful if you want to always see a given frame when your animation loads for the first time, or you'd like to see multiple frames, i.e. ``storyboard=[0, 5]`` to see both frame 0 and frame 5 in the viewer
    * ``tracks`` is mostly used internally by subclasses that process external data from another NLE or data source like subtitles
    * ``jumps`` can be used to mark "jump-points" within a timeline, for easy skipping around with the up/down arrows (akin to up/down arrow movements in NLEs)
    """

    __name__ = "Generic"

    def __init__(self,
        duration,
        fps=30,
        timeables=None,
        storyboard=None,
        jumps=None,
        ):
        self.fps = fps
        self.start = 0
        self.end = duration

        self.timeables = self._flatten(timeables)

        self._jumps = [self.start, *(jumps or []), self.end-1]
        
        if not storyboard:
            self.storyboard = [0]
        else:
            self.storyboard = storyboard
        if len(self.storyboard) == 0:
            self.storyboard.append(0)
        self.storyboard.sort()
    
    def _flatten(self, timeables):
        ts = []
        for t in timeables:
            if isinstance(t, Timeable):
                ts.append(t)
            else:
                ts.extend(self._flatten(t))
        return ts
    
    def jumps(self):
        return self._jumps
    
    def text_for_frame(self, fi):
        return ""
    
    def __str__(self):
        return "<coldtype.time.timeline({:s}):{:04d}f@{:02.2f}fps[{:s}]>".format(self.__name__, self.duration, self.fps, ",".join([str(i) for i in self.storyboard]))
    
    def __getitem__(self, index):
        return self.timeables[index]

    def at(self, i) -> Easeable:
        return Easeable(self.timeables, i)
    
    def _keyed(self, k):
        k = str(k)
        all = []
        if isinstance(k, str):
            for c in self.timeables:
                if c.name == k:
                    all.append(c)
        
        if len(all) == 0:
            return Timeable(-1, -1)
        return all

    def k(self, *keys):
        if len(keys) > 1:
            es = [self.k(k) for k in keys]
            return self._flatten(es)
        else:
            return self._flatten(self._keyed(keys[0]))
    
    def ki(self, key, fi):
        """(k)eyed-at-(i)ndex"""

        if not isinstance(key, str):
            try:
                es = [self.ki(k, fi).t for k in key]
                return Easeable(self._flatten(es), fi)
            except TypeError:
                pass
        
        return Easeable(self._keyed(key), fi)
    
    @property
    def tstart(self):
        if self._start > -1:
            return self._start
        _start = -1
        for t in self.timeables:
            ts = t.start
            if _start == -1:
                _start = ts
            elif ts < _start:
                _start = ts
        return _start

    @property
    def tend(self):
        if self._end > -1:
            return self._end
        _end = -1
        for t in self.timeables:
            te = t.end
            if _end == -1:
                _end = te
            elif te > _end:
                _end = te
        return _end