from coldtype.time.timeline import Timeline, Timeable


class AsciiTimeline(Timeline):
    __name__ = "AsciiTimeline"

    def __init__(self,
        multiplier:int,
        fps:float,
        ascii:str=None,
        sort_keys=False,
        **kwargs
        ):
        if isinstance(fps, str):
            ascii = fps
            fps = 30
        lines = [l.rstrip() for l in ascii.splitlines() if l.strip()]
        ml = max([len(l) for l in lines])
        super().__init__(multiplier*ml, fps=fps, **kwargs)

        self.multiplier = multiplier
        
        clips = []

        unclosed_clip = None
        for l in lines:
            clip_start = None
            clip_name = None
            if unclosed_clip:
                clip_start, clip_name = unclosed_clip
                unclosed_clip = None
            looped_clip_end = None
            for idx, c in enumerate(l):
                if c == "]":
                    if clip_start is not None and clip_name is not None:
                        clips.append(Timeable(clip_start, idx*multiplier,
                            name=clip_name))
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
                    clips.append(Timeable(clip_start, self.duration+looped_clip_end,
                        name=clip_name))
                    clip_start = None
                    clip_name = None
            
            if clip_start is not None and clip_name is not None:
                unclosed_clip = (clip_start, clip_name)
        
        if sort_keys:
            self.clips = sorted(clips, key=lambda c: c.text)
        else:
            self.clips = clips

    def __getitem__(self, item):
        if isinstance(item, str):
            for c in self.clips:
                if c.name == item:
                    return c
        else:
            return self.clips[item]