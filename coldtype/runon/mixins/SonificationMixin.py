import struct, wave
from coldtype.geometry import Rect

class SonificationMixin():
    # contours?
    def _prep_for_wave(self, flatten=1, centered=False):
        prepped = self.copy()
        if centered:
            prepped.center(tx=1, ty=1)
        
        if flatten > 0:
            prepped.flatten(flatten)
        
        return prepped

    def toAudio(self, flatten=1, centered=False, loops=3, filename=None):
        import numpy as np
        from pedalboard.io import AudioFile

        prepped = self._prep_for_wave(flatten=flatten, centered=centered)

        left, right = [], []
        for (_, pts) in prepped._val.value:
            if len(pts) > 0:
                left.append(pts[0][0] / 1000)
                right.append(pts[0][1] / 1000)

        audio = np.tile(np.array([left, right]), loops)

        if filename:
            with AudioFile(filename, "w", samplerate=48000, num_channels=2) as f:
                f.write(audio)
        
        return audio, len(left)
    
    def fromAudio(self, audio, start=500, end=9500, step=1, mult=1360, scale=2):
        for idx in range(start, end, step):
            try:
                x = audio[0][idx]
                y = audio[1][idx]
                self.oval(Rect.FromCenter((x*mult, y*mult), scale))
            except IndexError:
                pass
        return self

    # def wavefile(self, flatten=1, centered=False) -> str:
    #     #from IPython.display import Audio, display

    #     prepped = self._prep_for_wave(flatten=flatten, centered=centered)

    #     left, right = [], []
    #     for (_, pts) in prepped._val.value:
    #         if len(pts) > 0:
    #             left.append(pts[0][0])
    #             right.append(pts[0][1])

    #     samplesPerFrame = 200
    #     sampleRate = 48000.0 # hertz

    #     filename = "test_1.wav"

    #     obj = wave.open(filename, 'w')
    #     obj.setnchannels(2)
    #     obj.setsampwidth(2)
    #     obj.setframerate(sampleRate)

    #     for x in range(0, samplesPerFrame):
    #         for idx, l in enumerate(left):
    #             data = struct.pack('<h', int(l)*24)
    #             obj.writeframesraw(data)
    #             data = struct.pack('<h', int(right[idx])*24)
    #             obj.writeframesraw(data)

    #     # silence
    #     for _ in range(0, 5000):
    #         obj.writeframesraw(struct.pack("<h", 0))
    #         obj.writeframesraw(struct.pack("<h", 0))

    #     obj.close()

    #     return filename