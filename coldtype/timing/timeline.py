from collections import defaultdict
from re import match
from coldtype.timing.timeable import Timeable, Easeable
from typing import List


class Timeline(Timeable):
    """
    General base class for any kind of timeline or sequence, in the NLE sense

    * `fps` is `frames-per-second`, and defaults to 30
    * `storyboard` is useful if you want to always see a given frame when your animation loads for the first time, or you'd like to see multiple frames, i.e. `storyboard=[0, 5]` to see both frame 0 and frame 5 in the viewer
    * `tracks` is mostly used internally by subclasses that process external data from another NLE or data source like subtitles
    * `jumps` can be used to mark "jump-points" within a timeline, for easy skipping around with the up/down arrows (akin to up/down arrow movements in NLEs)
    """

    __name__ = "Generic"

    def __init__(self,
        duration=None,
        fps=30,
        timeables=None,
        storyboard=None,
        jumps=None,
        start=None,
        end=None,
        findWords=True,
        name=None,
        ):
        self.timeables:List[Timeable] = self._flatten(timeables)
        
        self.name = name
        self.fps = fps
        
        if start is not None:
            self.start = start
        else:
            self.start = 0
        
        if end is not None:
            self.end = end
        else:
            if duration is None:
                if len(self.timeables) > 0:
                    #self.start = min([t.start for t in self.timeables])
                    self.end = max([t.end for t in self.timeables])
                else:
                    self.end = 0
            else:
                self.end = duration

        self._holding = -1

        self._jumps = [self.start, *(jumps or []), self.end-1]
        
        if not storyboard:
            self.storyboard = [0]
        else:
            self.storyboard = storyboard
        if len(self.storyboard) == 0:
            self.storyboard.append(0)
        self.storyboard.sort()

        if findWords:
            self.words = self.interpretWords(findWords)
        else:
            self.words = None
    
    def _flatten(self, timeables):
        if not timeables:
            return []
        
        ts = []
        for t in timeables:
            if isinstance(t, Timeable):
                ts.append(t)
            else:
                ts.extend(self._flatten(t))
        return ts
    
    def jumps(self):
        return self._jumps
    
    def tracks(self):
        ts = defaultdict(lambda: [])
        for t in self.timeables:
            ts[t.track].append(t)
        return ts
    
    def text_for_frame(self, fi):
        return ""
    
    def __str__(self):
        return "<coldtype.timing.timeline({:s}):{:04d}f@{:02.2f}fps[{:s}]>".format(self.__name__, self.duration, self.fps, ",".join([str(i) for i in self.storyboard]))
    
    def __getitem__(self, index):
        return self.timeables[index]
    
    def __len__(self):
        return len(self.timeables)
    
    def __contains__(self, key):
        for t in self.timeables:
            if t.name == key:
                return True
        return False
    
    def hold(self, i):
        self._holding = i
        if self.words:
            self.words.hold(i)
        return self

    def at(self, i) -> Easeable:
        return Easeable(self.timeables, i)
    
    def timeable(self, name=None) -> Timeable:
        return Timeable(
            self.start,
            self.duration,
            name=name or "Clip",
            data=dict(),
            track=0,
            timeline=self)
    
    def easeable(self, i=None, name=None) -> Easeable:
        return Easeable(self.timeable(name), i or self._holding)
    
    def addClip(self, name=None, start=0, end=0):
        self.timeables.append(self.timeable(name).retime(start, -end))
        return self
    
    def _keyed(self, k):
        k = str(k)
        all = []
        if isinstance(k, str):
            for c in self.timeables:
                if k == "*" or c.name == k:
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
    
    def _norm_held_fi(self, fi=None):
        if fi is None:
            if self._holding >= 0:
                return self._holding
            else:
                raise Exception("Must .hold or provide fi=")
        return fi % self.duration
    
    def ki(self, key, fi=None):
        """(k)eyed-at-(i)ndex"""

        fi = self._norm_held_fi(fi)

        if not isinstance(key, str):
            try:
                es = [self.ki(k, fi).t for k in key]
                return Easeable(self._flatten(es), fi)
            except TypeError:
                pass
        
        return Easeable(self._keyed(key), fi)
    
    def current(self, track=None, fi=None) -> Easeable:
        fi = self._norm_held_fi(fi)

        matches = []
        for t in self.timeables:
            if t.now(fi):
                if track is not None and t.track != track:
                    continue
                matches.append(t)
        
        return Easeable(matches, fi)
    
    def latest(self, track=None, fi=None) -> Easeable:
        fi = self._norm_held_fi(fi)

        matches = []
        _fi = fi
        while _fi >= 0 and not matches:
            matches = self.current(track=track, fi=_fi).t or []
            _fi -= 1
        
        return Easeable(matches, fi)
    
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
    
    def shift(self, prop, fn):
        for t in self.timeables:
            attr = getattr(t, prop)
            if callable(fn):
                setattr(t, prop, fn(t))
            else:
                setattr(t, prop, attr + fn)
        return self
    
    def findWordsWorkarea(self, fi):
        if self.words:
            cg = self.words.currentGroup(fi)
            if cg:
                return [int(cg.start), int(cg.end)]
    
    def interpretWords(self, include="*"):
        from coldtype.timing.sequence import ClipTrack, Clip

        includes = []
        excludes = []

        if isinstance(include, str):
            for x in include.split(" "):
                if x == "*":
                    continue
                elif x.startswith("-"):
                    excludes.append(int(x[1:]))
                elif x.startswith("+"):
                    includes.append(int(x[1:]))

        clips = []
        styles = []

        for t in self.timeables:
            if len(includes) > 0:
                if t.track not in includes:
                    continue
            if len(excludes) > 0:
                if t.track in excludes:
                    continue

            if t.name.startswith("."):
                styles.append(Timeable(t.start, t.end, index=t.idx, name=t.name[1:], data=t.data, timeline=self, track=t.track))
            else:
                start = t.start
                end = t.end
                if t.start == t.end:
                    end = start + 1
                if t.name == "•":
                    start -= 1
                    end -= 1
                clips.append(Clip(t.name, start, end, t.idx, track=t.track))
        
        return ClipTrack(self, clips, None, Timeline(timeables=styles, findWords=False))