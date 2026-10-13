import time
from typing import Dict, Any, Optional
from backend.config.settings import CONFIG
from backend.decision.emergency import EmergencyEvaluator
from backend.decision.adaptive_control import AdaptiveTrafficController
from backend.decision.signal_controller import SignalController
from backend.database.database import log_event

class MultimodalDecisionEngine:
    """Combines Video AI + Audio AI + Traffic Density to control 4-way traffic signals."""

    def __init__(self):
        e_cfg = CONFIG.get("emergency", {})
        t_cfg = CONFIG.get("traffic", {})

        self.evaluator = EmergencyEvaluator(
            audio_weight=e_cfg.get("audio_weight", 0.50),
            video_weight=e_cfg.get("video_weight", 0.50),
            emergency_threshold=e_cfg.get("threshold", 0.75),
            audio_only_timeout_sec=e_cfg.get("audio_only_confirmation_window_sec", 3.0)
        )
        self.adaptive_ctrl = AdaptiveTrafficController(t_cfg)
        self.signal_ctrl = SignalController(
            traffic_config=t_cfg,
            emergency_clear_delay=e_cfg.get("emergency_clear_delay_sec", 5.0)
        )

        self.last_logged_mode = "NORMAL"
        self.last_logged_state = "NS_GREEN"
        self.last_log_time = 0.0

    def process(self, audio_data: Dict[str, Any], video_data: Dict[str, Any]) -> Dict[str, Any]:
        current_time = time.time()

        # 1. Multimodal Emergency Evaluation
        eval_result = self.evaluator.evaluate(audio_data, video_data, current_time)

        # 2. Determine active axis based on current state
        curr_state = self.signal_ctrl.state
        active_axis = "EW" if "EW" in curr_state else "NS"

        # 3. Adaptive Green Calculation
        density = video_data.get("density", "LOW")
        veh_count = video_data.get("vehicle_count", 0)
        dir_counts = video_data.get("direction_counts", {})
        adaptive_green = self.adaptive_ctrl.calculate_green_time(
            density, veh_count, dir_counts, active_axis
        )

        # 4. Step Signal Controller FSM
        signal_state = self.signal_ctrl.update(current_time, eval_result, adaptive_green)

        # 5. Database Logging for notable events
        mode = signal_state.get("mode", "NORMAL")
        state = signal_state.get("state", "NS_GREEN")

        # Log on mode change, state change, or every 30 seconds
        should_log = (
            mode != self.last_logged_mode or
            (mode == "EMERGENCY" and state != self.last_logged_state) or
            (current_time - self.last_log_time > 30.0 and mode != "NORMAL")
        )

        if should_log:
            event_name = f"Signal {state} ({mode})"
            if eval_result.get("is_emergency"):
                event_name = f"EMERGENCY: {eval_result.get('reason')}"
            elif mode == "ACCIDENT_ALERT":
                event_name = f"ALERT: {eval_result.get('reason')}"
            elif mode == "ADAPTIVE" and density == "HIGH":
                event_name = f"Congestion Adaptive Green ({adaptive_green}s)"

            log_event(
                event_type=event_name,
                audio_class=audio_data.get("predicted_class"),
                audio_confidence=audio_data.get("confidence"),
                video_class="ambulance" if video_data.get("ambulance_detected") else "traffic",
                video_confidence=video_data.get("ambulance_confidence") if video_data.get("ambulance_detected") else None,
                vehicle_count=veh_count,
                density=density,
                direction=eval_result.get("target_direction"),
                decision=eval_result.get("reason"),
                signal_state=str(signal_state.get("signals")),
                mode=mode
            )
            self.last_logged_mode = mode
            self.last_logged_state = state
            self.last_log_time = current_time

        # Unified response dictionary
        return {
            "mode": mode,
            "priority": eval_result.get("priority", "LOW"),
            "emergency_score": eval_result.get("emergency_score", 0.0),
            "target_direction": eval_result.get("target_direction", "NONE"),
            "reason": eval_result.get("reason", "Routine cycle"),
            "adaptive_green_seconds": adaptive_green,
            "signal_state": signal_state,
            "fusion_math": {
                "audio_weight": self.evaluator.audio_weight,
                "video_weight": self.evaluator.video_weight,
                "audio_score": audio_data.get("confidence", 0.0) if audio_data.get("status") in ["EMERGENCY", "ACCIDENT"] else 0.0,
                "video_score": video_data.get("ambulance_confidence", 0.0) if video_data.get("ambulance_detected") else 0.0,
                "threshold": self.evaluator.emergency_threshold
            },
            "timestamp": current_time
        }
