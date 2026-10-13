import time
import threading
from typing import Dict, Any, Optional
import numpy as np

from backend.config.settings import CONFIG
from backend.audio.audio_capture import AudioCapture
from backend.audio.preprocessing import (
    calculate_rms,
    calculate_activity_percentage,
    get_waveform_downsampled,
    normalize_audio
)
from backend.audio.feature_extraction import AudioFeatureExtractor
from backend.audio.model import AudioClassifierModel
from backend.audio.labels import AUDIO_DISPLAY_NAMES, EMERGENCY_AUDIO_CLASSES

class AudioPipeline:
    """End-to-end background audio processing and inference pipeline."""

    def __init__(self):
        a_cfg = CONFIG.get("audio", {})
        self.sample_rate = a_cfg.get("sample_rate", 16000)
        self.chunk_duration = a_cfg.get("chunk_duration", 1.5)
        self.conf_threshold = a_cfg.get("confidence_threshold", 0.65)

        self.capture = AudioCapture(
            sample_rate=self.sample_rate,
            chunk_duration=self.chunk_duration,
            device_index=a_cfg.get("device_index", -1)
        )
        self.extractor = AudioFeatureExtractor(
            sample_rate=self.sample_rate,
            n_mfcc=a_cfg.get("n_mfcc", 20),
            n_mels=a_cfg.get("n_mels", 64)
        )
        self.model = AudioClassifierModel(
            model_path=a_cfg.get("model_path", "models/audio/audio_classifier.pkl")
        )

        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        # State outputs
        self.latest_result: Dict[str, Any] = {
            "predicted_class": "normal_traffic",
            "display_name": "Normal Traffic Sound",
            "confidence": 0.85,
            "status": "NORMAL",
            "activity_pct": 0.0,
            "rms": 0.0,
            "waveform": [0.0] * 32,
            "inference_mode": "INITIALIZING",
            "is_microphone_connected": False,
            "demo_override": False,
            "timestamp": time.time()
        }

        # Demo simulation overrides
        self.demo_override_active = False
        self.demo_data: Optional[Dict[str, Any]] = None

    def start(self):
        if self.is_running:
            return
        self.capture.start()
        self.is_running = True
        self.thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.capture.stop()

    def set_demo_override(self, active: bool, data: Optional[Dict[str, Any]] = None):
        with self.lock:
            self.demo_override_active = active
            self.demo_data = data

    def _processing_loop(self):
        while self.is_running:
            raw_chunk = self.capture.get_chunk()
            rms = calculate_rms(raw_chunk)
            activity = calculate_activity_percentage(raw_chunk)
            waveform = get_waveform_downsampled(raw_chunk, target_points=32)

            with self.lock:
                is_override = self.demo_override_active
                override_info = dict(self.demo_data) if self.demo_data else {}

            if is_override and override_info:
                pred_class = override_info.get("class", "ambulance_siren")
                confidence = override_info.get("confidence", 0.95)
                inf_mode = "DEMO_MODE"
                # Synthetic high activity for demonstration
                activity = max(activity, 75.0)
                # Synthetic pulsating waveform
                waveform = [(0.3 + 0.5 * np.sin(i * 0.4 + time.time() * 5.0) ** 2) for i in range(32)]
            else:
                norm_chunk = normalize_audio(raw_chunk)
                features = self.extractor.extract_features(norm_chunk)
                pred_class, confidence, inf_mode = self.model.predict(features, raw_chunk)

            display_name = AUDIO_DISPLAY_NAMES.get(pred_class, pred_class.replace("_", " ").title())
            status = EMERGENCY_AUDIO_CLASSES.get(pred_class, "NORMAL")

            with self.lock:
                self.latest_result = {
                    "predicted_class": pred_class,
                    "display_name": display_name,
                    "confidence": round(confidence, 2),
                    "status": status,
                    "activity_pct": round(activity, 1),
                    "rms": round(rms, 4),
                    "waveform": [round(float(v), 3) for v in waveform],
                    "inference_mode": inf_mode,
                    "is_microphone_connected": self.capture.get_status()["connected"],
                    "demo_override": is_override,
                    "timestamp": time.time()
                }

            time.sleep(0.12)

    def get_latest_result(self) -> Dict[str, Any]:
        with self.lock:
            return dict(self.latest_result)
