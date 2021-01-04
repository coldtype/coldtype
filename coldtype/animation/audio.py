import math
import os.path
import numpy as np
try:
    import soundfile as sf
except:
    sf = None

from coldtype.pens.datpen import DATPen

class Wavfile():
    def __init__(self, path, fps=30):
        self.sf, self.sf_fs = sf.read(str(path))
        self.fps = fps
        self.hz = self.sf_fs
        self.samples_per_frame = self.hz / fps
        self.path = path
        self.peaks = self.sf
        self.framelength = int(round(len(self.peaks) / self.samples_per_frame))

        max_frame_amp = 0
        for i in range(0, self.framelength):
            amp = self.amp(i)
            if amp > max_frame_amp:
                max_frame_amp = amp
        self.max_frame_amp = max_frame_amp

    def calc_peaks(self):
        snd = self.sf / (2.**15)
        s1 = snd[:, 0]
        return s1

    def samples_for_frame(self, i):
        start_sample = math.floor(i * self.samples_per_frame)
        end_sample = math.floor(start_sample + self.samples_per_frame)
        return self.peaks[start_sample:end_sample]

    def amp(self, i):
        return np.average(np.fabs(self.samples_for_frame(i)))
    
    def frame_waveform(self, fi, r, inc=1, pen=None):
        wave = pen or DATPen()
        samples = self.samples_for_frame(fi)[::inc]
        ww = r.w/len(samples)
        wh = r.h
        for idx, w in enumerate(samples):
            if idx == 0:
                wave.moveTo((r.x, w[0]*wh))
            else:
                wave.lineTo((idx*ww, w[0]*wh))
        wave.endPath()
        wave.f(None).s(1).sw(2)
        return wave
