from coldtype.timing import Timeline, Timeable
from coldtype.helpers import sibling

from pathlib import Path
from functools import partial
from lxml import etree
import gzip, math

import xml.dom.minidom as mini
import xml.etree.ElementTree as ET

# DeviceChain/MainSequencer/ClipTimeable/ArrangerAutomation/Events/MidiClip/Notes/KeyTracks

def save_test_xml(x):
    sibling(__file__, "test_read_ableton.xml").write_text(etree.tostring(x, pretty_print=True).decode())


def b2f(fpb, t):
    return math.floor(t * fpb)


def b2ms(bpm, b):
    return b * (60000 / bpm)


class AbletonMIDINote(Timeable):
    def __repr__(self):
        return f"<AbletonMIDINote {self.name},{self.start},{self.end}/>"


class AbletonMIDIClip(Timeline):
    def __init__(self, b2ff, clip):
        clip_name = clip.find("Name").attrib["Value"]
        clip_start = float(clip.find("CurrentStart").attrib["Value"])
        clip_end = float(clip.find("CurrentEnd").attrib["Value"])

        super().__init__(name=clip_name, findWords=False, start=b2ff(clip_start), end=b2ff(clip_end))

        for idx, kt in enumerate(clip.findall("Notes/KeyTracks/KeyTrack")):
            midi_key = kt.find("MidiKey").attrib["Value"]
            for jdx, note in enumerate(kt.find("Notes")):
                na = dict(note.attrib).copy()
                if na["IsEnabled"]:
                    nt = clip_start + float(na["Time"])
                    nd = float(na["Duration"])
                    self.timeables.append(AbletonMIDINote(b2ff(nt), b2ff(nt+nd), jdx, midi_key))


class AbletonMIDITrack(Timeline):
    def __init__(self, b2ff, track):
        self.b2ff = b2ff
        
        track_name = track.find("Name/EffectiveName").attrib["Value"]
        timeables = [AbletonMIDIClip(b2ff, clip) for clip in track.findall("DeviceChain/MainSequencer/ClipTimeable/ArrangerAutomation/Events/MidiClip")]
        
        super().__init__(timeables=timeables, findWords=False, name=track_name)

        automation = []
        for a in track.xpath("AutomationEnvelopes/Envelopes/AutomationEnvelope/Automation"):
            automation.append(a)

        self.xml = track
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


class AbletonAudioTrack(Timeline):
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

        super().__init__(timeables=clips, findWords=False, name=track_name)
        #super().__init__(clips, name=track_name)


class AbletonReader(Timeline):
    def __init__(self, path, duration=-1, fps=30, rounded=True, note_names={}):
        note_names_reversed = {v:k for (k,v) in note_names.items()}
        als_path = path if isinstance(path, Path) else Path(path).expanduser()

        lx = None
        if als_path.suffix == ".xml":
            with open(str(als_path), "rb") as f:
                lx = etree.fromstring(f.read())
        else:
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
                #tracks.append(AbletonAudioTrack(b2ff, t))
                pass
            elif t.tag == "ReturnTrack":
                self.returns.append(t)
        
        if duration == -1:
            duration = max([t.end for t in tracks])
        
        # huh?
        #for t in tracks:
        #    t.constrain(0, duration)

        super().__init__(duration=duration, fps=fps, timeables=tracks, findWords=False, name="Ableton")
        #super().__init__(duration, fps=fps, tracks=tracks)

if __name__ == "<run_path>":
    from coldtype import *
    
    ar = AbletonReader("~/Waves/projs/2024.02.05.1 Project/2024.07.29.01.als")
    
    el = ar.timeables[1].automation[0]
    points = {}
    for fe in el.findall("Events/FloatEvent"):
        b = float(fe.attrib["Time"])
        frame = ar.b2ff(b)
        percent = float(fe.attrib["Value"])
        fr = b2f((60/120)*30, b)
        if fr < 0:
            fr = 0
        points[fr] = percent
    
    interp = []
    for fr in range(0, ar.duration):
        p = points.get(fr, None)
        if p:
            interp.append(p)
        else:
            pass

    #reparsed = mini.parseString(ET.tostring(el, 'utf-8'))
    #print(reparsed.toprettyxml(indent="  "))

    @animation(Rect(540, 540), tl=ar, bg=0)
    def ableton(f):
        e1 = ar.timeables[1].timeables[0].ki(60, f.i).adsr([7, 0, 0, 30])
        e2 = ar.timeables[1].timeables[0].ki(65, f.i).adsr([7, 0, 0, 30])
        return (P(
            P().oval(f.a.r.inset(100)).fssw(-1, hsl(0.017, 0.8, 0.7), 3).scale(e1+0.25),
            P().oval(f.a.r.inset(100)).fssw(-1, hsl(0.7, 0.8, 0.7), 3).scale(e2+0.2),
        ))