import time
import threading
import math
import cv2
import numpy as np
from typing import Optional, Tuple

class VideoCamera:
    """Threaded Video Camera capture with automatic synthetic video fallback."""

    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        self.camera_index = camera_index
        self.width = width
        self.height = height

        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.is_synthetic = False
        self.lock = threading.Lock()
        self.latest_frame: Optional[np.ndarray] = None
        self.thread: Optional[threading.Thread] = None
        self.sim_tick = 0

        self._initialize_camera()

    def _initialize_camera(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            # Short test read
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                    self.is_synthetic = False
                    self.latest_frame = cv2.resize(frame, (self.width, self.height))
                    return
        except Exception:
            pass

        # If camera could not be opened, use synthetic simulation
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

        self.is_synthetic = True
        self.latest_frame = self._generate_synthetic_frame()

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
            self.cap = None

    def _capture_loop(self):
        while self.is_running:
            if not self.is_synthetic and self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    if frame.shape[1] != self.width or frame.shape[0] != self.height:
                        frame = cv2.resize(frame, (self.width, self.height))
                    with self.lock:
                        self.latest_frame = frame
                else:
                    # Switch to synthetic if camera drops
                    self.is_synthetic = True
                time.sleep(0.02)
            else:
                frame = self._generate_synthetic_frame()
                with self.lock:
                    self.latest_frame = frame
                time.sleep(0.04)

    def _generate_synthetic_frame(self) -> np.ndarray:
        """Generates a clean simulated traffic video frame when webcam is absent."""
        self.sim_tick += 1
        frame = np.full((self.height, self.width, 3), (35, 35, 40), dtype=np.uint8)

        # Draw intersection road layout
        road_color = (60, 60, 65)
        line_color = (200, 200, 200)

        # Vertical road (North-South)
        cv2.rectangle(frame, (self.width // 2 - 80, 0), (self.width // 2 + 80, self.height), road_color, -1)
        # Horizontal road (East-West)
        cv2.rectangle(frame, (0, self.height // 2 - 80), (self.width, self.height // 2 + 80), road_color, -1)

        # Center intersection lines
        for y in range(0, self.height, 40):
            if y < self.height // 2 - 80 or y > self.height // 2 + 80:
                cv2.line(frame, (self.width // 2, y), (self.width // 2, y + 20), line_color, 2)
        for x in range(0, self.width, 40):
            if x < self.width // 2 - 80 or x > self.width // 2 + 80:
                cv2.line(frame, (x, self.height // 2), (x + 20, self.height // 2), line_color, 2)

        # Animate simulated moving cars
        # Car 1 (Southbound)
        c1_y = int((self.sim_tick * 4) % (self.height + 60)) - 30
        cv2.rectangle(frame, (self.width // 2 - 50, c1_y - 20), (self.width // 2 - 20, c1_y + 20), (220, 100, 50), -1)

        # Car 2 (Northbound)
        c2_y = self.height - int(((self.sim_tick * 3) + 120) % (self.height + 60)) + 30
        cv2.rectangle(frame, (self.width // 2 + 20, c2_y - 20), (self.width // 2 + 50, c2_y + 20), (50, 180, 220), -1)

        # Car 3 (Eastbound)
        c3_x = int((self.sim_tick * 3.5) % (self.width + 80)) - 40
        cv2.rectangle(frame, (c3_x - 25, self.height // 2 + 20), (c3_x + 25, self.height // 2 + 50), (100, 220, 100), -1)

        # Simulated watermarking
        cv2.putText(
            frame,
            "[VIRTUAL WEBCAM - SIMULATION STREAM]",
            (20, self.height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 220, 255),
            1,
            cv2.LINE_AA
        )
        return frame

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        with self.lock:
            if self.latest_frame is not None:
                return True, self.latest_frame.copy()
            return False, None

    def get_status(self) -> dict:
        return {
            "connected": not self.is_synthetic,
            "synthetic_mode": self.is_synthetic,
            "camera_index": self.camera_index,
            "width": self.width,
            "height": self.height
        }
