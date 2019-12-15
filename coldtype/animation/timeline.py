

class Timeline():
    __name__ = "Generic"

    def __init__(self, duration, fps=30, storyboard=[0], workareas=None):
        self.fps = fps
        self.duration = round(duration)
        self.storyboard = storyboard
        if len(self.storyboard) == 0:
            self.storyboard.append(0)
        self.storyboard.sort()
        if workareas:
            self.workareas = workareas
        else:
            self.workareas = [range(0, self.duration+1)]

        if not hasattr(self, "tracks"):
            self.tracks = []
    
    def __str__(self):
        return "<Timeline({:s}):{:04d}f@{:02.2f}fps[{:s}]>".format(self.__name__, self.duration, self.fps, ",".join([str(i) for i in self.storyboard]))
    
    def __getitem__(self, item):
        if isinstance(item, str):
            for t in self.tracks:
                if hasattr(t, "name") and t.name == item:
                    return t
        else:
            return self.tracks[item]