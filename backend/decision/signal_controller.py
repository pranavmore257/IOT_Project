import time
from typing import Dict, Any, Optional

class SignalController:
    """
    Finite State Machine for 4-way intersection (North, South, East, West).
    Enforces safe yellow clearance intervals and emergency preemption.
    """

    def __init__(self, traffic_config: Dict[str, Any], emergency_clear_delay: float = 5.0):
        self.normal_green_time = traffic_config.get("normal_green_time", 10)
        self.yellow_time = traffic_config.get("yellow_time", 3)
        self.all_red_time = traffic_config.get("all_red_time", 1)
        self.emergency_clear_delay = emergency_clear_delay

        # Current state
        self.state = "NS_GREEN"
        self.state_start_time: Optional[float] = None
        self.allocated_duration = self.normal_green_time
        self.mode = "NORMAL"  # NORMAL, ADAPTIVE, EMERGENCY, ACCIDENT_ALERT, MANUAL

        # Emergency preemption tracking
        self.emergency_target_dir: Optional[str] = None
        self.emergency_clear_start: Optional[float] = None

        # Signal states for each direction
        self.signals = {
            "NORTH": "GREEN",
            "SOUTH": "GREEN",
            "EAST": "RED",
            "WEST": "RED"
        }

    def update(
        self,
        current_time: float,
        eval_result: Dict[str, Any],
        adaptive_green: int
    ) -> Dict[str, Any]:
        """Updates FSM based on elapsed time and emergency/adaptive evaluation."""
        if self.state_start_time is None:
            self.state_start_time = current_time

        is_emergency = eval_result.get("is_emergency", False)
        eval_mode = eval_result.get("mode", "NORMAL")
        target_dir = eval_result.get("target_direction", "NORTH")

        # Handle Accident Alert
        if eval_mode == "ACCIDENT_ALERT":
            self.mode = "ACCIDENT_ALERT"
            self.signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "RED", "WEST": "RED"}
            self.state = "ACCIDENT_HOLD"
            return self.get_state_dict(current_time)

        # Handle Emergency Preemption
        if is_emergency and eval_mode == "EMERGENCY":
            self.emergency_clear_start = None  # Reset clear timer
            if self.mode != "EMERGENCY" or self.emergency_target_dir != target_dir:
                self._initiate_emergency_preemption(target_dir, current_time)
            elif self.state == "EMERGENCY_CORRIDOR":
                # Ensure emergency corridor signals remain locked
                self._apply_corridor_signals(target_dir)

            return self.get_state_dict(current_time)

        # If emergency was active but now resolved, handle safe clearance delay
        if self.mode == "EMERGENCY" and not is_emergency:
            if self.emergency_clear_start is None:
                self.emergency_clear_start = current_time

            if current_time - self.emergency_clear_start < self.emergency_clear_delay:
                # Hold corridor until clearance delay finishes
                return self.get_state_dict(current_time)
            else:
                # Safe resumption: transition corridor to YELLOW
                self._resume_normal_traffic(current_time)
                return self.get_state_dict(current_time)

        # Standard / Adaptive Traffic Cycle
        self.mode = "ADAPTIVE" if eval_mode == "ADAPTIVE" or adaptive_green != self.normal_green_time else "NORMAL"
        self._step_normal_cycle(current_time, adaptive_green)
        return self.get_state_dict(current_time)

    def _step_normal_cycle(self, current_time: float, adaptive_green: int):
        elapsed = current_time - self.state_start_time

        if self.state == "NS_GREEN":
            if elapsed >= self.allocated_duration:
                self._transition_to("NS_YELLOW", self.yellow_time, current_time)
                self.signals = {"NORTH": "YELLOW", "SOUTH": "YELLOW", "EAST": "RED", "WEST": "RED"}
            else:
                self.signals = {"NORTH": "GREEN", "SOUTH": "GREEN", "EAST": "RED", "WEST": "RED"}

        elif self.state == "NS_YELLOW":
            if elapsed >= self.allocated_duration:
                self._transition_to("ALL_RED_1", self.all_red_time, current_time)
                self.signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "RED", "WEST": "RED"}
            else:
                self.signals = {"NORTH": "YELLOW", "SOUTH": "YELLOW", "EAST": "RED", "WEST": "RED"}

        elif self.state == "ALL_RED_1":
            if elapsed >= self.allocated_duration:
                self._transition_to("EW_GREEN", adaptive_green, current_time)
                self.signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "GREEN", "WEST": "GREEN"}
            else:
                self.signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "RED", "WEST": "RED"}

        elif self.state == "EW_GREEN":
            if elapsed >= self.allocated_duration:
                self._transition_to("EW_YELLOW", self.yellow_time, current_time)
                self.signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "YELLOW", "WEST": "YELLOW"}
            else:
                self.signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "GREEN", "WEST": "GREEN"}

        elif self.state == "EW_YELLOW":
            if elapsed >= self.allocated_duration:
                self._transition_to("ALL_RED_2", self.all_red_time, current_time)
                self.signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "RED", "WEST": "RED"}
            else:
                self.signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "YELLOW", "WEST": "YELLOW"}

        elif self.state == "ALL_RED_2":
            if elapsed >= self.allocated_duration:
                self._transition_to("NS_GREEN", adaptive_green, current_time)
                self.signals = {"NORTH": "GREEN", "SOUTH": "GREEN", "EAST": "RED", "WEST": "RED"}
            else:
                self.signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "RED", "WEST": "RED"}

        else:
            self._transition_to("NS_GREEN", adaptive_green, current_time)
            self.signals = {"NORTH": "GREEN", "SOUTH": "GREEN", "EAST": "RED", "WEST": "RED"}

    def _initiate_emergency_preemption(self, target_dir: str, current_time: float):
        """Preempts current cycle safely by clearing non-emergency green."""
        self.emergency_target_dir = target_dir
        self.mode = "EMERGENCY"

        # Check if conflicting traffic currently has green
        if target_dir in ["NORTH", "SOUTH"]:
            if self.state in ["EW_GREEN"]:
                # Conflicting EW is GREEN: MUST provide YELLOW clearance
                self._transition_to("EW_YELLOW", self.yellow_time, current_time)
                self.signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "YELLOW", "WEST": "YELLOW"}
                return
            elif self.state in ["EW_YELLOW", "ALL_RED_1", "ALL_RED_2"]:
                return
        elif target_dir in ["EAST", "WEST"]:
            if self.state in ["NS_GREEN"]:
                # Conflicting NS is GREEN: MUST provide YELLOW clearance
                self._transition_to("NS_YELLOW", self.yellow_time, current_time)
                self.signals = {"NORTH": "YELLOW", "SOUTH": "YELLOW", "EAST": "RED", "WEST": "RED"}
                return
            elif self.state in ["NS_YELLOW", "ALL_RED_1", "ALL_RED_2"]:
                return

        # Safe to activate corridor
        self._transition_to("EMERGENCY_CORRIDOR", 30, current_time)
        self._apply_corridor_signals(target_dir)

    def _apply_corridor_signals(self, target_dir: str):
        if target_dir in ["NORTH", "SOUTH"]:
            self.signals = {"NORTH": "GREEN", "SOUTH": "GREEN", "EAST": "RED", "WEST": "RED"}
        else:
            self.signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "GREEN", "WEST": "GREEN"}

    def _resume_normal_traffic(self, current_time: float):
        """Clears emergency corridor by cycling through yellow to next normal state."""
        self.mode = "NORMAL"
        if self.emergency_target_dir in ["NORTH", "SOUTH"]:
            self._transition_to("NS_YELLOW", self.yellow_time, current_time)
            self.signals = {"NORTH": "YELLOW", "SOUTH": "YELLOW", "EAST": "RED", "WEST": "RED"}
        else:
            self._transition_to("EW_YELLOW", self.yellow_time, current_time)
            self.signals = {"NORTH": "RED", "SOUTH": "RED", "EAST": "YELLOW", "WEST": "YELLOW"}
        self.emergency_target_dir = None
        self.emergency_clear_start = None

    def _transition_to(self, new_state: str, duration: int, current_time: float):
        self.state = new_state
        self.allocated_duration = duration
        self.state_start_time = current_time

    def set_manual_signal(self, north: str, south: str, east: str, west: str):
        """Manual signal override for demonstration."""
        self.mode = "MANUAL"
        self.signals = {
            "NORTH": north.upper(),
            "SOUTH": south.upper(),
            "EAST": east.upper(),
            "WEST": west.upper()
        }
        self.state = "MANUAL_OVERRIDE"

    def get_state_dict(self, current_time: float) -> Dict[str, Any]:
        start = self.state_start_time if self.state_start_time is not None else current_time
        elapsed = current_time - start
        remaining = max(0, int(self.allocated_duration - elapsed))
        return {
            "state": self.state,
            "mode": self.mode,
            "signals": dict(self.signals),
            "remaining_seconds": remaining,
            "allocated_seconds": self.allocated_duration,
            "emergency_target": self.emergency_target_dir
        }
