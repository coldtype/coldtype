from typing import List

from coldtype.time.timeable import Timeable, Easeable
from coldtype.time.timeline import Timeline
from coldtype.geometry.rect import Rect


class AsciiTimeline(Timeline):
    __name__ = "AsciiTimeline"

    def __init__(self,
        multiplier:int,
        fps:float,
        ascii:str=None,
        **kwargs
        ):
        if isinstance(fps, str):
            ascii = fps
            fps = 30
        lines = [l.rstrip() for l in ascii.splitlines() if l.strip()]
        ml = max([len(l) for l in lines]) - 1
        super().__init__(multiplier*ml, fps=fps, **kwargs)

        self.multiplier = multiplier
        
        clips = []
        unclosed_clip = None

        for lidx, l in enumerate(lines):
            clip_start = None
            clip_name = None
            instant_clip = None

            if unclosed_clip:
                clip_start, clip_name = unclosed_clip
                unclosed_clip = None
            looped_clip_end = None
            for idx, c in enumerate(l):
                if c == "]":
                    if clip_start is not None and clip_name is not None:
                        clips.append(Timeable(
                            clip_start,
                            (idx+1)*multiplier,
                            name=clip_name,
                            data=dict(line=lidx),
                            timeline=self))
                    else:
                        looped_clip_end = idx*multiplier
                    clip_start = None
                    clip_name = None
                elif c == "[":
                    clip_start = idx*multiplier
                    clip_name = ""
                elif c not in [" ", "-", "|", "<", ">"]:
                    if clip_name is None:
                        if instant_clip is not None:
                            instant_clip += c
                        else:
                            instant_clip = c
                            clip_start = idx*multiplier
                    else:
                        clip_name += c
                if instant_clip and c == " ":
                    clips.append(Timeable(
                        clip_start,
                        clip_start+1,
                        name=instant_clip,
                        data=dict(line=lidx),
                        timeline=self))
                    clip_start = None
                    instant_clip = None
            
            if instant_clip:
                clips.append(Timeable(
                    clip_start,
                    clip_start+1,
                    name=instant_clip,
                    data=dict(line=lidx),
                    timeline=self))
            
            if looped_clip_end:
                if clip_start is not None and clip_name is not None:
                    clips.append(Timeable(
                        clip_start,
                        self.duration+looped_clip_end,
                        name=clip_name,
                        data=dict(line=idx),
                        timeline=self))
                    clip_start = None
                    clip_name = None
            
            if clip_start is not None and clip_name is not None:
                unclosed_clip = (clip_start, clip_name)
        
        self.clips:List[Timeable] = []
        self.clips = clips
        
        for cidx, clip in enumerate(self.clips):
            clip.index = cidx
    
    def _keyed(self, k):
        k = str(k)
        all = []
        if isinstance(k, str):
            for c in self.clips:
                if c.name == k:
                    all.append(c)
        return all
    
    def ki(self, key, fi):
        """(k)eyed-at-(i)ndex"""

        if not isinstance(key, str):
            try:
                es = [self.ki(k, fi).t for k in key]
                return Easeable(es, fi)
            except TypeError:
                pass

        # all = []
        # key = str(key)

        # for c in self.clips:
        #     if c.name == key:
        #         all.append(c)
        
        # if len(all) > 0:
        #     return Easeable(all, fi)
        
        return Easeable(self._keyed(key), fi)

    def __getitem__(self, item) -> Easeable:
        try:
            if isinstance(item[1], int):
                item, fi = item
                return self.ki(item, fi)

        except TypeError:
            return self._keyed(item)
    
    def now(self, fi, line=None, first=False, filter_fn=None):
        matches = []
        for clip in self.clips:
            if clip.start <= fi < clip.end:
                if line is not None:
                    if clip.data["line"] != line:
                        continue
                matches.append(clip)
        if filter_fn:
            matches = list(filter(filter_fn, matches))
        if first:
            return Easeable(matches[0], fi) if matches else Easeable(Timeable(-2, -1, -1), fi)
        return [Easeable(m, fi) for m in matches]
    
    def rmap(self, r=Rect(1000, 1000)):
        """
        Rect-map, i.e. a representation of this ascii timeline as a 2D map of rectangles
        """
        from coldtype.geometry.rect import Rect
        out = {}
        for clip in self.clips:
            sc = r.w / self.duration
            out[clip.name] = Rect(clip.start * sc, 0, clip.duration * sc, r.h)
        return out