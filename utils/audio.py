# -*- coding: utf-8 -*-
"""
utils/audio.py

AudioManager: hiệu ứng âm thanh (.ogg), chạy cross-platform.
macOS: afplay | Windows: winsound | Android: Kivy SoundLoader
"""

import os
import sys
import subprocess
import tempfile

try:
    import av
    import numpy as np
    _HAV_AV = True
except ImportError:
    _HAV_AV = False

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
    if not _HAV_AV:
        return None, 0, 0
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
    import struct
    pcm_bytes = (pcm * 32767).clip(-32768, 32767).astype(np.int16).tobytes()
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


def _detect_platform():
    try:
        from kivy.utils import platform
        return platform
    except ImportError:
        return sys.platform


class AudioManager:
    def __init__(self, data_manager):
        self.data = data_manager
        self._sfx = {}
        self._sfx_pcm = {}
        self._processes = []
        self._platform = _detect_platform()
        self._load_all()

    def _path(self, filename):
        p = os.path.join(SOUND_DIR, filename)
        return p if os.path.exists(p) else ""

    def _load_all(self):
        if self._platform == "android" or not _HAV_AV:
            for name, filename in SFX_FILES.items():
                path = self._path(filename)
                self._sfx[name] = path if path else None
        else:
            for name, filename in SFX_FILES.items():
                path = self._path(filename)
                if not path:
                    self._sfx_pcm[name] = None
                    continue
                try:
                    pcm, rate, ch = _decode_ogg(path)
                    self._sfx_pcm[name] = (pcm, rate, ch)
                except Exception:
                    self._sfx_pcm[name] = None

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

    def play_sfx(self, name):
        if not self.data.is_sfx_on():
            return
        vol = self.data.get_volume()
        if vol <= 0:
            return
        if self._sfx_pcm:
            self._play_desktop(name, vol)
        elif self._sfx.get(name):
            self._play_loader(name, vol)

    def _play_loader(self, name, vol):
        path = self._sfx.get(name)
        if not path:
            return
        try:
            from kivy.core.audio import SoundLoader
            sound = SoundLoader.load(path)
            if sound:
                sound.volume = vol
                sound.play()
        except Exception:
            pass

    def _play_desktop(self, name, vol):
        entry = self._sfx_pcm.get(name)
        if entry is None:
            return
        pcm, rate, ch = entry
        try:
            scaled = pcm * vol if vol < 1.0 else pcm
            wav = _pcm_to_wav(scaled, ch, rate)

            if sys.platform == "win32":
                import winsound
                winsound.PlaySound(wav, winsound.SND_MEMORY | winsound.SND_ASYNC)
            else:
                self._cleanup()
                tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                tmp.write(wav)
                tmp.close()
                cmd = "aplay" if sys.platform == "linux" else "afplay"
                proc = subprocess.Popen(
                    [cmd, tmp.name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self._processes.append((proc, tmp.name))
        except Exception:
            pass

    def stop_all(self):
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
        if sys.platform == "win32":
            try:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
