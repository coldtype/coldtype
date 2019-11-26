from coldtype import *
from enum import Enum
from random import random
import mido
import re

print("THIS ANIMATION")

VIDEO_OFFSET = 86313 # why is this?


def to_frames(seconds, fps):
    frames = int(round(float(seconds)*fps))
    if frames >= VIDEO_OFFSET:
        frames -= VIDEO_OFFSET
    return frames


class Marker():
    def __init__(self, fps, marker):
        self.marker = marker
        self.start = to_frames(marker.get("start"), fps)
        self.end = to_frames(marker.get("end"), fps)


class ClipType(Enum):
    ClearScreen = "ClearScreen"
    NewLine = "NewLine"
    Isolated = "Isolated"
    JoinPrev = "JoinPrev"


class ClipFlags(Enum):
    FadeIn = "FadeIn"
    FadeOut = "FadeOut"


class Clip():
    def __init__(self, clip, fps=None, markers=[], idx=None):
        self.idx = idx
        self.clip = clip
        self.styles = []
        self.position = 1
        self.joined = False
        self.joinPrev = None
        self.joinNext = None

        if isinstance(clip, dict):
            try:
                self.text, self.transform = clip.get("name").split("|||")
                try:
                    self.transform = eval(f"dict({self.transform})")
                except ValueError:
                    print("Could not eval transform spec")
                    self.transform = dict()
            except ValueError:
                self.text = clip.get("name")
                self.transform = dict()
            
            self.start = to_frames(clip.get("start"), fps)
            self.end = to_frames(clip.get("end"), fps)
            self.inpoint = to_frames(clip.get("inPoint"), fps)
            self.outpoint = to_frames(clip.get("outPoint"), fps)
            self.duration = self.end - self.start
            self.flags = {}

            self.type = ClipType.Isolated
            if self.text.startswith("*"):
                self.text = self.text[1:]
                self.type = ClipType.ClearScreen
            elif self.text.startswith("≈"):
                self.text = self.text[1:]
                self.type = ClipType.NewLine
            elif self.text.startswith("+"):
                self.text = self.text[1:]
                self.type = ClipType.JoinPrev
            
            if self.text.startswith("ƒ"):
                r = r"^([0-9]+)ƒ"
                self.text = self.text[1:]
                value = 3
                match = re.match(r, self.text)
                if match:
                    value = int(match[1])
                    self.text = re.sub(r, "", self.text)
                self.flags[ClipFlags.FadeIn] = value
            
            elif self.text.endswith("ƒ"):
                self.flags[ClipFlags.FadeOut] = 3

            for m in markers:
                if self.inpoint <= m.start and self.outpoint > m.end:
                    self.type = ClipType.NewLine #ClipType.ClearScreen
    
    def addJoin(self, clip, direction):
        if direction == -1:
            self.joinPrev = clip
        elif direction == 1:
            self.joinNext = clip
    
    def joinStart(self):
        if self.joinPrev:
            return self.joinPrev.joinStart()
        else:
            return self.start
    
    def joinEnd(self):
        if self.joinNext:
            return self.joinNext.joinEnd()
        else:
            return self.end
    
    def textForIndex(self, index):
        txt = self.text
        try:
            txt = self.text.split("/")[index]
        except:
            txt = self.text.split("/")[-1]
        return txt, self.addSpace

    def ftext(self):
        txt = self.text
        if self.type == ClipType.Isolated:
            return " " + txt
        else:
            return txt
    
    def __repr__(self):
        return "<TC:({:s}/{:04d}/{:04d}\"{:s}\")>".format([" -1", "NOW", " +1"][self.position+1], self.start, self.end, self.text)


class Timeline():
    def __init__(self, fps, duration, storyboard=[0], workareas=None):
        self.fps = fps
        self.duration = duration
        self.storyboard = storyboard
        if len(self.storyboard) == 0:
            self.storyboard.append(0)
        self.storyboard.sort()
        if workareas:
            self.workareas = workareas
        else:
            self.workareas = [range(0, self.duration+1)]


class AnimationFrame():
    def __init__(self, index, animation, filepath, layers):
        self.i = index
        self.a = animation
        self.filepath = filepath
        self.layers = layers

    def __repr__(self):
        return f"<AnimationFrame {self.i}>"

class Animation():
    def __init__(self, render, rect, timeline=None, bg=0, layers=None):
        self.render = render
        self.rect = rect
        self.r = self.rect
        self.cache = {}
        self.layers = layers

        if isinstance(timeline, Path):
            if str(timeline).endswith(".json"):
                jsondata = json.loads(timeline.read_text())
                meta = jsondata.get("metadata")
                fps = 1 / meta.get("frameRate")
                duration = int(round(int(meta.get("duration"))/int(meta.get("timebase"))))
                storyboard = []
                tof = lambda s: int(round(float(s)*fps))
                for m in jsondata.get("storyboard"):
                    storyboard.append(tof(m.get("start")))
                workareas = []
                workareas.append(
                    range(
                        max(0, tof(meta.get("inPoint"))),
                        tof(meta.get("outPoint"))+1
                        ))
                self.jsonfile = timeline
                self.timeline = Timeline(
                    fps,
                    duration,
                    storyboard=storyboard,
                    workareas=workareas
                )
                self.clipGroupsByTrack = []
                for track in jsondata.get("tracks"):
                    markers = [Marker(fps, m) for m in track.get("markers")]
                    clips = track.get("clips")
                    gcs = grouped_clips([Clip(c, fps=fps, markers=markers) for c in clips])
                    self.clipGroupsByTrack.append(gcs)
        elif isinstance(timeline, Timeline):
            self.timeline = timeline
        else:
            self.timeline = Timeline(30, 1)
        
        self.t = self.timeline # alias
        self.bg = normalize_color(bg)
    
    def progress(self, i, cyclic=False):
        if cyclic:
            a = (i / (self.timeline.duration/2))
            if a < 1:
                return a
            else:
                return 2 - a
        else:
            return i / self.timeline.duration
    
    def trackClipGroupForFrame(self, track_idx, frame_idx, styles=None):
        groups = self.clipGroupsByTrack[track_idx]
        for group in groups:
            if group.start <= frame_idx and group.end > frame_idx:
                style_groups = None
                if styles:
                    style_groups = []
                    for style in styles:
                        style_groups.append(self.trackClipGroupForFrame(style, frame_idx))
                return group.position(frame_idx, style_groups)


