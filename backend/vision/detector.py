import os
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
import cv2
import numpy as np

class VehicleDetector:
    """YOLO-based Vehicle and Emergency Vehicle Detector with auto-device acceleration."""

    COCO_TARGET_CLASSES = {
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck"
    }

    CLASS_COLORS = {
        "car": (255, 144, 30),        # Dodger blue-ish (BGR)
        "motorcycle": (0, 215, 255),  # Gold
        "bus": (255, 0, 128),         # Purple
        "truck": (0, 165, 255),       # Orange
        "ambulance": (0, 0, 255),     # Bright Red
    }

    def __init__(self, model_name: str = "yolov8n.pt", conf_threshold: float = 0.45):
        self.conf_threshold = conf_threshold
        self.model_name = model_name
        self.model = None
        self.device = "cpu"
        self.is_ready = False
        self.last_inference_ms = 0.0

        self._load_model()

    def _load_model(self):
        try:
            import torch
            if torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"
        except Exception:
            self.device = "cpu"

        try:
            from ultralytics import YOLO
            # Check local models dir first
            local_path = Path("models/yolo") / self.model_name
            if local_path.exists():
                self.model = YOLO(str(local_path))
            else:
                # Ultralytics will download yolov8n.pt automatically
                self.model = YOLO(self.model_name)
            self.is_ready = True
        except Exception as e:
            print(f"[VehicleDetector] YOLO initialization warning: {e}. Running fallback detector.")
            self.model = None
            self.is_ready = False

    def detect(self, frame: np.ndarray) -> Tuple[List[Dict[str, Any]], float]:
        """
        Runs YOLO detection on frame.
        Returns (list_of_detections, inference_time_ms).
        """
        start_t = time.perf_counter()
        detections: List[Dict[str, Any]] = []

        if not self.is_ready or self.model is None:
            # Fallback basic color/contour detection if YOLO is not loaded
            detections = self._fallback_detection(frame)
            inf_time = (time.perf_counter() - start_t) * 1000.0
            self.last_inference_ms = inf_time
            return detections, inf_time

        try:
            results = self.model(
                frame,
                conf=self.conf_threshold,
                device=self.device,
                verbose=False
            )
            for r in results:
                boxes = r.boxes
                if boxes is None:
                    continue
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())

                    if cls_id in self.COCO_TARGET_CLASSES:
                        class_name = self.COCO_TARGET_CLASSES[cls_id]
                        xyxy = box.xyxy[0].cpu().numpy().astype(int)
                        x1, y1, x2, y2 = xyxy.tolist()

                        # Check ambulance heuristic:
                        # Inspect region for prominent red/white emergency pattern
                        is_ambulance = self._check_ambulance_heuristic(frame, x1, y1, x2, y2, class_name)
                        if is_ambulance:
                            class_name = "ambulance"

                        detections.append({
                            "bbox": (x1, y1, x2, y2),
                            "class": class_name,
                            "confidence": round(conf, 2),
                            "is_emergency": (class_name == "ambulance")
                        })
        except Exception as e:
            print(f"[VehicleDetector] Error during YOLO inference: {e}")

        inf_time = (time.perf_counter() - start_t) * 1000.0
        self.last_inference_ms = inf_time
        return detections, inf_time

    def _check_ambulance_heuristic(self, frame: np.ndarray, x1: int, y1: int, x2: int, y2: int, class_name: str) -> bool:
        """
        Heuristic: For cars, vans, or trucks, check if vehicle has an emergency color scheme
        (predominantly white body with saturated red cross / red stripes).
        """
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        if x2 - x1 < 30 or y2 - y1 < 30:
            return False

        roi = frame[y1:y2, x1:x2]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Red mask in HSV (two ranges)
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])

        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_ratio = (cv2.countNonZero(mask_red1 | mask_red2)) / float((x2 - x1) * (y2 - y1))

        # White mask in HSV
        lower_white = np.array([0, 0, 180])
        upper_white = np.array([180, 50, 255])
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        white_ratio = cv2.countNonZero(mask_white) / float((x2 - x1) * (y2 - y1))

        # Ambulance indicator: substantial white base with significant red markings
        if white_ratio > 0.25 and red_ratio > 0.08:
            return True

        return False

    def _fallback_detection(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Contour-based fallback detector when YOLO weights are downloading or offline."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for c in contours:
            area = cv2.contourArea(c)
            if 1500 < area < 40000:
                x, y, w, h = cv2.boundingRect(c)
                detections.append({
                    "bbox": (x, y, x + w, y + h),
                    "class": "car",
                    "confidence": 0.65,
                    "is_emergency": False
                })
        return detections[:8]

    def annotate_frame(
        self,
        frame: np.ndarray,
        detections: List[Dict[str, Any]],
        counts: Dict[str, int],
        density: str,
        fps: float
    ) -> np.ndarray:
        """Draws bounding boxes, labels, HUD, counts, and density badge."""
        annotated = frame.copy()
        h, w = annotated.shape[:2]

        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            label = det["class"]
            conf = det.get("confidence", 0.0)
            track_id = det.get("track_id", "")
            direction = det.get("direction", "")

            color = self.CLASS_COLORS.get(label, (0, 255, 0))
            if det.get("is_emergency"):
                color = (0, 0, 255)  # Flash red for emergency
                # Draw glowing border
                cv2.rectangle(annotated, (x1 - 3, y1 - 3), (x2 + 3, y2 + 3), (0, 255, 255), 2)

            # Draw main bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Draw tag background
            id_txt = f"#{track_id} " if track_id != "" else ""
            dir_txt = f"[{direction}] " if direction else ""
            display_text = f"{dir_txt}{id_txt}{label.upper()} {conf:.2f}"
            
            (tw, th), baseline = cv2.getTextSize(
                display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1
            )
            cv2.rectangle(
                annotated,
                (x1, max(0, y1 - th - 8)),
                (x1 + tw + 6, max(th + 8, y1)),
                color,
                -1
            )
            cv2.putText(
                annotated,
                display_text,
                (x1 + 3, max(th + 2, y1 - 4)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )

        # HUD Overlay Banner at the top
        overlay = annotated.copy()
        cv2.rectangle(overlay, (0, 0), (w, 55), (20, 20, 25), -1)
        cv2.addWeighted(overlay, 0.82, annotated, 0.18, 0, annotated)

        # HUD Texts
        total_vehicles = counts.get("total", len(detections))
        hud_text = f"TOTAL: {total_vehicles} | C:{counts.get('car', 0)} M:{counts.get('motorcycle', 0)} B:{counts.get('bus', 0)} T:{counts.get('truck', 0)} AMB:{counts.get('ambulance', 0)}"
        cv2.putText(annotated, hud_text, (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (240, 240, 240), 1, cv2.LINE_AA)

        # Density Badge
        density_colors = {"LOW": (0, 220, 0), "MEDIUM": (0, 215, 255), "HIGH": (0, 0, 255)}
        d_color = density_colors.get(density, (200, 200, 200))
        cv2.putText(annotated, f"DENSITY: {density}", (15, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.52, d_color, 2, cv2.LINE_AA)

        # FPS & Inference Time
        perf_text = f"FPS: {fps:.1f} | {self.last_inference_ms:.1f}ms [{self.device.upper()}]"
        cv2.putText(annotated, perf_text, (w - 230, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 240, 180), 1, cv2.LINE_AA)

        return annotated
