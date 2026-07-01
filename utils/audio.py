import os
import subprocess
import tempfile
import av
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUND_DIR = os.path.join(BASE_DIR, "assets", "sounds")

SFX_FILES = {
    "eat": "alert_money.ogg",
    "die": "error_2.ogg",
    "win": "start_game.ogg",
    "click": "button_up.ogg",
    "navigate": "navigate.ogg",
    "kill": "whoosh.ogg",
    "boost_on": "boost_start.ogg",
    "boost_off": "boost_stop.ogg",
}


def _decode_ogg(path):
    container = av.open(path)
    stream = container.streams.audio[0]
    codec = stream.codec_context
    rate = codec.sample_rate
    ch = codec.channels
    frames = []
    for frame in container.decode(audio=0):
        arr = frame.to_ndarray()
        frames.append(arr)
    container.close()
    if not frames:
        return None, 0, 0
    data = np.concatenate(frames, axis=1) if frames[0].ndim > 1 else np.concatenate(frames)
    if data.ndim > 1:
        data = data.T.ravel()
    return data, rate, ch


def _pcm_to_wav(pcm, channels, sample_rate):
    pcm_bytes = (pcm * 32767).clip(-32768, 32767).astype(np.int16).tobytes()
    import struct
    data_size = len(pcm_bytes)
    header = struct.pack(
        "<4sI4s4sIHHIIHH",
        b"RIFF", 36 + data_size, b"WAVE",
        b"fmt ", 16, 1, channels,
        sample_rate, sample_rate * channels * 2,
        channels * 2, 16,
    )
    header += struct.pack("<4sI", b"data", data_size)
    return header + pcm_bytes


class AudioManager:
    def __init__(self, data_manager):
        self.data = data_manager
        self._sfx = {}
        self._processes = []
        self._load_all()

    def _path(self, filename):
        p = os.path.join(SOUND_DIR, filename)
        return p if os.path.exists(p) else ""

    def _load_all(self):
        for name, filename in SFX_FILES.items():
            path = self._path(filename)
            if not path:
                self._sfx[name] = None
                continue
            try:
                pcm, rate, ch = _decode_ogg(path)
                self._sfx[name] = (pcm, rate, ch)
            except Exception:
                self._sfx[name] = None

    def _cleanup(self):
        still = []
        for proc, name in self._processes:
            if proc.poll() is not None:
                try:
                    os.unlink(name)
                except Exception:
                    pass
            else:
                still.append((proc, name))
        self._processes = still

    def _apply_volume(self, pcm, volume):
        if volume >= 1.0:
            return pcm
        return pcm * volume

    def play_sfx(self, name):
        if not self.data.is_sfx_on():
            return
        entry = self._sfx.get(name)
        if entry is None:
            return
        pcm, rate, ch = entry
        vol = self.data.get_volume()
        if vol <= 0:
            return
        try:
            scaled = self._apply_volume(pcm, vol)
            wav = _pcm_to_wav(scaled, ch, rate)
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.write(wav)
            tmp.close()
            subprocess.Popen(["afplay", tmp.name],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def stop_music(self):
        for proc, name in self._processes:
            try:
                proc.terminate()
            except Exception:
                pass
            try:
                os.unlink(name)
            except Exception:
                pass
        self._processes.clear()

    def play_music(self):
        pass

    def apply_music_setting(self):
        pass

    def apply_volume(self):
        pass
