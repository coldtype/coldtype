from typing import Union

from coldtype.interpolation import interp_dict
from coldtype.time.timeline import Timeline, Timeable
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

        self.keyframes = self._norm_keyframes(keyframes)

        duration = round(multiplier*ml)

        #super().__init__(round(multiplier*ml), fps=fps, **kwargs)

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
                        if instant_clip:
                            instant_clip += c
                        else:
                            clip_start = round(idx*multiplier)
                            instant_clip = c
                    # if clip_name is None:
                    #     clips.append(Timeable(
                    #         round(idx*multiplier),
                    #         round(idx*multiplier),
                    #         name=c,
                    #         data=dict(line=lidx),
                    #         timeline=self))
                    else:
                        clip_name += c
                elif c in [" "] and instant_clip:
                    clips.append(Timeable(
                        clip_start,
                        clip_start,
                        name=instant_clip,
                        data=dict(line=lidx),
                        timeline=self))
                    instant_clip = None
            
            if instant_clip:
                clips.append(Timeable(
                    clip_start,
                    clip_start,
                    name=instant_clip,
                    data=dict(line=lidx),
                    timeline=self))
            
            if looped_clip_end:
                if clip_start is not None and clip_name is not None:
                    clips.append(Timeable(
                        clip_start,
                        duration+looped_clip_end,
                        name=clip_name,
                        data=dict(line=idx),
                        timeline=self))
                    clip_start = None
                    clip_name = None
            
            if clip_start is not None and clip_name is not None:
                unclosed_clip = (clip_start, clip_name)
        
        clips = sorted(clips, key=lambda c: c.start)
        for cidx, clip in enumerate(clips):
            clip.index = cidx
        
        super().__init__(duration, fps, clips, **kwargs)
    
    def _norm_keyframes(self, keyframes):
        if not keyframes:
            return {}

        if not isinstance(keyframes, dict):
            kfs = {}
            for idx, v in enumerate(keyframes):
                kfs[str(idx)] = v
            return kfs
        else:
            kfs = {}
            for k, v in keyframes.items():
                kfs[str(k)] = v
            return kfs
    
    def kf(self, easefn="eeio", fi=None, lines=None, keyframes=None):
        fi = self._norm_held_fi(fi)
        fi = fi % self.duration

        if keyframes is None:
            keyframes = self.keyframes
        else:
            keyframes = self._norm_keyframes(keyframes)

        for c1, c2 in self.enumerate(lines=lines, pairs=True, edges=True):
            start, end = c1.start, c2.start
            if c2.start < c1.end:
                end += self.duration
                if fi < c1.start:
                    fi += self.duration

            t = Timeable(start, end,
                name=f"_kf_{c1.name}/{c2.name}",
                timeline=self)
            
            if t.now(fi):
                return interp_dict(t.at(fi).e(easefn, 0), keyframes[c1.name], keyframes[c2.name])
    
        return list(keyframes.values())[0]
    
    def enumerate(self, lines=None, pairs=False, edges=False):
        matches = []
        for c in self.timeables:
            match = False
            if lines is not None:
                if c.data["line"] in lines:
                    match = True
            else:
                match = True
            
            if match:
                if edges and c.duration > 0:
                    matches.append(Timeable(c.start, c.start, -1, name=c.name, timeline=self))
                    matches.append(Timeable(c.end-1, c.end-1, -1, name=c.name, timeline=self))
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
    
    def rmap(self, r=Rect(1000, 1000)):
        """
        Rect-map, i.e. a representation of this ascii timeline as a 2D map of rectangles
        """
        from coldtype.geometry.rect import Rect
        out = {}
        for clip in self.timeables:
            sc = r.w / self.duration
            out[clip.name] = Rect(clip.start * sc, 0, clip.duration * sc, r.h)
        return out
    
    def __getitem__(self, item):
        return self._keyed(item)