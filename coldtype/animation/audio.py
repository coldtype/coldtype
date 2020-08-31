import math
import os.path
import numpy as np
import soundfile as sf


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