import sys
from pathlib import Path
from fontTools.misc.bezierTools import splitCubic, splitLine

from coldtype.color import normalize_color
from coldtype.geometry import Rect
from coldtype.text import *

from enum import Enum
from random import random
from defcon import Font
import json
import mido
import math
import re

import easing_functions as ef

VIDEO_OFFSET = 86313 # why is this?

easer_ufo = Font(str(Path(__file__).parent.joinpath("easers.ufo")))

eases = dict(
    cei=ef.CubicEaseIn,
    ceo=ef.CubicEaseOut,
    ceio=ef.CubicEaseInOut,
    qei=ef.QuadEaseIn,
    qeo=ef.QuadEaseOut,
    qeio=ef.QuadEaseInOut,
    eei=ef.ExponentialEaseIn,
    eeo=ef.ExponentialEaseOut,
    eeio=ef.ExponentialEaseInOut,
    sei=ef.SineEaseIn,
    seo=ef.SineEaseOut,
    seio=ef.SineEaseInOut,
    bei=ef.BounceEaseIn,
    beo=ef.BounceEaseOut,
    beio=ef.BounceEaseInOut,
    eleo=ef.ElasticEaseOut,
    elei=ef.ElasticEaseIn,
    elieo=ef.ElasticEaseInOut,
    )


def curve_pos_and_speed(curve, x):
    x1000 = x*1000
    for idx, (action, pts) in enumerate(curve.value):
        if action in ["moveTo", "endPath", "closePath"]:
            continue
        last_action, last_pts = curve.value[idx-1]
        if action == "curveTo":
            o = -1
            a = last_pts[-1]
            b, c, d = pts
            if x1000 == a[0]:
                o = a[1]/1000
                eb = a
                ec = b
            elif x1000 == d[0]:
                o = d[1]/1000
                eb = c
                ec = d
            elif x1000 > a[0] and x1000 < d[0]:
                e, f = splitCubic(a, b, c, d, x1000, isHorizontal=False)
                ez, ea, eb, ec = e
                o = ec[1]/1000
            else:
                continue
            tangent = math.degrees(math.atan2(ec[1] - eb[1], ec[0] - eb[0]) + math.pi*.5)
            #print(o, tangent)
            if tangent >= 90:
                t = (tangent - 90)/90
            else:
                t = tangent/90
            if o != -1:
                return o, t
    raise Exception("No curve value found!")


def ease(style, x):
    if style == "linear":
        return x, 0.5
    e = eases.get(style)
    if e:
        return e().ease(x), 0.5
    else:
        if style in easer_ufo:
            return curve_pos_and_speed(DATPen().glyph(easer_ufo[style]), x)
        else:
            raise Exception("No easing function with that mnemonic")


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
    def __init__(self, clip, fps=None, markers=[], idx=None, track=0):
        self.idx = idx
        self.clip = clip
        self.styles = []
        self.position = 1
        self.joined = False
        self.joinPrev = None
        self.joinNext = None
        self.track = track
        self.group = None

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
    def __init__(self, duration, fps=30, storyboard=[0], workareas=None):
        self.fps = fps
        self.duration = round(duration)
        self.storyboard = storyboard
        if len(self.storyboard) == 0:
            self.storyboard.append(0)
        self.storyboard.sort()
        if workareas:
            self.workareas = workareas
        else:
            self.workareas = [range(0, self.duration+1)]
    
    def __str__(self):
        return "<Timeline:{:04d}f@{:02.2f}fps>".format(self.duration, self.fps)


class AnimationFrame():
    def __init__(self, index, animation, layers):
        self.i = index
        self.a = animation
        self.layers = layers
        self.filepaths = {}

    def __repr__(self):
        return f"<AnimationFrame {self.i}>"


