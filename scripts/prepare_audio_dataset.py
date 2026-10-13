import os
import math
import numpy as np
from pathlib import Path
import wave

SAMPLE_RATE = 16000
DURATION = 2.0  # seconds

def write_wav(filepath: Path, samples: np.ndarray):
    samples = np.clip(samples, -1.0, 1.0)
    int_samples = (samples * 32767.0).astype(np.int16)
    with wave.open(str(filepath), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int_samples.tobytes())

def generate_ambulance(t: np.ndarray) -> np.ndarray:
    """Ambulance: two-tone alternating pitch (750 Hz and 960 Hz)."""
    f = np.where((t % 0.7) < 0.35, 750.0, 960.0)
    phase = 2 * np.pi * np.cumsum(f) / SAMPLE_RATE
    tone = 0.6 * np.sin(phase) + 0.15 * np.sin(2 * phase)
    noise = 0.05 * np.random.normal(0, 1, len(t))
    return tone + noise

def generate_fire_truck(t: np.ndarray) -> np.ndarray:
    """Fire truck: continuous low wail with deep dual pitch (550 Hz to 850 Hz)."""
    f = 700.0 + 150.0 * np.sin(2 * np.pi * 0.4 * t)
    phase = 2 * np.pi * np.cumsum(f) / SAMPLE_RATE
    tone = 0.65 * np.sin(phase) + 0.2 * np.sin(1.5 * phase)
    noise = 0.05 * np.random.normal(0, 1, len(t))
    return tone + noise

def generate_police(t: np.ndarray) -> np.ndarray:
    """Police: rapid high-pitched yelp (850 Hz to 1450 Hz)."""
    f = 1150.0 + 300.0 * np.sin(2 * np.pi * 3.0 * t)
    phase = 2 * np.pi * np.cumsum(f) / SAMPLE_RATE
    tone = 0.6 * np.sin(phase) + 0.15 * np.sin(3 * phase)
    noise = 0.05 * np.random.normal(0, 1, len(t))
    return tone + noise

def generate_honking(t: np.ndarray) -> np.ndarray:
    """Vehicle horn: sustained dual-frequency pulse (420 Hz & 510 Hz) with pauses."""
    envelope = np.where((t % 0.8) < 0.5, 0.75, 0.05)
    horn = 0.4 * np.sin(2 * np.pi * 420.0 * t) + 0.4 * np.sin(2 * np.pi * 510.0 * t)
    noise = 0.05 * np.random.normal(0, 1, len(t))
    return envelope * horn + noise

def generate_accident(t: np.ndarray) -> np.ndarray:
    """Accident: sudden metallic impact burst with rapid exponential decay."""
    burst_idx = int(0.3 * SAMPLE_RATE)
    envelope = np.zeros_like(t)
    decay = np.exp(-12.0 * (t[burst_idx:] - t[burst_idx]))
    envelope[burst_idx:burst_idx + len(decay)] = decay
    crunch = np.random.normal(0, 1, len(t)) * envelope * 0.95
    thud = 0.5 * np.sin(2 * np.pi * 120.0 * t) * envelope
    return crunch + thud

def generate_normal_traffic(t: np.ndarray) -> np.ndarray:
    """Normal traffic: steady low-frequency engine rumble + pink noise."""
    rumble = 0.15 * np.sin(2 * np.pi * 65.0 * t) + 0.1 * np.sin(2 * np.pi * 130.0 * t)
    noise = 0.12 * np.random.normal(0, 1, len(t))
    return rumble + noise

def main():
    base_dir = Path("data/audio")
    classes = {
        "ambulance": generate_ambulance,
        "fire_truck": generate_fire_truck,
        "police": generate_police,
        "honking": generate_honking,
        "accident": generate_accident,
        "normal": generate_normal_traffic
    }

    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    samples_per_class = 20

    print("Generating audio dataset in data/audio/...")
    for class_name, generator in classes.items():
        folder = base_dir / class_name
        folder.mkdir(parents=True, exist_ok=True)

        for i in range(samples_per_class):
            jitter = np.random.uniform(0.95, 1.05)
            audio = generator(t * jitter)
            # Add random variation
            audio += np.random.normal(0, 0.02, len(audio))
            filepath = folder / f"sample_{i+1:03d}.wav"
            write_wav(filepath, audio)

        print(f"Generated {samples_per_class} samples in {folder}")

    print("\nDataset generation complete! You can now run scripts/train_audio_model.py")

if __name__ == "__main__":
    main()
