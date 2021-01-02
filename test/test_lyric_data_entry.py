from coldtype.test import *
from coldtype.animation.sequence import Sequence, ClipTrack, Clip
from coldtype.animation.audio import Wavfile
import json

fnt = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")
audio = Wavfile(__sibling__("media/helloworld.wav"))

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
    
    def remove_clip_at_frame(self, fi, tidx):
        clips = self.data["tracks"][tidx]["clips"]
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
        

tl = Subtitler("test/lyric_data.json", audio.framelength, storyboard=[3])

@animation(timeline=tl, audio=audio.path, bg=0, rstate=1, watch=[tl.path])
def lyric_entry(f, rs):
    def render_clip_fn(f, idx, clip, ftext):
        return ftext, Style(fnt, 150, wdth=0.5, wght=0.5)

    cg = tl.clip_group(0, f.i)
    clips = tl.data["tracks"][tl.workarea_track]["clips"]
    if rs.text:
        tl.add_clip(f.i, rs.text)
        tl.persist()
    elif rs.cmd:
        if rs.cmd == "d":
            tl.delete_clip(f.i)
            tl.persist()
        if rs.cmd == "c":
            tl.persist()

    return (cg
        .pens(f, render_clip_fn, f.a.r)
        .f(hsl(0.9))
        .xa()
        .align(f.a.r)
        .remove_futures())
    #return DATPen().oval(f.a.r).f(0.1)