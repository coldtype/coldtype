import enum
from coldtype.time.timeline import Timeline, Timeable


class AsciiTimeline(Timeline):
    __name__ = "AsciiTimeline"

    def __init__(self,
        multiplier:int,
        fps:float,
        ascii:str=None,
        sort=False,
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
                    clip_name += c
            
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
        
        if sort:
            self.clips = sorted(clips, key=lambda c: c.name)
        else:
            self.clips = clips
        
        for cidx, clip in enumerate(self.clips):
            clip.index = cidx

    def __getitem__(self, item):
        if isinstance(item, str):
            for c in self.clips:
                if c.name == item:
                    return c
        else:
            return self.clips[item]
    
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
            return matches[0] if matches else None
        return matches