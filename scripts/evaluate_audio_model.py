import json
from pathlib import Path

def main():
    metrics_path = Path("models/audio/metrics.json")
    model_path = Path("models/audio/audio_classifier.pkl")

    print("\n" + "="*60)
    print("      SMART ACOUSTIC TRAFFIC SIGNAL - MODEL METRICS")
    print("="*60)

    if not model_path.exists() or not metrics_path.exists():
        print("[Status] Model not evaluated yet.")
        print("To train and evaluate the audio classifier, run:")
        print("  1. python scripts/prepare_audio_dataset.py")
        print("  2. python scripts/train_audio_model.py")
        print("="*60)
        return

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    print(f"Model Architecture: {metrics.get('model_type', 'Custom Classifier')}")
    print(f"Feature Extractor:  {metrics.get('features', 'MFCC')}")
    print(f"Sample Rate:        {metrics.get('sample_rate', 16000)} Hz")
    print(f"Total Dataset Size: {metrics.get('samples_count', 0)} samples")
    print("-" * 60)
    print(f"Accuracy:           {metrics.get('accuracy', 0)*100:.2f}%")
    print(f"Precision (macro):  {metrics.get('precision', 0)*100:.2f}%")
    print(f"Recall (macro):     {metrics.get('recall', 0)*100:.2f}%")
    print(f"F1 Score:           {metrics.get('f1_score', 0)*100:.2f}%")
    print("-" * 60)
    print("Supported Classes:")
    for cls in metrics.get("classes", []):
        print(f"  - {cls}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
