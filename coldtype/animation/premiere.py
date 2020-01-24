import re, json, math
from pathlib import Path
from enum import Enum
import copy

from coldtype.animation.time import AnimationTime
from coldtype.animation.timeline import Timeline
from coldtype.animation.easing import ease
from coldtype.text import StyledString, Lockup, Graf, GrafStyle, Furniture, DATPen, DATPenSet


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
    GrafBreak = "GrafBreak"
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
            elif self.text.startswith("¶"):
                self.text = self.text[1:]
                self.type = ClipType.GrafBreak
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
    
    def fadeIn(self, fi, easefn="seio", fade_length=None):
        if ClipFlags.FadeIn in self.flags or fade_length:
            if fade_length:
                fade = fade_length
            else:
                fade = self.flags[ClipFlags.FadeIn]
            fv = (fi-self.start)/fade
            if fv >= 1:
                return 1
            else:
                a, _ = ease(easefn, fv)
                return a
        return -1

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
        t = (i-self.start) / self.duration
        if loops == 0:
            return AnimationTime(t, t, 0, easefn)
        else:
            loop_t, loop_index = self._loop(t, times=loops, cyclic=cyclic)
            return AnimationTime(t, loop_t, loop_index, easefn)
    
    def __repr__(self):
        return "<Clip:({:s}/{:04d}/{:04d}\"{:s}\")>".format([" -1", "NOW", " +1"][self.position+1], self.start, self.end, self.text)


group_pens_cache = {}

class ClipGroup():
    def __init__(self, timeline, index, clips):
        self.index = index
        self.clips = clips
        self.start = clips[0].start
        self.end = clips[-1].end
        self.duration = self.end - self.start
        self.track = clips[0].track
        self.timeline = timeline

        for idx, clip in enumerate(clips):
            clip.idx = idx
            clip.group = self
    
    def prg(self, i):
        return (i-self.start)/self.duration
    
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
            elif clip.type == ClipType.GrafBreak:
                lines.append(line)
                cclip = copy.deepcopy(clip)
                cclip.text = "¶"
                lines.append([cclip])
                #lines.append([Furniture(100, 100)])
                line = [clip]
                # add a graf mark
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
                            elif style_clip.start >= clip.start and style_clip.end <= clip.end:
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
    
    def ClearCache():
        global group_pens_cache
        group_pens_cache = {}
    
    def pens2(self, f, render_clip_fn, rect, graf_style, fit=None):
        group_pens = DATPenSet()
        lines = []
        groupings = []
        for idx, _line in enumerate(self.lines()):
            slugs = []
            texts = []
            for clip in _line:
                try:
                    text, style_name, style = render_clip_fn(f, clip)
                    texts.append([text, clip.idx, style_name, style])
                except Exception as e:
                    print(e)
                    raise Exception("pen2 render_clip must return text, style_name, & style")
            
            grouped_texts = []
            idx = 0
            done = False
            while not done:
                style_name = texts[idx][2]
                grouped_text = [texts[idx]]
                style_same = True
                while style_same:
                    idx += 1
                    try:
                        next_style_name = texts[idx][2]
                        if next_style_name == style_name:
                            style_same = True
                            grouped_text.append(texts[idx])
                        else:
                            style_same = False
                            grouped_texts.append(grouped_text)
                    except IndexError:
                        done = True
                        style_same = False
                        grouped_texts.append(grouped_text)
            
            for gt in grouped_texts:
                full_text = "".join([t[0] for t in gt])
                slugs.append(StyledString(full_text, gt[0][3]))
            groupings.append(grouped_texts)
            lines.append(slugs)
        
        lockups = []
        for line in lines:
            lockup = Lockup(line, preserveLetters=True, nestSlugs=True)
            if fit:
                lockup.fit(fit)
            lockups.append(lockup)
        graf = Graf(lockups, rect, graf_style)
        pens = graf.pens()#.align(rect, x="minx")
        
        re_grouped = DATPenSet()
        for idx, line in enumerate(lines):
            #print(pens, idx, line[0].text)
            line_dps = pens[idx]
            re_grouped_line = DATPenSet()
            for gidx, gt in enumerate(groupings[idx]):
                group_dps = line_dps[gidx]
                tidx = 0
                last_clip_dps = None
                for (text, cidx, style_name, style) in gt:
                    clip:Clip = self.clips[cidx]
                    clip_dps = DATPenSet(group_dps[tidx:tidx+len(text)])
                    clip_dps.tag = style_name
                    clip_dps.data["clip"] = self.clips[cidx]
                    if clip.type == ClipType.JoinPrev and last_clip_dps:
                        grouped_clip_dps = DATPenSet()
                        grouped_clip_dps.append(last_clip_dps)
                        grouped_clip_dps.append(clip_dps)
                        re_grouped_line[-1] = grouped_clip_dps
                        last_clip_dps = grouped_clip_dps
                    else:
                        re_grouped_line.append(clip_dps)
                        last_clip_dps = clip_dps
                    tidx += len(text)
            re_grouped_line.addFrame(line_dps.getFrame())
            re_grouped.append(re_grouped_line)
        
        pens = re_grouped
        for pens in pens.pens:
            for pen in pens.pens:
                pen.removeOverlap()
            group_pens.append(pens)
        
        for clip, pen in self.iterate_clip_pens(group_pens):
           if clip.position == 1 or clip.text == "¶":
               pen.f(0)
        
        return group_pens
    
    def pens(self, render_clip_fn, rect, graf_style, fit=None, cache=True):
        global group_pens_cache
        
        if cache:
            if group_pens_cache.get(self.track, dict()).get(self.index):
                return group_pens_cache[self.track][self.index]
        
        group_pens = DATPenSet()
        lines = []
        for idx, _line in enumerate(self.lines()):
            slugs = []
            for clip in _line:
                result = render_clip_fn(clip)
                if result:
                    slugs.append(result)
                else:
                    raise Exception("render_clip must return something")
            lines.append(slugs)
        lockups = []
        for line in lines:
            lockup = Lockup(line, preserveLetters=True, nestSlugs=True)
            if fit:
                lockup.fit(fit)
            lockups.append(lockup)
        graf = Graf(lockups, rect, graf_style)
        pens = graf.pens().align(rect, x=graf_style.x)
        for pens in pens.pens:
            for pen in pens.pens:
                pen.removeOverlap()
            group_pens.append(pens)
        track_cache = group_pens_cache.get(self.track, dict())
        track_cache[self.index] = group_pens
        group_pens_cache[self.track] = track_cache
        return group_pens
    
    def iterate_clip_pens(self, pens):
        for pen in pens:
            if hasattr(pen, "data"):
                if pen.data.get("clip"):
                    yield pen.data.get("clip"), pen
                else:
                    yield from self.iterate_clip_pens(pen)
    
    def iterate_pens(self, pens, copy=True):
        for idx, line in enumerate(self.lines()):
            _pens = pens[idx]
            for cidx, clip in enumerate(line):
                if copy:
                    p = _pens.pens[cidx].copy()
                else:
                    p = _pens.pens[cidx]
                yield idx, clip, p
    
    def __repr__(self):
        return "<ClipGroup {:04d}-{:04d} \"{:s}\">".format(self.start, self.end, self.text())
    
    def __hash__(self):
        return self.text()


