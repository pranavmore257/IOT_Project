import time
import threading
from typing import Dict, Any, Optional
import cv2
import numpy as np

from backend.config.settings import CONFIG
from backend.vision.camera import VideoCamera
from backend.vision.detector import VehicleDetector
from backend.vision.roi import ROIManager
from backend.vision.density import DensityCalculator
from backend.vision.tracker import SimpleCentroidTracker

class VisionPipeline:
    """End-to-end background vision processing pipeline."""

    def __init__(self):
        v_cfg = CONFIG.get("video", {})
        t_cfg = CONFIG.get("traffic", {})

        self.camera = VideoCamera(
            camera_index=v_cfg.get("camera_index", 0),
            width=v_cfg.get("width", 640),
            height=v_cfg.get("height", 480)
        )
        self.detector = VehicleDetector(
            model_name=v_cfg.get("model_name", "yolov8n.pt"),
            conf_threshold=v_cfg.get("confidence_threshold", 0.45)
        )
        self.roi_manager = ROIManager(v_cfg.get("roi", {}))
        self.density_calc = DensityCalculator(t_cfg)
        self.tracker = SimpleCentroidTracker()

        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        # State outputs
        self.latest_jpeg: Optional[bytes] = None
        self.latest_result: Dict[str, Any] = {
            "vehicle_count": 0,
            "counts": {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0, "ambulance": 0},
            "density": "LOW",
            "ambulance_detected": False,
            "ambulance_confidence": 0.0,
            "ambulance_direction": "NONE",
            "direction_counts": {"NORTH": 0, "SOUTH": 0, "EAST": 0, "WEST": 0},
            "fps": 0.0,
            "inference_ms": 0.0,
            "demo_override": False,
            "is_camera_connected": False,
            "timestamp": time.time()
        }

        # Demo simulation overrides
        self.demo_override_active = False
        self.demo_data: Optional[Dict[str, Any]] = None

    def start(self):
        if self.is_running:
            return
        self.camera.start()
        self.is_running = True
        self.thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.camera.stop()

    def set_demo_override(self, active: bool, data: Optional[Dict[str, Any]] = None):
        """Allows demo mode triggers to inject simulated visual state."""
        with self.lock:
            self.demo_override_active = active
            self.demo_data = data

    def _processing_loop(self):
        prev_time = time.perf_counter()
        frame_count = 0
        fps = 0.0

        while self.is_running:
            ret, frame = self.camera.get_frame()
            if not ret or frame is None:
                time.sleep(0.03)
                continue

            h, w = frame.shape[:2]

            # Handle Demo Override if active
            with self.lock:
                is_override = self.demo_override_active
                override_info = dict(self.demo_data) if self.demo_data else {}

            if is_override and override_info:
                # Inject visual emergency box or vehicle clusters for demo demonstration
                frame = self._render_demo_overlay(frame, override_info)
                detections = override_info.get("detections", [])
                counts = override_info.get("counts", {})
                density = override_info.get("density", "MEDIUM")
                ambulance_det = override_info.get("ambulance_detected", False)
                ambulance_conf = override_info.get("ambulance_confidence", 0.92)
                ambulance_dir = override_info.get("ambulance_direction", "NORTH")
                dir_counts = override_info.get("direction_counts", {"NORTH": 5, "SOUTH": 2, "EAST": 1, "WEST": 1})
            else:
                # Run real YOLO detection
                detections, inf_time = self.detector.detect(frame)

                # Assign direction based on ROI for each vehicle
                ambulance_det = False
                ambulance_conf = 0.0
                ambulance_dir = "NONE"
                dir_counts = {"NORTH": 0, "SOUTH": 0, "EAST": 0, "WEST": 0}
                counts = {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0, "ambulance": 0}

                for det in detections:
                    direction = self.roi_manager.get_direction(det["bbox"], w, h)
                    det["direction"] = direction
                    if direction in dir_counts:
                        dir_counts[direction] += 1

                    cls_name = det["class"]
                    if cls_name in counts:
                        counts[cls_name] += 1

                    if det.get("is_emergency") or cls_name == "ambulance":
                        ambulance_det = True
                        if det["confidence"] > ambulance_conf:
                            ambulance_conf = det["confidence"]
                            ambulance_dir = direction

                # Simple tracking
                self.tracker.update(detections)

                total_vehicles = sum(counts.values())
                counts["total"] = total_vehicles
                density = self.density_calc.calculate(total_vehicles)

            # Draw ROIs on frame
            self.roi_manager.draw_rois(frame, cv2)

            # FPS calculation
            frame_count += 1
            curr_time = time.perf_counter()
            if curr_time - prev_time >= 0.5:
                fps = frame_count / (curr_time - prev_time)
                frame_count = 0
                prev_time = curr_time

            # Annotate frame
            annotated_frame = self.detector.annotate_frame(
                frame, detections, counts, density, fps
            )

            # If demo mode is active, watermark prominent DEMO MODE badge
            if is_override:
                cv2.rectangle(annotated_frame, (w - 180, h - 45), (w - 10, h - 10), (0, 0, 220), -1)
                cv2.putText(
                    annotated_frame,
                    "DEMO MODE",
                    (w - 170, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

            # Encode frame to JPEG
            ret, buffer = cv2.imencode(".jpg", annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if ret:
                jpeg_bytes = buffer.tobytes()
            else:
                jpeg_bytes = None

            with self.lock:
                self.latest_jpeg = jpeg_bytes
                self.latest_result = {
                    "vehicle_count": sum(counts.values()) if "total" not in counts else counts["total"],
                    "counts": counts,
                    "density": density,
                    "ambulance_detected": ambulance_det,
                    "ambulance_confidence": round(ambulance_conf, 2),
                    "ambulance_direction": ambulance_dir,
                    "direction_counts": dir_counts,
                    "fps": round(fps, 1),
                    "inference_ms": round(self.detector.last_inference_ms, 1),
                    "demo_override": is_override,
                    "is_camera_connected": self.camera.get_status()["connected"],
                    "timestamp": time.time()
                }

            time.sleep(0.01)

    def _render_demo_overlay(self, frame: np.ndarray, demo_info: Dict[str, Any]) -> np.ndarray:
        h, w = frame.shape[:2]
        if demo_info.get("ambulance_detected"):
            # Draw synthetic ambulance vehicle near North approach
            nx, ny = w // 2 - 40, 100
            cv2.rectangle(frame, (nx, ny), (nx + 80, ny + 120), (255, 255, 255), -1)
            # Red cross
            cv2.rectangle(frame, (nx + 32, ny + 35), (nx + 48, ny + 85), (0, 0, 220), -1)
            cv2.rectangle(frame, (nx + 15, ny + 52), (nx + 65, ny + 68), (0, 0, 220), -1)
        return frame

    def get_latest_jpeg(self) -> Optional[bytes]:
        with self.lock:
            return self.latest_jpeg

    def get_latest_result(self) -> Dict[str, Any]:
        with self.lock:
            return dict(self.latest_result)