class ClipGroup():
    def __init__(self, index, clips):
        self.index = index
        self.clips = clips
        self.start = clips[0].start
        self.end = clips[-1].end

        for idx, clip in enumerate(clips):
            clip.idx = idx
    
    def styles(self):
        all_styles = set()
        for clip in self.clips:
            for style in clip.styles:
                all_styles.add(style)
        return all_styles
    
    def lines(self):
        lines = []
        line = []
        for clip in self.clips:
            if clip.type == ClipType.NewLine:
                lines.append(line)
                line = [clip]
            else:
                line.append(clip)
        if len(line) > 0:
            lines.append(line)
        return lines
    
    def position(self, idx, styles):
        for clip in self.clips:
            clip.joined = False
        for clip in self.clips:
            clip.styles = []
            if styles:
                for style in styles:
                    if style:
                        for style_clip in style.clips:
                            if clip.start >= style_clip.start and clip.end <= style_clip.end:
                                clip.styles.append(style_clip.ftext().strip())
            if clip.start > idx:
                clip.position = 1
            elif clip.start <= idx and clip.end > idx:
                clip.position = 0
                before_clip = clip
                while before_clip.type == ClipType.JoinPrev:
                    before_clip = self.clips[before_clip.idx-1]
                    before_clip.joined = True
                try:
                    after_clip = self.clips[clip.idx+1]
                    while after_clip.type == ClipType.JoinPrev:
                        after_clip.joined = True
                        after_clip = self.clips[after_clip.idx+1]
                except IndexError:
                    pass
            else:
                clip.position = -1
        return self
    
    def currentSyllable(self):
        for clip in self.clips:
            if clip.position == 0:
                return clip
    
    def currentWord(self):
        for clip in self.clips:
            if clip.position == 0:
                clips = [clip]
                before_clip = clip
                # walk back
                while before_clip.type == ClipType.JoinPrev:
                    before_clip = self.clips[before_clip.idx-1]
                    clips.insert(0, before_clip)
                # walk forward
                try:
                    after_clip = self.clips[clip.idx+1]
                    while after_clip.type == ClipType.JoinPrev:
                        clips.append(after_clip)
                        after_clip = self.clips[after_clip.idx+1]
                except IndexError:
                    pass
                return clips
    
    def currentLine(self):
        for line in self.lines():
            for clip in line:
                if clip.position == 0:
                    return line

    def sibling(self, clip, direction, wrap=False):
        try:
            if clip.idx + direction < 0 and not wrap:
                return None
            return self.clips[clip.idx + direction]
        except IndexError:
            return None
    
    def text(self):
        txt = ""
        for c in self.clips:
            if c.type == ClipType.ClearScreen:
                pass
            elif c.type == ClipType.Isolated:
                txt += "( )"
            elif c.type == ClipType.JoinPrev:
                txt += "|"
            elif c.type == ClipType.NewLine:
                txt += "/(\\n)/"
            txt += c.text
        return txt
        #return "|".join([(c.text + "/") if c.eol else c.text for c in self.clips])
    
    def __repr__(self):
        return "<ClipGroup {:04d}-{:04d} \"{:s}\">".format(self.start, self.end, self.text())
    
    def __hash__(self):
        return self.text()


def grouped_clips(tcs):
    groups = []
    group = []
    last_clip = None
    for idx, tc in enumerate(tcs):
        if tc.type == ClipType.ClearScreen:
            if len(group) > 0:
                groups.append(ClipGroup(len(groups), group))
            group = []
        elif tc.type == ClipType.JoinPrev:
            if last_clip:
                last_clip.addJoin(tc, +1)
                tc.addJoin(last_clip, -1)
        group.append(tc)
        last_clip = tc
    if len(group) > 0:
        groups.append(ClipGroup(len(groups), group))
    return groups

def s_to_f(s, fps):
    return math.floor(s*fps)

def midi_to_frames(f, fps, bpm=120, length=None, loop_length=None):
    mid = mido.MidiFile(f)
    time = 0
    cumulative_time = 0
    events = []
    open_notes = {}
    for i, track in enumerate(mid.tracks):
        for msg in track:
            delta_s = mido.tick2second(msg.time, mid.ticks_per_beat, mido.bpm2tempo(bpm))
            cumulative_time += delta_s
            if msg.type == "note_on":
                open_notes[msg.note] = cumulative_time
            elif msg.type == "note_off":
                o = open_notes.get(msg.note)
                open_notes[msg.note] = None
                events.append((msg.note, s_to_f(o, fps), s_to_f(cumulative_time, fps)))
    
    if length and loop_length:
        looped = []
        loop_count = math.floor(loop_length / length)
        bps = bpm / 60
        offset = bps * fps
        for l in range(1, round(loop_count)):
            for (note, start, end) in events:
                looped.append((note, int(round(start+offset*l*length)), int(round(end+offset*l*length))))
        events.extend(looped)
    return events