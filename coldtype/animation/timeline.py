from coldtype.animation import Timeable


class Timeline(Timeable):
    __name__ = "Generic"

    def __init__(self, duration, fps=30, storyboard=[0], tracks=[]):
        self.fps = fps
        self.start = 0
        self.end = duration
        self.tracks = tracks
        self.storyboard = storyboard
        if len(self.storyboard) == 0:
            self.storyboard.append(0)
        self.storyboard.sort()
    
    def __str__(self):
        return "<coldtype.animation.timeline({:s}):{:04d}f@{:02.2f}fps[{:s}]>".format(self.__name__, self.duration, self.fps, ",".join([str(i) for i in self.storyboard]))
    
    def __getitem__(self, item):
        if isinstance(item, str):
            for t in self.tracks:
                if hasattr(t, "name") and t.name == item:
                    return t
        else:
            return self.tracks[item]