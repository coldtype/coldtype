import re
from enum import Enum
from coldtype.timing.easing import ease
from coldtype.timing.timeable import Timeable


class ClipType(Enum):
    ClearScreen = "ClearScreen"
    NewLine = "NewLine"
    GrafBreak = "GrafBreak"
    Blank = "Blank"
    Isolated = "Isolated"
    JoinPrev = "JoinPrev"
    Meta = "Meta"
    EndCap = "EndCap"


class ClipFlags(Enum):
    FadeIn = "FadeIn"
    FadeOut = "FadeOut"


class Clip(Timeable):
    def __init__(self, text, start, end, idx=None, track=0):
        self.idx = idx
        self.input_text = str(text)
        self.text = text
        self.start = start
        self.end = end

        self.styles = []
        self.style_clips = []
        self.position = 1
        self.joined = False
        self.joinPrev = None
        self.joinNext = None
        self.track = track
        self.group = None
        self.blank = False
        self.blank_height = 20
        self.inline_styles = []
        self.inline_data = {}
        self.flags = {}
        self.type = ClipType.Isolated
        self.symbol = None
        self.symbol_position = 0

        if self.text.startswith("^$"):
            symbol, rest = self.text.split("|")
            self.symbol = symbol[2:]
            self.symbol_position = -2
            self.text = rest
        elif self.text.startswith("^"):
            symbol, rest = self.text.split("|")
            self.symbol = symbol[1:]
            self.symbol_position = -1
            self.text = rest
        elif self.text.startswith("$"):
            symbol, rest = self.text.split("|")
            self.symbol = symbol[1:]
            self.symbol_position = +1
            self.text = rest

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
        elif self.text.startswith("µ:"):
            self.type = ClipType.Meta
            self.text = self.text[2:]
        elif self.text == "•":
            self.type = ClipType.EndCap
            self.text = ""
        
        parts = self.text.split(":")
        inline_style_marker = parts.index("ß") if "ß" in parts else -1
        inline_data_marker = parts.index("∂") if "∂" in parts else -1

        if inline_style_marker > -1:
            self.inline_styles = parts[inline_style_marker+1].split(",")
        if inline_data_marker > -1:
            qs = [q.split("=") for q in parts[inline_data_marker+1].split("&")]
            for k, v in qs:
                self.inline_data[k] = eval(v)
        
        self.text = parts[0]
        self.text = self.text.replace("{colon}", ":")

        #if "ß" in self.text:
        #    parts = self.text.split(":")
        #    self.text = parts[0]
        #    self.inline_styles = parts[-1].split(",")
        
        #self.text = self.text.replace("§", "\u200b")
        if self.text.startswith("§"):
            #self.text = "\u200b"
            self.text = self.text[1:]
            #self.type = ClipType.JoinPrev
            self.type = ClipType.NewLine
            self.blank = True
            try:
                self.blank_height = float(self.text.strip())
            except:
                pass
    
        if self.text.startswith("∫"):
            self.text = ""
            self.blank = True
        
        if not self.text:
            self.blank = True
            self.text = ""
        
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
        
        self.original_text = str(self.text)
    
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
    
    def style_matching(self, txt):
        try:
            return next(c for c in self.style_clips if txt in c.text)
        except StopIteration:
            return None

    def ftext(self):
        txt = self.text
        if self.type == ClipType.Isolated:
            return " " + txt
        else:
            return txt
    
    def fade(self, default_fade=5):
        if ClipFlags.FadeIn in self.flags:
            return self.flags[ClipFlags.FadeIn]
        else:
            return default_fade
    
    def fadeIn(self, fi, easefn="seio", fade_length=None, start=0):
        if ClipFlags.FadeIn in self.flags or fade_length:
            if fade_length:
                fade = fade_length
            else:
                fade = self.flags[ClipFlags.FadeIn]
            
            if start == 0:
                start_frame = self.start
            elif start == -1:
                start_frame = self.start - fade
            
            if fi < start_frame:
                return -1
            elif fi > start_frame + fade:
                return 1
            else:
                fv = (fi - start_frame) / fade
                a, _ = ease(easefn, fv)
                return a
        return -1
    
    def __repr__(self):
        return "<Clip:({:s}/{:04d}/{:04d}\"{:s}\")>".format([" -1", "NOW", " +1"][self.position+1], self.start, self.end, self.text)