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


def midi_to_note_name(midi_number):
    if not (0 <= midi_number <= 127):
        return "Invalid MIDI note number"

    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    note_index = midi_number % 12
    octave = (midi_number // 12) - 1

    note_name = note_names[note_index]
    return f"{note_name}{octave}"


strings = {
    "D5": 4, "F5": 4, "G5": 4,
    "C5": 3, #"D5": 3,
    "G4": 2, "G#4": 2, "A4": 2, "B4": 2,
    "C4": 1, "D4": 1, "E4": 1, "F4": 1,
}


class AbletonMIDINote(Timeable):
    def __repr__(self):
        return f"<AbletonMIDINote {self.name},{self.start},{self.end}/>"


class AbletonMIDIClip(Timeline):
    def __init__(self, b2ff, clip):
        clip_name = clip.find("Name").attrib["Value"]
        clip_start = float(clip.find("CurrentStart").attrib["Value"])
        clip_end = float(clip.find("CurrentEnd").attrib["Value"])

        timeables_by_id = dict()

        super().__init__(name=clip_name, findWords=False, start=b2ff(clip_start), end=b2ff(clip_end))

        for idx, kt in enumerate(clip.findall("Notes/KeyTracks/KeyTrack")):
            midi_key = kt.find("MidiKey").attrib["Value"]
            for jdx, note in enumerate(kt.find("Notes")):
                na = dict(note.attrib).copy()
                #if na["IsEnabled"]:
                nt = clip_start + float(na["Time"])
                nd = float(na["Duration"])
                note_id = na["NoteId"]
                vel = float(na["Velocity"])
                note_name = midi_to_note_name(int(midi_key))
                string = strings.get(note_name, None)
                end = b2ff(nt+nd)
                if note_name == "G5" and vel < 100:
                    end = b2ff(nt+nd+0.25)
                    string = 5
                note = AbletonMIDINote(b2ff(nt), end, jdx, midi_key, id=note_id, data=dict(velocity=vel, note=note_name, string=string))
                self.timeables.append(note)
                timeables_by_id[note_id] = note
        
        for idx, el in enumerate(clip.findall("Notes/PerNoteEventStore/EventLists/PerNoteEventList")):
            note_id = el.attrib["NoteId"]
            note = timeables_by_id[note_id]
            cc = el.attrib["CC"]
            if cc == "-2":
                negatives = False
                for jdx, event in enumerate(el.find("Events")):
                    offset = float(event.attrib["TimeOffset"])
                    value = float(event.attrib["Value"])
                    if value < 0.01:
                        negatives = True
                    note.timeables.append(Timeable(b2ff(offset), b2ff(offset)+1, jdx, data=dict(value=value)))
                if negatives and note.data.get("note") == "D5":
                    note.data["string"] = note.data.get("string") - 1


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

        master_track = lx.find("LiveSet/MainTrack")
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
    
    ar = AbletonReader("~/Waves/projs/2024.02.05.1 Project/__silentnighttab2.als")

    #print(ar.timeables[0].timeables[0].timeables)
    
    # el = ar.timeables[1].automation[0]
    # points = {}
    # for fe in el.findall("Events/FloatEvent"):
    #     b = float(fe.attrib["Time"])
    #     frame = ar.b2ff(b)
    #     percent = float(fe.attrib["Value"])
    #     fr = b2f((60/120)*30, b)
    #     if fr < 0:
    #         fr = 0
    #     points[fr] = percent
    
    # interp = []
    # for fr in range(0, ar.duration):
    #     p = points.get(fr, None)
    #     if p:
    #         interp.append(p)
    #     else:
    #         pass

    #reparsed = mini.parseString(ET.tostring(el, 'utf-8'))
    #print(reparsed.toprettyxml(indent="  "))
    
    from coldtype.raster import phototype

    colors = {
        5: hsl(0.65, 0.6, 0.6),
        4: hsl(0.3, 0.6, 0.6),
        3: hsl(0.9, 0.7, 0.6),
        2: hsl(0.6, 0.7, 0.6),
        1: hsl(0, 0.7, 0.6),
    }

    @animation(Rect(1920*2-400, 1080), tl=ar, bg=0)
    def ableton(f):
        xs = 2
        ys = 15
        
        notes = P()
        hits = P()
        
        for t in ar.timeables[0].timeables[0].timeables:
            n:AbletonMIDINote = t
            note = n.data.get("note")
            string = n.data.get("string")
            color = colors.get(string, 1)
            x = n.start*xs
            y = int(n.name)*ys
            bend_points = [Point(x, y+ys/2)]
            last_y = y+ys/2
            for b in n.timeables:
                if b.start < 0.01:
                    continue
                p = Point(x+b.start*xs, y+ys/2+(b.data["value"]/170)*ys)
                last_y = p.y
                bend_points.append(p)
            bend_points.append(Point(x+n.duration*xs, last_y))
            #out.append(P().rect(Rect(x, y, n.duration*xs, ys)).fssw(-1, hsl(0.65), 1))
            notes.append(P().line(bend_points).f(color).outline(3, cap="butt").ro())
            hits.append(P().line([Point(x, y).o(0, -2), Point(x, y).o(0, ys+2)]).fssw(-1, 1, 2))
        return P(notes, hits).align(f.a.r.inset(60), "CX").scale(1, 2)#.ch(phototype(f.a.r, 0.5, 120, 40))

        #e1 = ar.timeables[1].timeables[0].ki(60, f.i).adsr([7, 0, 0, 30])
        #e2 = ar.timeables[1].timeables[0].ki(65, f.i).adsr([7, 0, 0, 30])
        #return (P(
        #    P().oval(f.a.r.inset(100)).fssw(-1, hsl(0.017, 0.8, 0.7), 3).scale(e1+0.25),
        #    P().oval(f.a.r.inset(100)).fssw(-1, hsl(0.7, 0.8, 0.7), 3).scale(e2+0.2),
        #))