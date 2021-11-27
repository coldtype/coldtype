from typing import List, Union

from coldtype.interpolation import interp_dict
from coldtype.time.timeable import Timeable, Easeable
from coldtype.time.timeline import Timeline
from coldtype.geometry.rect import Rect


class AsciiTimeline(Timeline):
    __name__ = "AsciiTimeline"

    def __init__(self,
        multiplier:Union[int,float],
        fps:float,
        ascii:str=None,
        keyframes:dict=None,
        **kwargs
        ):
        if isinstance(fps, str):
            ascii = fps
            fps = 30
        lines = [l.rstrip() for l in ascii.splitlines() if l.strip()]
        ml = max([len(l) for l in lines]) - 1

        self.keyframes = keyframes or {}
        
        if not isinstance(self.keyframes, dict):
            kfs = {}
            for idx, v in enumerate(self.keyframes):
                kfs[str(idx)] = v
            self.keyframes = kfs

        super().__init__(round(multiplier*ml), fps=fps, **kwargs)

        self.multiplier = multiplier
        
        clips = []
        unclosed_clip = None

        for lidx, l in enumerate(lines):
            if l.startswith("#"):
                continue
            
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
                            round((idx+1)*multiplier),
                            name=clip_name,
                            data=dict(line=lidx),
                            timeline=self))
                    else:
                        looped_clip_end = round(idx*multiplier)
                    clip_start = None
                    clip_name = None
                elif c == "[":
                    clip_start = round(idx*multiplier)
                    clip_name = ""
                elif c not in [" ", "-", "|", "<", ">"]:
                    if clip_name is None:
                        clips.append(Timeable(
                            round(idx*multiplier),
                            round(idx*multiplier),
                            name=c,
                            data=dict(line=lidx),
                            timeline=self))
                    else:
                        clip_name += c
            
            # if instant_clip:
            #     clips.append(Timeable(
            #         clip_start,
            #         clip_start,
            #         name=instant_clip,
            #         data=dict(line=lidx),
            #         timeline=self))
            
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
        self.clips = sorted(clips, key=lambda c: c.start)
        
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
    
    def kf(self, fi, easefn="eeio", lines=None):
        fi = fi % self.duration

        for c1, c2 in self.enumerate(lines=lines, pairs=True):
            start, end = c1.start, c2.start
            if c2.start < c1.end:
                end += self.duration
                if fi < c1.start:
                    fi += self.duration

            t = Timeable(start, end,
                name=f"_kf_{c1.name}/{c2.name}",
                timeline=self)
            if t.now(fi):
                return interp_dict(t.at(fi).e(easefn, 0), self.keyframes[c1.name], self.keyframes[c2.name])
    
        return list(self.keyframes.values())[0]
    
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

        except (IndexError, TypeError):
            return self._keyed(item)
    
    def enumerate(self, lines=None, pairs=False):
        matches = []
        for c in self.clips:
            if lines is not None:
                if c.data["line"] in lines:
                    matches.append(c)
            else:
                matches.append(c)
        
        for i, c in enumerate(matches):
            if pairs:
                if i < len(matches)-1:
                    yield c, matches[i+1]
                else:
                    yield c, matches[0]
            else:
                yield c
    
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