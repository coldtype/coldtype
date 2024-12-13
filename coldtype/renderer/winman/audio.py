from coldtype.renderer.winman.passthrough import WinmanPassthrough
from coldtype.renderable.animation import animation

import wave
try:
    import pyaudio
    import soundfile
    import numpy as np
    from soundfile import SoundFile
except ImportError:
    pyaudio = None
    soundfile = None
    np = None


class WinmanAudio(WinmanPassthrough):
    @staticmethod
    def Possible():
        return bool(pyaudio and soundfile and np)

    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.pa_src:SoundFile = None
        self.pa_stream = None
        self.pa_rate = 0
        self.a = None
    
    def recycle(self):
        if self.pa_stream:
            self.pa_stream.stop_stream()
            self.pa_stream.close()
        if self.pa_src:
            self.pa_src.close()
        
        self.pa_stream = None
        self.pa_src = None
    
    def reload_with_animation(self, a:animation):
        self.recycle()
        self.a = a
        if a.audio:
            try:
                self.pa_src = soundfile.SoundFile(a.audio, "r+")
            except:
                print(">>> Could not load audio file (corrupted?)")
                self.pa_src = None
    
    def play_frame(self, frame):
        #if not self.args.preview_audio:
        #    return
        
        if pyaudio and self.pa_src:
            hz = self.pa_src.samplerate
            width = self.pa_src.channels

            if not self.pa_stream or hz != self.pa_rate:
                self.pa_rate = hz
                self.pa_stream = self.pa.open(
                    format=pyaudio.paFloat32,
                    channels=width,
                    rate=hz,
                    output=True)

            audio_frame = frame
            chunk = int(hz / self.a.timeline.fps)

            try:
                self.pa_src.seek(chunk*audio_frame)
                data = self.pa_src.read(chunk)
                data = data.astype(np.float32).tostring()
                self.pa_stream.write(data)
            except wave.Error:
                print(">>> Could not read audio at frame", audio_frame)

    def play_once(self, animation):
        if not animation.audio:
            return

        wf = wave.open(str(animation.audio), 'rb')
        stream = self.p.open(
            format=self.p.get_format_from_width(
                wf.getsampwidth()),
            channels = wf.getnchannels(),
            rate = wf.getframerate(),
            output = True)

        chunk = 1024
        data = wf.readframes(chunk)
        # Play the sound by writing the audio data to the stream
        while data != '':
            stream.write(data)
            data = wf.readframes(chunk)
        
        stream.close()
        print("PLAY!", animation.audio)
        pass

    def terminate(self):
        self.recycle()
        self.pa.terminate()