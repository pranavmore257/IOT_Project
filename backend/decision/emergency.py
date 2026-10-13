from typing import Dict, Any, Tuple

class EmergencyEvaluator:
    """Multimodal Fusion Logic combining Audio AI + Video AI evidence."""

    def __init__(
        self,
        audio_weight: float = 0.50,
        video_weight: float = 0.50,
        emergency_threshold: float = 0.75,
        audio_only_timeout_sec: float = 3.0
    ):
        self.audio_weight = audio_weight
        self.video_weight = video_weight
        self.emergency_threshold = emergency_threshold
        self.audio_only_timeout_sec = audio_only_timeout_sec

        self.audio_alert_start_time = None

    def evaluate(self, audio_data: Dict[str, Any], video_data: Dict[str, Any], current_time: float) -> Dict[str, Any]:
        """
        Combines audio and video evidence into an emergency evaluation.
        Returns:
            {
                "is_emergency": bool,
                "mode": str ("NORMAL", "EMERGENCY", "POSSIBLE_EMERGENCY", "ACCIDENT_ALERT", "ADAPTIVE"),
                "priority": str ("LOW", "MEDIUM", "HIGH", "CRITICAL"),
                "emergency_score": float,
                "target_direction": str,
                "reason": str,
                "case": int
            }
        """
        audio_class = audio_data.get("predicted_class", "normal_traffic")
        audio_conf = audio_data.get("confidence", 0.0)
        is_audio_siren = audio_class in ["ambulance_siren", "fire_truck_siren", "police_siren"] and audio_conf >= 0.60
        is_accident_sound = (audio_class == "accident_impact") and audio_conf >= 0.70

        video_ambulance = video_data.get("ambulance_detected", False)
        video_conf = video_data.get("ambulance_confidence", 0.0)
        video_dir = video_data.get("ambulance_direction", "NORTH")
        if video_dir not in ["NORTH", "SOUTH", "EAST", "WEST"]:
            video_dir = "NORTH"

        # Case 4: Accident / Crash Sound
        if is_accident_sound:
            return {
                "is_emergency": True,
                "mode": "ACCIDENT_ALERT",
                "priority": "CRITICAL",
                "emergency_score": round(audio_conf, 2),
                "target_direction": "ALL",
                "reason": f"Acoustic impact detected ({audio_conf*100:.1f}%) - safe intersection hold",
                "case": 4
            }

        # Calculate multimodal fusion score
        a_score = audio_conf if is_audio_siren else 0.0
        v_score = video_conf if video_ambulance else 0.0
        emergency_score = (self.audio_weight * a_score) + (self.video_weight * v_score)

        # Case 1: Audio + Video confirm ambulance
        if is_audio_siren and video_ambulance:
            if emergency_score >= self.emergency_threshold:
                return {
                    "is_emergency": True,
                    "mode": "EMERGENCY",
                    "priority": "HIGH",
                    "emergency_score": round(emergency_score, 2),
                    "target_direction": video_dir,
                    "reason": f"Audio ({audio_conf*100:.0f}%) and Video ({video_conf*100:.0f}%) confirm emergency vehicle approaching {video_dir}",
                    "case": 1
                }

        # Case 2: Audio siren ONLY (no visual ambulance yet)
        if is_audio_siren and not video_ambulance:
            if self.audio_alert_start_time is None:
                self.audio_alert_start_time = current_time

            elapsed = current_time - self.audio_alert_start_time
            if elapsed > self.audio_only_timeout_sec and audio_conf >= 0.85:
                # Upgraded to emergency after temporal confirmation window
                return {
                    "is_emergency": True,
                    "mode": "EMERGENCY",
                    "priority": "MEDIUM",
                    "emergency_score": round(emergency_score, 2),
                    "target_direction": "NORTH",
                    "reason": f"Persistent acoustic siren verified ({audio_conf*100:.0f}%) after {elapsed:.1f}s confirmation",
                    "case": 2
                }
            else:
                return {
                    "is_emergency": False,
                    "mode": "POSSIBLE_EMERGENCY",
                    "priority": "MEDIUM",
                    "emergency_score": round(emergency_score, 2),
                    "target_direction": "NORTH",
                    "reason": f"Siren heard ({audio_conf*100:.0f}%) - awaiting camera visual confirmation ({elapsed:.1f}s)",
                    "case": 2
                }
        else:
            self.audio_alert_start_time = None

        # Case 3: Video ambulance ONLY (no siren sound)
        if video_ambulance and not is_audio_siren:
            if video_conf >= 0.80:
                return {
                    "is_emergency": True,
                    "mode": "EMERGENCY",
                    "priority": "MEDIUM",
                    "emergency_score": round(emergency_score, 2),
                    "target_direction": video_dir,
                    "reason": f"Emergency vehicle visually verified ({video_conf*100:.0f}%) approaching {video_dir} (silent siren)",
                    "case": 3
                }
            else:
                return {
                    "is_emergency": False,
                    "mode": "POSSIBLE_EMERGENCY",
                    "priority": "LOW",
                    "emergency_score": round(emergency_score, 2),
                    "target_direction": video_dir,
                    "reason": f"Possible emergency vehicle visible ({video_conf*100:.0f}%) approaching {video_dir}",
                    "case": 3
                }

        # Case 5: Normal or Adaptive Traffic
        return {
            "is_emergency": False,
            "mode": "NORMAL",
            "priority": "LOW",
            "emergency_score": round(emergency_score, 2),
            "target_direction": "NONE",
            "reason": "Routine traffic conditions",
            "case": 5
        }