class AnimationTime():
    def __init__(self, t, loop_t, loop, easefn):
        self.t = t
        self.loop_t = loop_t
        self.loop = loop
        self.loop_phase = int(loop%2 != 0)
        self.e, self.s = self.ease(easefn)
    
    def ease(self, easefn):
        easer = easefn
        if not isinstance(easer, str):
            try:
                iter(easefn) # is-iterable
                if len(easefn) > self.loop:
                    easer = easefn[self.loop]
                elif len(easefn) == 2:
                    easer = easefn[self.loop % 2]
                elif len(easefn) == 1:
                    easer = easefn[0]
            except TypeError:
                pass
        return ease(easer, self.loop_t)


class Animation():
    def __init__(self, render, rect=Rect(0, 0, 1920, 1080), timeline=None, bg=0, layers=["main"], watches=[]):
        self.render = render
        self.rect = Rect(rect)
        self.r = self.rect
        self.cache = {}
        self.layers = layers
        self.watches = [str(w.expanduser().resolve()) for w in watches]
        self.sourcefile = None

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
                    duration,
                    fps,
                    storyboard=storyboard,
                    workareas=workareas
                )
                self.clipGroupsByTrack = []
                for tidx, track in enumerate(jsondata.get("tracks")):
                    markers = [Marker(fps, m) for m in track.get("markers")]
                    clips = track.get("clips")
                    gcs = self.groupedClips([Clip(c, fps=fps, markers=markers, track=tidx) for c in clips])
                    self.clipGroupsByTrack.append(gcs)
        elif isinstance(timeline, Timeline):
            self.timeline = timeline
        elif timeline:
            self.timeline = Timeline(timeline, 30)
        else:
            self.timeline = Timeline(1, 30)
        
        self.t = self.timeline # alias
        self.bg = normalize_color(bg)
    
    def groupedClips(self, tcs):
        groups = []
        group = []
        last_clip = None
        for idx, tc in enumerate(tcs):
            if tc.type == ClipType.ClearScreen:
                if len(group) > 0:
                    groups.append(ClipGroup(self, len(groups), group))
                group = []
            elif tc.type == ClipType.JoinPrev:
                if last_clip:
                    last_clip.addJoin(tc, +1)
                    tc.addJoin(last_clip, -1)
            group.append(tc)
            last_clip = tc
        if len(group) > 0:
            groups.append(ClipGroup(self, len(groups), group))
        return groups
        
    def _loop(self, t, times=1, cyclic=True):
        lt = t*times*2
        ltf = math.floor(lt)
        ltc = math.ceil(lt)
        if False:
            if ltc % 2 != 0: # looping back
                lt = 1 - (ltc - lt)
            else: # looping forward
                lt = ltc - lt
        lt = lt - ltf
        if cyclic and ltf%2 == 1:
            lt = 1 - lt
        return lt, ltf
    
    def progress(self, i, loops=0, cyclic=True, easefn="linear"):
        t = i / self.timeline.duration
        if loops == 0:
            return AnimationTime(t, t, 0, easefn)
        else:
            loop_t, loop_index = self._loop(t, times=loops, cyclic=cyclic)
            return AnimationTime(t, loop_t, loop_index, easefn)
    
    #def prg(self, i, c=False):
    #    return self.progress(i, cyclic=c)
    
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

group_pens_cache = {}

