import unittest
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.test_density import test_density_thresholds
from tests.test_emergency import (
    test_audio_video_emergency,
    test_audio_only_does_not_immediately_trigger,
    test_accident_impact_detection
)
from tests.test_signal_controller import (
    test_signal_transition_is_safe,
    test_emergency_preemption_safety
)
from tests.test_decision_engine import test_high_traffic_extends_green

class TestTrafficAI(unittest.TestCase):
    def test_density(self):
        test_density_thresholds()

    def test_emergency_audio_video(self):
        test_audio_video_emergency()

    def test_emergency_audio_only(self):
        test_audio_only_does_not_immediately_trigger()

    def test_emergency_accident(self):
        test_accident_impact_detection()

    def test_signal_safety(self):
        test_signal_transition_is_safe()

    def test_emergency_preemption(self):
        test_emergency_preemption_safety()

    def test_adaptive_green(self):
        test_high_traffic_extends_green()

if __name__ == "__main__":
    unittest.main()