class ClipTrack():
    def __init__(self, clips):
        self.clips = clips
        self.clip_groups = self.groupedClips(clips)
    
    def groupedClips(self, clips):
        groups = []
        group = []
        last_clip = None
        for idx, clip in enumerate(clips):
            if clip.type == ClipType.ClearScreen:
                if len(group) > 0:
                    groups.append(ClipGroup(self, len(groups), group))
                group = []
            elif clip.type == ClipType.JoinPrev:
                if last_clip:
                    last_clip.addJoin(clip, +1)
                    clip.addJoin(last_clip, -1)
            group.append(clip)
            last_clip = clip
        if len(group) > 0:
            groups.append(ClipGroup(self, len(groups), group))
        return groups
    
    def current(self, fi):
        for idx, clip in enumerate(self.clips):
            clip:Clip
            if clip.start <= fi and fi < clip.end:
                return clip


class PremiereTimeline(Timeline):
    __name__ = "Premiere"

    def __init__(self, path, storyboard=None):
        json_path = path if isinstance(path, Path) else Path(path).expanduser()
        jsondata = json.loads(json_path.read_text())
        meta = jsondata.get("metadata")
        
        fps = 1 / meta.get("frameRate")
        duration = int(round(int(meta.get("duration"))/int(meta.get("timebase"))))

        tof = lambda s: int(round(float(s)*fps))
        
        cti = tof(meta.get("cti"))
        self.cti = cti

        _storyboard = []
        _storyboard.append(self.cti)
        for m in jsondata.get("storyboard"):
            f = tof(m.get("start"))
            if f not in _storyboard:
                _storyboard.append(f)
        
        if storyboard:
            _storyboard = storyboard
        
        workareas = []
        workareas.append(range(max(0, tof(meta.get("inPoint"))), tof(meta.get("outPoint"))+1))

        tracks = []
        for tidx, track in enumerate(jsondata.get("tracks")):
            markers = [Marker(fps, m) for m in track.get("markers")]
            tracks.append(ClipTrack([Clip(c, fps=fps, markers=markers, track=tidx) for c in track.get("clips")]))
        
        super().__init__(duration, fps, _storyboard, workareas, tracks)
    
    def trackClipGroupForFrame(self, track_idx, frame_idx, styles=None, check_end=True):
        for gidx, group in enumerate(self[track_idx].clip_groups):
            if not check_end:
                end_good = False
                try:
                    next_group = self[track_idx].clip_groups[gidx+1]
                    end_good = next_group.start > frame_idx
                except IndexError:
                    end_good = True
            if group.start <= frame_idx and ((check_end and group.end > frame_idx) or (not check_end and end_good)):
                style_groups = None
                if styles:
                    style_groups = []
                    for style in styles:
                        style_groups.append(self.trackClipGroupForFrame(style, frame_idx, check_end=False))
                return group.position(frame_idx, style_groups)
    
    def currentWorkarea(self):
        cg = self.trackClipGroupForFrame(0, self.cti)
        if cg:
            return [cg.start, cg.end]