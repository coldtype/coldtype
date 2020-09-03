from coldtype.animation import Timeline, Timeable, TimeableSet
from coldtype.helpers import sibling

from pathlib import Path
from functools import partial
from lxml import etree
import gzip, math

# DeviceChain/MainSequencer/ClipTimeable/ArrangerAutomation/Events/MidiClip/Notes/KeyTracks

def save_xml(x):
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
            for note in kt.find("Notes"):
                na = dict(note.attrib).copy()
                if na["IsEnabled"]:
                    nt = clip_start + float(na["Time"])
                    nd = float(na["Duration"])
                    self.timeables.append(AbletonMIDINote(b2ff(nt), b2ff(nt+nd), idx, midi_key))


class AbletonMIDITrack(TimeableSet):
    def __init__(self, b2ff, track):
        track_name = track.find("Name/EffectiveName").attrib["Value"]
        super().__init__([AbletonMIDIClip(b2ff, clip) for clip in track.findall("DeviceChain/MainSequencer/ClipTimeable/ArrangerAutomation/Events/MidiClip")], track_name)
        
        #automation = []
        #for a in track.xpath("AutomationEnvelopes/Envelopes/AutomationEnvelope/Automation"):
        #    automation.append(a)

    def notes(self):
        return [int(t.name) for t in self.flat_timeables()]
    
    def range(self):
        ns = self.notes()
        return min(ns), max(ns)


class AbletonReader(Timeline):
    def __init__(self, path, duration=-1, fps=30, rounded=True, note_names={}):
        note_names_reversed = {v:k for (k,v) in note_names.items()}
        als_path = path if isinstance(path, Path) else Path(path).expanduser()

        lx = None
        with gzip.open(str(als_path), "rb") as f:
            lx = etree.fromstring(f.read())
            save_xml(lx)

        master_track = lx.find("LiveSet/MasterTrack")
        bpm = float(master_track.find("AutomationEnvelopes/Envelopes/AutomationEnvelope[@Id='1']/Automation/Events/FloatEvent").attrib["Value"])

        fpb = (60/bpm)*fps
        b2ff = partial(b2f, fpb)

        tracks = [AbletonMIDITrack(b2ff, track) for track in lx.findall("LiveSet/Tracks/MidiTrack")]
        
        if duration == -1:
            duration = max([t.end for t in tracks])

        super().__init__(duration, fps=fps, tracks=tracks)

if __name__ == "<run_path>":
    from coldtype import *

    ar = AbletonReader("~/Audio/loopprojs/test_read Project/test_read2.als")

    @renderable()
    def ableton(r):
        return DATPen().oval(r).f(hsl(0.3))