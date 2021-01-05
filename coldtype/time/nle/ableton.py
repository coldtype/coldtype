from coldtype.time import Timeline, Timeable, TimeableSet
from coldtype.helpers import sibling

from pathlib import Path
from functools import partial
from lxml import etree
import gzip, math

# DeviceChain/MainSequencer/ClipTimeable/ArrangerAutomation/Events/MidiClip/Notes/KeyTracks

def save_test_xml(x):
    sibling(__file__, "test_read_ableton.xml").write_text(etree.tostring(x, pretty_print=True).decode())


def b2f(fpb, t):
    return math.floor(t * fpb)


class AbletonMIDINote(Timeable):
    def __repr__(self):
        return f"<AbletonMIDINote {self.name},{self.start},{self.end}/>"


class AbletonMIDIClip(TimeableSet):
    def __init__(self, b2ff, clip):
        clip_name = clip.find("Name").attrib["Value"]
        clip_start = float(clip.find("CurrentStart").attrib["Value"])
        clip_end = float(clip.find("CurrentEnd").attrib["Value"])

        super().__init__([], clip_name, start=b2ff(clip_start), end=b2ff(clip_end))

        for idx, kt in enumerate(clip.findall("Notes/KeyTracks/KeyTrack")):
            midi_key = kt.find("MidiKey").attrib["Value"]
            for jdx, note in enumerate(kt.find("Notes")):
                na = dict(note.attrib).copy()
                if na["IsEnabled"]:
                    nt = clip_start + float(na["Time"])
                    nd = float(na["Duration"])
                    self.timeables.append(AbletonMIDINote(b2ff(nt), b2ff(nt+nd), jdx, midi_key))


class AbletonMIDITrack(TimeableSet):
    def __init__(self, b2ff, track):
        self.b2ff = b2ff
        
        track_name = track.find("Name/EffectiveName").attrib["Value"]
        super().__init__([AbletonMIDIClip(b2ff, clip) for clip in track.findall("DeviceChain/MainSequencer/ClipTimeable/ArrangerAutomation/Events/MidiClip")], track_name)

        automation = []
        for a in track.xpath("AutomationEnvelopes/Envelopes/AutomationEnvelope/Automation"):
            automation.append(a)
        self.automation = automation

    def notes(self):
        return [int(t.name) for t in self.flat_timeables()]
    
    def range(self):
        ns = self.notes()
        return min(ns), max(ns)


class AbletonAudioClip(Timeable):
    def __init__(self, b2ff, clip):
        clip_name = clip.find("Name").attrib["Value"]
        clip_start = float(clip.find("CurrentStart").attrib["Value"])
        clip_end = float(clip.find("CurrentEnd").attrib["Value"])
        super().__init__(b2ff(clip_start), b2ff(clip_end), name=clip_name)


class AbletonAudioTrack(TimeableSet):
    def __init__(self, b2ff, track):
        self.lx = track
        track_name = track.find("Name/EffectiveName").attrib["Value"]
        clips = []
        for clip in track.findall("DeviceChain/MainSequencer/Sample/ArrangerAutomation/Events/AudioClip"):
            clips.append(AbletonAudioClip(b2ff, clip))

        automation = []
        for a in track.xpath("AutomationEnvelopes/Envelopes/AutomationEnvelope/Automation"):
            automation.append(a)
        self.automation = automation

        super().__init__(clips, name=track_name)


class AbletonReader(Timeline):
    def __init__(self, path, duration=-1, fps=30, rounded=True, note_names={}):
        note_names_reversed = {v:k for (k,v) in note_names.items()}
        als_path = path if isinstance(path, Path) else Path(path).expanduser()

        lx = None
        with gzip.open(str(als_path), "rb") as f:
            lx = etree.fromstring(f.read())
        self.lx = lx

        master_track = lx.find("LiveSet/MasterTrack")
        bpm = float(master_track.find("AutomationEnvelopes/Envelopes/AutomationEnvelope[@Id='1']/Automation/Events/FloatEvent").attrib["Value"])

        fpb = (60/bpm)*fps
        b2ff = partial(b2f, fpb)
        self.b2ff = b2ff

        self.returns = []

        tracks = []
        for t in lx.xpath("LiveSet/Tracks/*"):
            if t.tag == "MidiTrack":
                tracks.append(AbletonMIDITrack(b2ff, t))
            elif t.tag == "AudioTrack":
                tracks.append(AbletonAudioTrack(b2ff, t))
                pass
            elif t.tag == "ReturnTrack":
                self.returns.append(t)
        
        if duration == -1:
            duration = max([t.end for t in tracks])
        
        for t in tracks:
            t.constrain(0, duration)

        super().__init__(duration, fps=fps, tracks=tracks)

if __name__ == "<run_path>":
    from coldtype import *

    ar = AbletonReader("~/Audio/loopprojs/test_read Project/test_read2.als")

    @renderable()
    def ableton(r):
        return DATPen().oval(r).f(hsl(0.3))