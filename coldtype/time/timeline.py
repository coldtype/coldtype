from coldtype.time import Timeable


class Timeline(Timeable):
    """
    General base class for any kind of timeline or sequence, in the NLE sense

    * ``fps`` is `frames-per-second`, and defaults to 30
    * ``storyboard`` is useful if you want to always see a given frame when your animation loads for the first time, or you'd like to see multiple frames, i.e. ``storyboard=[0, 5]`` to see both frame 0 and frame 5 in the viewer
    * ``tracks`` is mostly used internally by subclasses that process external data from another NLE or data source like subtitles
    * ``jumps`` can be used to mark "jump-points" within a timeline, for easy skipping around with the up/down arrows (akin to up/down arrow movements in NLEs)
    """

    __name__ = "Generic"

    def __init__(self, duration, fps=30, storyboard=None, tracks=None, jumps=None):
        self.fps = fps
        self.start = 0
        self.end = duration
        self.tracks = tracks or []
        self._jumps = [self.start, *(jumps or []), self.end-1]
        
        if not storyboard:
            self.storyboard = [0]
        else:
            self.storyboard = storyboard
        if len(self.storyboard) == 0:
            self.storyboard.append(0)
        self.storyboard.sort()
    
    def jumps(self):
        return self._jumps
    
    def text_for_frame(self, fi):
        return ""
    
    def __str__(self):
        return "<coldtype.time.timeline({:s}):{:04d}f@{:02.2f}fps[{:s}]>".format(self.__name__, self.duration, self.fps, ",".join([str(i) for i in self.storyboard]))
    
    def __getitem__(self, item):
        if isinstance(item, str):
            for t in self.tracks:
                if hasattr(t, "name") and t.name == item:
                    return t
        else:
            return self.tracks[item]