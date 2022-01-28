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
        eases:dict=None,
        **kwargs
        ):
        if isinstance(fps, str):
            ascii = fps
            fps = 30
        
        lines = [l.rstrip() for l in ascii.splitlines() if l.strip()]
        ml = max([len(l) for l in lines]) - 1

        self.multiplier = multiplier
        self.keyframes = self._norm_keyframes(keyframes)
        self.eases = eases

        clips = []
        unclosed_clip = None
        duration = round(multiplier*ml)

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
                            round((idx)*multiplier)+multiplier,
                            name=clip_name,
                            data=dict(line=lidx),
                            track=lidx-1,
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
                        track=lidx-1,
                        timeline=self))
                    instant_clip = None
            
            if instant_clip:
                clips.append(Timeable(
                    clip_start,
                    clip_start,
                    name=instant_clip,
                    data=dict(line=lidx),
                    track=lidx-1,
                    timeline=self))
            
            if looped_clip_end:
                if clip_start is not None and clip_name is not None:
                    clips.append(Timeable(
                        clip_start,
                        duration+looped_clip_end,
                        name=clip_name,
                        data=dict(line=idx),
                        track=lidx-1,
                        timeline=self))
                    clip_start = None
                    clip_name = None
            
            if clip_start is not None and clip_name is not None:
                unclosed_clip = (clip_start, clip_name)
        
        clips = sorted(clips, key=lambda c: c.start)
        for cidx, clip in enumerate(clips):
            clip.idx = cidx
        
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
    
    def _find_kf_easer(self, ease, eases):
        for t in self.timeables:
            if t.name.startswith("~") and t.name[1:] in eases.keys():
                if ease.start <= t.start < ease.end:
                    return eases[t.name[1:]]
        return "eeio"
    
    def keyframe_current(self, fi, keyframes, lines=None):
        for c1, c2 in self.enumerate(lines=lines, pairs=True, edges=True, filter=keyframes.keys()):
            start, end = c1.start, c2.start

            if c2.start < c1.end:
                end += self.duration
                if fi < c1.start:
                    fi += self.duration

            t = Timeable(start, end,
                name=f"_kf_{c1.name}/{c2.name}",
                timeline=self)
            
            if t.now(fi):
                return [fi, t, c1, c2]
    
    def kf(self, easefn=None, fi=None, lines=None, keyframes=None, eases=None, offset=0):
        fi = self._norm_held_fi(fi)

        if keyframes is None:
            keyframes = self.keyframes
        else:
            keyframes = self._norm_keyframes(keyframes)

        if offset:
            # if callable(offset):
            #     res_ = self.keyframe_current(fi % self.duration, keyframes, lines)
            #     if res_:
            #         _, t, c1, c2 = res_
            #         fi = fi + offset(f"{c1.name}->{c2.name}")
            #     else:
            #         fi = fi + offset(None)
            # else:
            fi = fi + offset
        
        fi = fi % self.duration

        res = self.keyframe_current(fi, keyframes, lines)
    
        if res:
            fi, t, c1, c2 = res
            if c1.name == c2.name:
                return keyframes[c1.name]
            else:
                easer = easefn
                if easer is None:
                    if eases or self.eases:
                        easer = self._find_kf_easer(t, eases or self.eases)
                    else:
                        easer = "eeio"
                
                return interp_dict(
                    t.at(fi).e(easer, 0),
                    keyframes[c1.name],
                    keyframes[c2.name])
    
        return list(keyframes.values())[0]
    
    def enumerate(self, lines=None, pairs=False, edges=False, filter=None):
        matches = []
        for c in self.timeables:
            match = False
            if c.name.startswith("~"):
                match = False
            elif filter and c.name not in filter:
                match = False
            elif lines is not None:
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
    
    def inflate(self, lines=None):
        for a, b in self.enumerate(pairs=True, lines=lines):
            if a.start == a.end:
                if a.start < b.start:
                    a.end = b.start
                else:
                    a.end = self.duration
        return self
    
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