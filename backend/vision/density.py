from typing import Dict, Any

class DensityCalculator:
    """Calculates traffic density and breakdown from detected vehicle counts."""

    def __init__(self, traffic_config: Dict[str, Any]):
        self.low_threshold = traffic_config.get("low_density", 5)
        self.medium_threshold = traffic_config.get("medium_density", 10)

    def calculate(self, vehicle_count: int) -> str:
        """Returns density tier: LOW, MEDIUM, or HIGH."""
        if vehicle_count <= self.low_threshold:
            return "LOW"
        elif vehicle_count <= self.medium_threshold:
            return "MEDIUM"
        else:
            return "HIGH"

    def get_color_bgr(self, density: str):
        """Returns BGR color for visualization."""
        if density == "LOW":
            return (0, 200, 0)      # Green
        elif density == "MEDIUM":
            return (0, 215, 255)    # Amber/Yellow
        else:
            return (0, 0, 255)      # Red
