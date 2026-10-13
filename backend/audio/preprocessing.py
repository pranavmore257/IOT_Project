import numpy as np

def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """Normalizes audio samples to range [-1.0, 1.0]."""
    if len(audio) == 0:
        return audio
    max_val = np.max(np.abs(audio))
    if max_val > 1e-6:
        return audio / max_val
    return audio

def calculate_rms(audio: np.ndarray) -> float:
    """Calculates Root Mean Square (RMS) energy level."""
    if len(audio) == 0:
        return 0.0
    return float(np.sqrt(np.mean(audio ** 2)))

def calculate_activity_percentage(audio: np.ndarray, min_db: float = -50.0, max_db: float = -5.0) -> float:
    """
    Computes an intuitive 0.0 - 100.0 audio activity percentage
    based on decibel energy relative to silence.
    """
    rms = calculate_rms(audio)
    if rms < 1e-5:
        return 0.0
    db = 20.0 * np.log10(rms + 1e-9)
    # Map [min_db, max_db] to [0.0, 100.0]
    scaled = (db - min_db) / (max_db - min_db) * 100.0
    return float(np.clip(scaled, 0.0, 100.0))

def apply_pre_emphasis(audio: np.ndarray, coeff: float = 0.97) -> np.ndarray:
    """High-pass pre-emphasis filter to balance high frequency energy."""
    if len(audio) < 2:
        return audio
    return np.append(audio[0], audio[1:] - coeff * audio[:-1])

def get_waveform_downsampled(audio: np.ndarray, target_points: int = 40) -> list:
    """Downsamples audio chunk to a small list of floats for live dashboard visualization."""
    if len(audio) == 0:
        return [0.0] * target_points
    step = max(1, len(audio) // target_points)
    sampled = [float(abs(audio[i])) for i in range(0, len(audio), step)[:target_points]]
    # Pad if needed
    while len(sampled) < target_points:
        sampled.append(0.0)
    return sampled
