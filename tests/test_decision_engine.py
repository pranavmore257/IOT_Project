import pytest
from backend.decision.decision_engine import MultimodalDecisionEngine

def test_high_traffic_extends_green():
    engine = MultimodalDecisionEngine()

    audio_normal = {"predicted_class": "normal_traffic", "confidence": 0.85, "status": "NORMAL"}
    video_high_traffic = {
        "vehicle_count": 14,
        "counts": {"car": 10, "motorcycle": 2, "bus": 1, "truck": 1, "ambulance": 0},
        "density": "HIGH",
        "ambulance_detected": False,
        "ambulance_confidence": 0.0,
        "ambulance_direction": "NONE",
        "direction_counts": {"NORTH": 8, "SOUTH": 4, "EAST": 1, "WEST": 1}
    }

    res = engine.process(audio_normal, video_high_traffic)
    assert res["adaptive_green_seconds"] >= 20
    assert res["mode"] in ["NORMAL", "ADAPTIVE"]
