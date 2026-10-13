from typing import Dict, Any

class AdaptiveTrafficController:
    """Computes dynamic green signal durations based on real-time vehicle density."""

    def __init__(self, traffic_config: Dict[str, Any]):
        self.normal_green = traffic_config.get("normal_green_time", 10)
        self.high_green = traffic_config.get("high_density_green_time", 20)
        self.min_green = traffic_config.get("min_green_time", 6)
        self.max_green = traffic_config.get("max_green_time", 30)

    def calculate_green_time(self, density: str, vehicle_count: int, direction_counts: Dict[str, int], active_axis: str) -> int:
        """
        Calculates adaptive green duration for the currently green axis ('NS' or 'EW').
        """
        if active_axis == "NS":
            axis_count = direction_counts.get("NORTH", 0) + direction_counts.get("SOUTH", 0)
        else:
            axis_count = direction_counts.get("EAST", 0) + direction_counts.get("WEST", 0)

        # Base duration from overall density
        if density == "HIGH" or axis_count >= 8:
            duration = self.high_green
        elif density == "MEDIUM" or axis_count >= 4:
            duration = int((self.normal_green + self.high_green) / 2)
        else:
            duration = self.normal_green

        # Clamp between bounds
        return max(self.min_green, min(self.max_green, duration))
