import pytest
import time
from backend.decision.emergency import EmergencyEvaluator

def test_audio_video_emergency():
    evaluator = EmergencyEvaluator(audio_weight=0.5, video_weight=0.5, emergency_threshold=0.75)
    current_time = time.time()

    audio_data = {"predicted_class": "ambulance_siren", "confidence": 0.95}
    video_data = {"ambulance_detected": True, "ambulance_confidence": 0.92, "ambulance_direction": "NORTH"}

    res = evaluator.evaluate(audio_data, video_data, current_time)
    assert res["is_emergency"] is True
    assert res["mode"] == "EMERGENCY"
    assert res["priority"] == "HIGH"
    assert res["target_direction"] == "NORTH"
    assert res["emergency_score"] >= 0.75
    assert res["case"] == 1

def test_audio_only_does_not_immediately_trigger():
    evaluator = EmergencyEvaluator(audio_weight=0.5, video_weight=0.5, emergency_threshold=0.75, audio_only_timeout_sec=3.0)
    current_time = 1000.0

    audio_data = {"predicted_class": "ambulance_siren", "confidence": 0.90}
    video_data = {"ambulance_detected": False, "ambulance_confidence": 0.0, "ambulance_direction": "NONE"}

    # Initial frame
    res = evaluator.evaluate(audio_data, video_data, current_time)
    assert res["is_emergency"] is False
    assert res["mode"] == "POSSIBLE_EMERGENCY"
    assert res["case"] == 2

    # After only 1 second (below 3.0s threshold) -> Still awaiting video confirmation
    res2 = evaluator.evaluate(audio_data, video_data, current_time + 1.0)
    assert res2["is_emergency"] is False
    assert res2["mode"] == "POSSIBLE_EMERGENCY"

def test_accident_impact_detection():
    evaluator = EmergencyEvaluator()
    current_time = time.time()

    audio_data = {"predicted_class": "accident_impact", "confidence": 0.92}
    video_data = {"ambulance_detected": False, "ambulance_confidence": 0.0}

    res = evaluator.evaluate(audio_data, video_data, current_time)
    assert res["is_emergency"] is True
    assert res["mode"] == "ACCIDENT_ALERT"
    assert res["priority"] == "CRITICAL"
    assert res["case"] == 4
