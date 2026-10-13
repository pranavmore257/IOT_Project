import time
import threading
from typing import Optional, Tuple
import numpy as np

class AudioCapture:
    """Non-blocking circular audio capture using sounddevice with synthetic fallback."""

    def __init__(self, sample_rate: int = 16000, chunk_duration: float = 1.5, device_index: int = -1):
        self.sample_rate = sample_rate
        self.chunk_size = int(sample_rate * chunk_duration)
        self.device_index = device_index if device_index >= 0 else None

        self.buffer = np.zeros(self.chunk_size, dtype=np.float32)
        self.lock = threading.Lock()
        self.is_running = False
        self.is_connected = False
        self.stream = None
        self.thread: Optional[threading.Thread] = None

        self._init_stream()

    def _init_stream(self):
        try:
            import sounddevice as sd
            # Test query devices
            devices = sd.query_devices()
            if len(devices) == 0:
                self.is_connected = False
                return

            def callback(indata, frames, time_info, status):
                if status:
                    pass
                mono_data = indata[:, 0] if indata.ndim > 1 else indata
                with self.lock:
                    # Roll buffer and append latest frames
                    n = len(mono_data)
                    if n >= self.chunk_size:
                        self.buffer = mono_data[-self.chunk_size:].astype(np.float32)
                    else:
                        self.buffer = np.roll(self.buffer, -n)
                        self.buffer[-n:] = mono_data.astype(np.float32)

            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                device=self.device_index,
                callback=callback,
                blocksize=int(self.sample_rate * 0.1)  # 100ms blocks
            )
            self.stream.start()
            self.is_connected = True
        except Exception as e:
            print(f"[AudioCapture] Microphone unavailable or sounddevice error ({e}). Running in simulation mode.")
            self.is_connected = False
            self.stream = None

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        if not self.is_connected:
            self.thread = threading.Thread(target=self._synthetic_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.is_running = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def _synthetic_loop(self):
        """Generates subtle synthetic background noise when microphone is absent."""
        while self.is_running:
            # Low level Brownian/white noise simulating quiet room background
            noise = np.random.normal(0, 0.005, int(self.sample_rate * 0.1)).astype(np.float32)
            with self.lock:
                n = len(noise)
                self.buffer = np.roll(self.buffer, -n)
                self.buffer[-n:] = noise
            time.sleep(0.1)

    def get_chunk(self) -> np.ndarray:
        with self.lock:
            return self.buffer.copy()

    def get_status(self) -> dict:
        return {
            "connected": self.is_connected,
            "sample_rate": self.sample_rate,
            "chunk_size": self.chunk_size,
            "device_index": self.device_index
        }
