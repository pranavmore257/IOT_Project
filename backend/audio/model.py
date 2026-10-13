import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import numpy as np

from backend.audio.labels import AUDIO_CLASSES
from backend.audio.preprocessing import calculate_rms

class AudioClassifierModel:
    """Modular Audio Classifier supporting trained models and honest acoustic heuristics."""

    def __init__(self, model_path: str = "models/audio/audio_classifier.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        self.scaler = None
        self.is_trained_model_loaded = False

        self._load_model()

    def _load_model(self):
        if self.model_path.exists():
            try:
                import joblib
                saved_data = joblib.load(str(self.model_path))
                if isinstance(saved_data, dict):
                    self.model = saved_data.get("model")
                    self.scaler = saved_data.get("scaler")
                else:
                    self.model = saved_data
                self.is_trained_model_loaded = True
                print(f"[AudioClassifierModel] Loaded trained model from {self.model_path}")
            except Exception as e:
                print(f"[AudioClassifierModel] Could not load model from {self.model_path}: {e}")
                self.model = None
                self.is_trained_model_loaded = False
        else:
            self.model = None
            self.is_trained_model_loaded = False

    def predict(self, features: Dict[str, Any], raw_audio: np.ndarray) -> Tuple[str, float, str]:
        """
        Returns (predicted_class, confidence, inference_mode).
        inference_mode is 'TRAINED_MODEL' or 'HEURISTIC_BASELINE'.
        """
        # If trained model is available, use it
        if self.is_trained_model_loaded and self.model is not None:
            try:
                mfcc_feat = features["mfcc"].reshape(1, -1)
                if self.scaler:
                    mfcc_feat = self.scaler.transform(mfcc_feat)
                
                if hasattr(self.model, "predict_proba"):
                    probs = self.model.predict_proba(mfcc_feat)[0]
                    best_idx = int(np.argmax(probs))
                    best_conf = float(probs[best_idx])
                    pred_class = self.model.classes_[best_idx]
                else:
                    pred_class = self.model.predict(mfcc_feat)[0]
                    best_conf = 0.85

                return str(pred_class), round(best_conf, 2), "TRAINED_MODEL"
            except Exception as e:
                print(f"[AudioClassifierModel] Inference error with trained model: {e}")

        # Otherwise, run the physics-based acoustic heuristic baseline
        return self._heuristic_prediction(features, raw_audio)

    def _heuristic_prediction(self, features: Dict[str, Any], raw_audio: np.ndarray) -> Tuple[str, float, str]:
        """Acoustic feature analysis for sirens, honking, accidents, and normal ambient traffic."""
        rms = calculate_rms(raw_audio)
        dom_freq = features.get("dominant_freq", 0.0)
        centroid = features.get("spectral_centroid", 0.0)
        zcr = features.get("zero_crossing_rate", 0.0)

        # 1. Very quiet sound -> Normal ambient traffic
        if rms < 0.015:
            return "normal_traffic", 0.90, "HEURISTIC_BASELINE"

        # 2. Impact / Accident Detection
        # Explosive transient: high peak-to-RMS crest factor and high broadband energy
        peak = float(np.max(np.abs(raw_audio)))
        crest_factor = peak / (rms + 1e-6)
        if crest_factor > 6.0 and rms > 0.08 and zcr > 0.15:
            conf = min(0.95, 0.65 + (crest_factor / 15.0) * 0.3)
            return "accident_impact", round(conf, 2), "HEURISTIC_BASELINE"

        # 3. Heavy Honking
        # Concentrated fundamental horn frequency in 350-850 Hz with high sustained loudness
        if 350 <= dom_freq <= 850 and rms > 0.05 and centroid < 1600:
            conf = min(0.92, 0.60 + rms * 3.0)
            return "heavy_honking", round(conf, 2), "HEURISTIC_BASELINE"

        # 4. Siren Analysis (Dominant frequencies in typical siren bandwidths 600 - 1500 Hz)
        if 600 <= dom_freq <= 1600 and rms > 0.03:
            # Check modulation or specific ranges
            if 700 <= dom_freq <= 1050:
                # Classic two-tone or wail ambulance frequency
                conf = min(0.94, 0.68 + (rms * 2.5))
                return "ambulance_siren", round(conf, 2), "HEURISTIC_BASELINE"
            elif 1050 < dom_freq <= 1550:
                # High-pitch police yelp
                conf = min(0.91, 0.65 + (rms * 2.5))
                return "police_siren", round(conf, 2), "HEURISTIC_BASELINE"
            elif 550 <= dom_freq < 700:
                # Fire engine low dual-horn
                conf = min(0.90, 0.65 + (rms * 2.5))
                return "fire_truck_siren", round(conf, 2), "HEURISTIC_BASELINE"

        # 5. Default traffic background
        return "normal_traffic", 0.80, "HEURISTIC_BASELINE"
