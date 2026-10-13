from typing import Tuple, Dict, Any

class ROIManager:
    """Manages 4-way intersection Regions of Interest (North, South, East, West)."""
    
    def __init__(self, roi_config: Dict[str, Any]):
        self.config = roi_config

    def get_direction(self, bbox: Tuple[int, int, int, int], frame_w: int, frame_h: int) -> str:
        """
        Determines direction (NORTH, SOUTH, EAST, WEST, or CENTER)
        based on the bounding box centroid (x1, y1, x2, y2).
        """
        x1, y1, x2, y2 = bbox
        cx = (x1 + x2) / 2.0 / max(frame_w, 1)
        cy = (y1 + y2) / 2.0 / max(frame_h, 1)

        # Check ROI boxes from config
        for direction, bounds in self.config.items():
            if (bounds["y_min"] <= cy <= bounds["y_max"] and
                bounds["x_min"] <= cx <= bounds["x_max"]):
                return direction.upper()

        # Fallback to nearest quadrant if outside exact boxes
        dx = cx - 0.5
        dy = cy - 0.5
        if abs(dy) > abs(dx):
            return "NORTH" if dy < 0 else "SOUTH"
        else:
            return "WEST" if dx < 0 else "EAST"

    def draw_rois(self, frame, cv2_module):
        """Draws visual quadrant boundaries on the video frame for presentation."""
        h, w = frame.shape[:2]
        colors = {
            "north": (0, 165, 255),  # Orange
            "south": (255, 255, 0),  # Cyan
            "east":  (255, 0, 255),  # Magenta
            "west":  (0, 255, 0),    # Green
        }
        for name, bounds in self.config.items():
            x1 = int(bounds["x_min"] * w)
            y1 = int(bounds["y_min"] * h)
            x2 = int(bounds["x_max"] * w)
            y2 = int(bounds["y_max"] * h)
            color = colors.get(name.lower(), (200, 200, 200))
            cv2_module.rectangle(frame, (x1, y1), (x2, y2), color, 1, cv2_module.LINE_AA)
            cv2_module.putText(
                frame,
                f"ROI: {name.upper()}",
                (x1 + 6, y1 + 18),
                cv2_module.FONT_HERSHEY_SIMPLEX,
                0.45,
                color,
                1,
                cv2_module.LINE_AA
            )
        return frame