class ClipGroup():
    def __init__(self, animation, index, clips):
        self.index = index
        self.clips = clips
        self.start = clips[0].start
        self.end = clips[-1].end
        self.track = clips[0].track
        self.animation = animation

        for idx, clip in enumerate(clips):
            clip.idx = idx
            clip.group = self
    
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
    
    def ClearCache():
        global group_pens_cache
        group_pens_cache = {}
    
    def pens(self, render_clip_fn, rect, graf_style, fit=None, cache=True):
        global group_pens_cache
        
        if cache:
            if group_pens_cache.get(self.track, dict()).get(self.index):
                return group_pens_cache[self.track][self.index]
        
        group_pens = []
        lines = []
        for idx, _line in enumerate(self.lines()):
            slugs = []
            for clip in _line:
                slugs.append(render_clip_fn(clip))
            lines.append(slugs)
        lockups = []
        for line in lines:
            lockup = Lockup(line, preserveLetters=True, nestSlugs=True)
            if fit:
                lockup.fit(fit)
            lockups.append(lockup)
        graf = Graf(lockups, rect, graf_style)
        pens = graf.pens().align(rect)
        for pens in pens.pens:
            for pen in pens.pens:
                pen.removeOverlap()
            group_pens.append(pens)
        track_cache = group_pens_cache.get(self.track, dict())
        track_cache[self.index] = group_pens
        group_pens_cache[self.track] = track_cache
        return group_pens
    
    def iterate_pens(self, pens):
        for idx, line in enumerate(self.lines()):
            _pens = pens[idx]
            for cidx, clip in enumerate(line):
                p = _pens.pens[cidx].copy()
                yield idx, clip, p
    
    def __repr__(self):
        return "<ClipGroup {:04d}-{:04d} \"{:s}\">".format(self.start, self.end, self.text())
    
    def __hash__(self):
        return self.text()


def s_to_f(s, fps):
    return math.floor(s*fps)

class MidiTrack():
    def __init__(self, notes):
        self.notes = notes
    
    def noteForFrame(self, note_numbers, frame, preverb=0, reverb=0):
        if isinstance(note_numbers, int):
            note_numbers = [note_numbers]
        for note in reversed(self.notes):
            valid = False
            if callable(note_numbers):
                if note_numbers(note.note):
                    valid = True
            else:
                if note_numbers == "*" or note.note in note_numbers:
                    valid = True
            
            if valid and frame >= (note.on-preverb) and frame < (note.off+reverb):
                return note
    
    def valueForFrame(self, note_numbers, frame, preverb=0, reverb=0):
        note = self.noteForFrame(note_numbers, frame, preverb=preverb, reverb=reverb)
        if note:
            v = 1 - ((frame - note.on) / (note.duration+reverb))
            if v > 1:
                v = 2 + ((frame - note.on - preverb) / preverb)
                print(v)
            return v
        else:
            return 0
    
    def countToFrame(self, note_number, frame, preverb=0):
        count = 0
        for note in self.notes:
            if note.note == note_number:
                if frame >= (note.on-preverb):
                    count += 1
        return count

class MidiNote():
    def __init__(self, note, on, off, fps, rounded):
        self.fps = fps
        self.note = note
        self.on_seconds = on
        self.off_seconds = off
        self.rounded = rounded
        self.on = self.onf(rounded=rounded)
        self.off = self.offf(rounded=rounded)
        self.duration = self.off - self.on

    def s_to_f(self, value, rounded=True, fps=None):
        _fps = fps or self.fps
        if rounded:
            return math.floor(value*_fps)
        else:
            return value*_fps
    
    def onf(self, rounded=True, fps=None):
        return self.s_to_f(self.on_seconds, rounded=rounded, fps=fps)
    
    def offf(self, rounded=True, fps=None):
        return self.s_to_f(self.off_seconds, rounded=rounded, fps=fps)


def read_midi(f, fps=30, bpm=120, rounded=True):
    mid = mido.MidiFile(str(f))
    events = {}
    open_notes = {}
    for i, track in enumerate(mid.tracks):
        time = 0
        cumulative_time = 0
        events[track.name] = []
        open_notes[track.name] = {}
        for idx, msg in enumerate(track):
            if hasattr(msg, "note"):
                delta_s = mido.tick2second(msg.time, mid.ticks_per_beat, mido.bpm2tempo(bpm))
                cumulative_time += delta_s
                o = open_notes.get(track.name).get(msg.note)
                if o != None:
                    open_notes[track.name][msg.note] = None
                    events[track.name].append(MidiNote(msg.note, o, cumulative_time, fps, rounded))
                if msg.type == "note_on" and msg.velocity > 0:
                    open_notes[track.name][msg.note] = cumulative_time
    if len(mid.tracks) == 1:
        return MidiTrack(events[list(events.keys())[0]])
    else:
        return events

def sibling(root, file):
    return Path(root).parent.joinpath(file)