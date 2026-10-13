import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import wave
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
import joblib

from backend.audio.feature_extraction import AudioFeatureExtractor

CLASS_MAP = {
    "ambulance": "ambulance_siren",
    "fire_truck": "fire_truck_siren",
    "police": "police_siren",
    "honking": "heavy_honking",
    "accident": "accident_impact",
    "normal": "normal_traffic"
}

def load_wav(filepath: Path) -> np.ndarray:
    with wave.open(str(filepath), "rb") as wf:
        n_frames = wf.getnframes()
        frames = wf.readframes(n_frames)
        samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        return samples

def main():
    data_dir = Path("data/audio")
    output_model_dir = Path("models/audio")
    output_model_dir.mkdir(parents=True, exist_ok=True)

    if not data_dir.exists() or len(list(data_dir.iterdir())) == 0:
        print("[Error] No dataset found. Please run scripts/prepare_audio_dataset.py first.")
        return

    extractor = AudioFeatureExtractor(sample_rate=16000, n_mfcc=20)
    X = []
    y = []

    print("[Training] Extracting MFCC features from data/audio/...")
    for folder in data_dir.iterdir():
        if not folder.is_dir():
            continue
        label = CLASS_MAP.get(folder.name, folder.name)
        wav_files = list(folder.glob("*.wav"))

        for wav_path in wav_files:
            try:
                audio = load_wav(wav_path)
                feat = extractor.extract_features(audio)
                X.append(feat["mfcc"])
                y.append(label)
            except Exception as e:
                print(f"Skipping {wav_path}: {e}")

    X = np.array(X)
    y = np.array(y)
    print(f"[Training] Loaded {len(X)} total audio samples across {len(np.unique(y))} classes.")

    # Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    print("[Training] Fitting Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train_scaled, y_train)

    # Evaluation
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    print("\n" + "="*50)
    print("           MODEL EVALUATION RESULTS")
    print("="*50)
    print(f"Accuracy:  {acc*100:.2f}%")
    print(f"Precision: {prec*100:.2f}%")
    print(f"Recall:    {rec*100:.2f}%")
    print(f"F1 Score:  {f1*100:.2f}%")
    print("="*50)
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Save trained model and scaler
    model_path = output_model_dir / "audio_classifier.pkl"
    joblib.dump({"model": model, "scaler": scaler}, str(model_path))
    print(f"[Training] Saved model to {model_path}")

    # Save metrics JSON
    metrics = {
        "model_type": "RandomForestClassifier",
        "features": "20-MFCC Coefficients",
        "sample_rate": 16000,
        "classes": list(np.unique(y)),
        "samples_count": len(X),
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "evaluated": True
    }
    metrics_path = output_model_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"[Training] Saved metrics to {metrics_path}")

if __name__ == "__main__":
    main()
