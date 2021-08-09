import json, re
from pathlib import Path
from coldtype.time.sequence import Sequence, ClipTrack, Clip
from coldtype.time.audio import Wavfile
from coldtype.text import Style, StyledString
from coldtype.pens.datpen import DATPen, DATPens
from coldtype.pens.dattext import DATText
from coldtype.geometry import Rect
from coldtype.color import hsl, bw
from coldtype.renderable.animation import animation
from coldtype.renderable import Overlay
from contextlib import contextmanager


class Subtitler(Sequence):
    def __init__(self, path, audio_path, duration=None, fps=30, storyboard=[0]):
        self.path = Path(path).expanduser().absolute()
        self.path.parent.mkdir(exist_ok=True, parents=True)
        
        self.audio_path = Path(audio_path).expanduser().absolute()
        self.wavfile = Wavfile(self.audio_path)

        if duration is None:
            duration = self.wavfile.framelength
        
        try:
            self.data = json.loads(self.path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = dict(workarea_track=0, tracks=[dict(clips=[])])
        
        tracks = []
        for tidx, t in enumerate(self.data.get("tracks")):
            clips = []
            for cidx, c in enumerate(t.get("clips")):
                cs = []
                txt = c.get("text")
                start = c.get("start")
                end = c.get("end")
                if "≈" in txt[1:]:
                    for lidx, ltxt in enumerate(txt.split("≈")):
                        if lidx > 0:
                            ltxt = "≈" + ltxt
                        cs.append(Clip(ltxt, start, end, cidx, tidx))
                else:
                    cs.append(Clip(txt, start, end, cidx, tidx))
                clips.extend(cs)
            tracks.append(ClipTrack(self, clips, []))
        
        super().__init__(duration, fps, storyboard, tracks, workarea_track=self.data["workarea_track"])

        if len(self.data["tracks"]) <= self.workarea_track:
            self.data["tracks"].append(dict(clips=[]))
            self.tracks.append(ClipTrack(self, [], []))
    
    def persist(self):
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    def conform(self, clips):
        clips = sorted(clips, key=lambda c: c["start"])
        for cidx, clip in enumerate(clips):
            try:
                next_clip = clips[cidx+1]
            except IndexError:
                next_clip = None
            if next_clip:
                if clip["end"] > next_clip["start"]:
                    clip["end"] = next_clip["start"]
        return clips
    
    def clips(self):
        clips = self.data["tracks"][self.workarea_track]["clips"]
        for cidx, c in enumerate(clips):
            c["idx"] = cidx
        return clips
    
    def text_for_frame(self, fi):
        clips = [c for c in self.clips() if c.get("start") == fi]
        if len(clips) > 0:
            return clips[0].get("text")
        else:
            return ""
    
    def remove_clip_at_frame(self, fi, clips):
        return [c for c in clips if c["start"] != fi]
    
    def overwrite_clips(self, clips):
        self.data["tracks"][self.workarea_track]["clips"] = self.conform(clips)
        self.persist()
    
    def delete_clip(self, fi, clips):
        clips = self.remove_clip_at_frame(fi, clips)
        self.overwrite_clips(clips)
    
    def add_clip(self, fi, text, clips):
        clips = self.remove_clip_at_frame(fi, clips)
        _, matches = self.closest(fi, +1, clips)
        end = None
        for (pos, cidx) in matches:
            if pos == "start":
                end = clips[cidx]["start"]
        if end is None:
            end = self.duration
        clips.append(dict(text=text, start=fi, end=end))
        self.overwrite_clips(clips)
    
    @contextmanager
    def active_clip(self, fi, clips):
        cidx = self.current_clip_idx(fi, clips)
        if cidx > -1:
            try:
                yield clips[cidx]
            finally:
                self.overwrite_clips(clips)
    
    def cut_clip(self, fi, clips):
        with self.active_clip(fi, clips) as c:
            c["end"] = fi
        
    def mod_clip_text(self, fi, clips, fn):
        with self.active_clip(fi, clips) as c:
            ctxt = c["text"]
            csym = None
            if ctxt[0] in ["≈", "*", "+"]:
                csym = ctxt[0]
                ctxt = ctxt[1:]
            c["text"] = fn(csym, ctxt)

    def closest(self, fi, direction, clips, ignore_on=False):
        closest = []
        closest_cut = 5000
        closest_frame = None

        for c in clips:
            if direction < 0:
                sc = fi - c["start"]
                ec = fi - c["end"]
            elif direction > 0:
                sc = c["start"] - fi
                ec = c["end"] - fi
            
            if sc >= 0 and sc < closest_cut:
                if sc == 0 and ignore_on:
                    pass
                else:
                    closest_cut = sc
                    closest_frame = c["start"]
            if ec >= 0 and ec < closest_cut:
                if ec == 0 and ignore_on:
                    pass
                else:
                    closest_cut = ec
                    closest_frame = c["end"]
        
        for c in clips:
            if c["start"] == closest_frame:
                closest.append(["start", c["idx"]])
            elif c["end"] == closest_frame:
                closest.append(["end", c["idx"]])
        
        if not ignore_on:
            if closest_frame == fi and len(closest) == 1:
                return self.closest(fi, direction, clips, ignore_on=True)
        
        return closest_frame == fi, closest
    
    def closest_to_playhead(self, fi, which, clips):
        on_cut, matches = self.closest(fi, which, clips)
        if not on_cut:
            for (pos, cidx) in matches:
                clips[cidx][pos] = fi
        self.overwrite_clips(clips)
    
    # def prev_and_next(self, fi):
    #     clips = self.clips(self.workarea_track)
    #     curr_clip = None
    #     next_clip = None
    #     prev_clip = None
        
    #     for cidx, clip in enumerate(clips):
    #         if curr_clip and not next_clip:
    #             if clip["start"] > fi:
    #                 next_clip = clip
            
    #         if clip["end"] <= fi:
    #             prev_clip = clip
            
    #         if clip["start"] <= fi < clip["end"]:
    #             curr_clip = clip
        
    #     return prev_clip, curr_clip, next_clip, clips

    def current_clip_idx(self, fi, clips):
        for clip in clips:
            if clip["start"] <= fi < clip["end"]:
                return clip["idx"]
        return -1
    
    # def prev(self, clip, clips):
    #     for cidx, c in enumerate(clips):
    #         if c == clip:
    #             try:
    #                 return clips[cidx-1]
    #             except IndexError:
    #                 return None
    
    # def next(self, clip, clips):
    #     for cidx, c in enumerate(clips):
    #         if c == clip:
    #             try:
    #                 return clips[cidx+1]
    #             except IndexError:
    #                 return None

    def process_state(self, rs, fi, clips=None):
        if not clips:
            clips = self.clips()
    
    def clip_timeline(self, fi, far, sw=30, sh=50, font_name=None):
        seq = DATPens()

        seq += (DATPen()
            .rect(Rect(0, 0, (self.duration * sw), sh)).f(bw(0.5, 0.35)))

        for tidx, t in enumerate(self.tracks):
            for cgidx, cg in enumerate(t.clip_groups):
                for cidx, c in enumerate(cg.clips):
                    r = Rect(c.start*sw, sh*tidx, (c.duration*sw)-2, sh)
                    current = c.start-25 <= fi <= c.end+25
                    if current:
                        seq.append(DATPens([
                            (DATPen()
                                .rect(r)
                                .f(hsl(cgidx*0.4+tidx*0.2, 0.75).lighter(0.2))),
                            (DATText(c.input_text,
                                Style(font_name, 24, load_font=0, fill=bw(0, 1 if tidx == self.workarea_track else 0.5)),
                                r.inset(3, 8)))]))

        on_cut = fi in self.jumps()

        seq.translate(far.w/2 - fi*sw, 10)

        seq.append(DATPen()
            .rect(far.take(sh*len(self.tracks)+20, "mny").take(6 if on_cut else 2, "mdx"))
            .f(hsl(0.9, 1) if on_cut else hsl(0.8, 0.5)))
        
        return seq


class lyric_editor(animation):
    def __init__(self, timeline:Subtitler, rect=(1080, 1080), data_font="Times", **kwargs):
        self.data_font = data_font
        super().__init__(
            rect=rect,
            timeline=timeline,
            rstate=1,
            watch=[timeline.path],
            **kwargs)

    def runpost(self, res, rp, rs):
        res = super().runpost(res, rp, rs)
        f:Frame = rp.args[0]
        if Overlay.Timeline in rs.overlays:
            self.timeline.process_state(rs, f.i)
            seq = self.timeline.clip_timeline(f.i, f.a.r, font_name=self.data_font)
            return DATPens([res, seq])
        return res

if __name__ == "<run_path>":
    from coldtype.test import recmono, co

    tl = Subtitler(
        #"test/lyric_data.json",
        #"test/media/helloworld.wav",
        "test/lyric_data2.json",
        "~/Type/fouchet/de/media/jitterbugging.wav",
        storyboard=[19])

    @lyric_editor(tl, bg=0, data_font=recmono)
    def lyric_entry2(f, rs):
        def render_clip_fn(f, idx, clip, ftext):
            if "stylized" in clip.styles:
                return ftext.upper(), Style(co, 150, wdth=0.5, tu=50, fill=hsl(0.61, s=1, l=0.7))
            return ftext, Style(recmono, 100, fill=1)

        return (tl.clip_group(0, f.i)
            .pens(f, render_clip_fn, f.a.r.inset(50))
            #.f(1)
            #.xa()
            #.align(f.a.r)
            .remove_futures())