from typing import Dict, Any

class AdaptiveTrafficController:
    """Computes bounded green durations from demand on each traffic axis."""

    def __init__(self, traffic_config: Dict[str, Any]):
        self.normal_green = traffic_config.get("normal_green_time", 10)
        self.high_green = traffic_config.get("high_density_green_time", 20)
        self.min_green = traffic_config.get("min_green_time", 6)
        self.max_green = traffic_config.get("max_green_time", 30)
        self.medium_axis_count = traffic_config.get("medium_axis_count", 4)
        self.high_axis_count = traffic_config.get("high_axis_count", 8)

    def calculate_green_time(self, density: str, vehicle_count: int, direction_counts: Dict[str, int], active_axis: str) -> int:
        """
        Calculates a duration for NS or EW from that axis's own lane counts.

        ``density`` and ``vehicle_count`` remain in the signature for callers that
        already provide them, but total intersection density must not extend an
        otherwise empty axis's green.
        """
        if active_axis == "NS":
            axis_count = direction_counts.get("NORTH", 0) + direction_counts.get("SOUTH", 0)
        elif active_axis == "EW":
            axis_count = direction_counts.get("EAST", 0) + direction_counts.get("WEST", 0)
        else:
            raise ValueError(f"Unsupported traffic axis: {active_axis}")

        if axis_count >= self.high_axis_count:
            duration = self.high_green
        elif axis_count >= self.medium_axis_count:
            duration = int((self.normal_green + self.high_green) / 2)
        else:
            duration = self.normal_green

        return max(self.min_green, min(self.max_green, duration))
