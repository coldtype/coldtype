from coldtype.animation import Timeline, Timeable, TimeableSet

from pathlib import Path

from lxml import etree
import gzip

# DeviceChain/MainSequencer/ClipTimeable/ArrangerAutomation/Events/MidiClip/Notes/KeyTracks

def save_xml(x):
    sibling(__file__, "test_read_ableton.xml").write_text(etree.tostring(x, pretty_print=True).decode())


class AbletonMIDITrack(TimeableSet):
    def __init__(self, track, bpm):
        notes = {}
        automation = []
        track_name = track.find("Name/EffectiveName").attrib["Value"]

        print(">>>>>>", track_name)

        for a in track.xpath("AutomationEnvelopes/Envelopes/AutomationEnvelope/Automation"):
            automation.append(a)

        midi_clips = track.findall("DeviceChain/MainSequencer/ClipTimeable/ArrangerAutomation/Events/MidiClip")

        for mc in midi_clips:
            clip_name = mc.find("Name").attrib["Value"]
            clip_start = float(mc.find("CurrentStart").attrib["Value"])
            clip_end = float(mc.find("CurrentEnd").attrib["Value"])
            
            print(">>>>>>>>>", clip_name)
            print(clip_start, clip_end)

            for kt in mc.findall("Notes/KeyTracks/KeyTrack"):
                midi_key = kt.find("MidiKey").attrib["Value"]
                notes[midi_key] = []
                for note in kt.find("Notes"):
                    na = dict(note.attrib).copy()
                    if na["IsEnabled"]:
                        nt = clip_start + float(na["Time"])
                        nd = float(na["Duration"])
                        notes[midi_key].append(na)
                        #print(midi_key, na)


class AbletonReader(Timeline):
    def __init__(self, path, duration, fps=30, rounded=True, note_names={}):
        note_names_reversed = {v:k for (k,v) in note_names.items()}
        als_path = path if isinstance(path, Path) else Path(path).expanduser()

        lx = None
        with gzip.open(str(als_path), "rb") as f:
            lx = etree.fromstring(f.read())
            save_xml(lx)

        master_track = lx.find("LiveSet/MasterTrack")
        bpm = master_track.find("AutomationEnvelopes/Envelopes/AutomationEnvelope[@Id='1']/Automation/Events/FloatEvent").attrib["Value"]

        found_duration = 0

        for track in lx.findall("LiveSet/Tracks/MidiTrack"):
            #save_xml(track)
            AbletonMIDITrack(track, bpm)
        

        print(bpm, found_duration)

if __name__ == "<run_path>":
    from coldtype import *

    ar = AbletonReader("~/Audio/loopprojs/test_read Project/test_read2.als", 4)

    @renderable()
    def ableton(r):
        return DATPen().oval(r).f(hsl(0.3))