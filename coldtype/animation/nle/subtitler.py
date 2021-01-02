import json
from pathlib import Path
from coldtype.animation.sequence import Sequence, ClipTrack, Clip

class Subtitler(Sequence):
    def __init__(self, path, duration, fps=30, storyboard=[0]):
        self.path = Path(path).expanduser().absolute()
        self.path.parent.mkdir(exist_ok=True, parents=True)
        try:
            self.data = json.loads(self.path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = dict(tracks=[dict(clips=[])])
        
        tracks = []
        for tidx, t in enumerate(self.data.get("tracks")):
            clips = []
            for cidx, c in enumerate(t.get("clips")):
                clips.append(Clip(c.get("text"), c.get("start"), c.get("end"), cidx, tidx))
            tracks.append(ClipTrack(self, clips, []))
        
        super().__init__(duration, fps, storyboard, tracks)
    
    def persist(self):
        self.conform()
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    def conform(self):
        clips = self.data["tracks"][self.workarea_track]["clips"]
        clips = sorted(clips, key=lambda c: c["start"])
        for cidx, clip in enumerate(clips):
            try:
                next_clip = clips[cidx+1]
            except IndexError:
                next_clip = None
            if next_clip:
                if clip["end"] > next_clip["start"]:
                    clip["end"] = next_clip["start"]
    
    def clips(self, tidx):
        return self.data["tracks"][tidx]["clips"]
    
    def remove_clip_at_frame(self, fi, tidx):
        clips = self.clips(tidx)
        clips = [c for c in clips if c["start"] != fi]
        return sorted(clips, key=lambda c: c["start"])
    
    def overwrite_clips(self, clips, tidx):
        self.data["tracks"][tidx]["clips"] = clips
    
    def delete_clip(self, fi):
        clips = self.remove_clip_at_frame(fi, self.workarea_track)
        self.overwrite_clips(clips, self.workarea_track)
    
    def add_clip(self, fi, text):
        clips = self.remove_clip_at_frame(fi, self.workarea_track)
        end = None
        for cidx, c in enumerate(clips):
            if c["start"] > fi:
                end = c["start"]
        if end is None:
            end = self.duration
        clips.append(dict(text=text, start=fi, end=end))
        self.overwrite_clips(clips, self.workarea_track)
    
    def cut_clip(self, fi):
        clips = self.clips(self.workarea_track)
        for c in clips:
            if c["start"] <= fi < c["end"]:
                c["end"] = fi
        self.overwrite_clips(clips, self.workarea_track)
    
    def extend_clip(self, fi):
        clips = self.clips(self.workarea_track)
        for c in clips:
            if c["start"] <= fi:
                c["end"] = fi
        self.overwrite_clips(clips, self.workarea_track)