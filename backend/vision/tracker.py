import math
from typing import List, Dict, Tuple, Any

class SimpleCentroidTracker:
    """Lightweight centroid tracker to maintain stable vehicle identities across frames."""

    def __init__(self, max_disappeared: int = 15, max_distance: float = 60.0):
        self.next_object_id = 0
        self.objects: Dict[int, Tuple[float, float]] = {}  # id -> (cx, cy)
        self.classes: Dict[int, str] = {}                  # id -> label
        self.disappeared: Dict[int, int] = {}              # id -> lost frames count
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def register(self, centroid: Tuple[float, float], label: str) -> int:
        obj_id = self.next_object_id
        self.objects[obj_id] = centroid
        self.classes[obj_id] = label
        self.disappeared[obj_id] = 0
        self.next_object_id += 1
        return obj_id

    def deregister(self, obj_id: int):
        if obj_id in self.objects:
            del self.objects[obj_id]
        if obj_id in self.classes:
            del self.classes[obj_id]
        if obj_id in self.disappeared:
            del self.disappeared[obj_id]

    def update(self, detections: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        """
        detections: list of dicts with 'bbox': (x1, y1, x2, y2), 'class': str, 'conf': float
        Returns dict of obj_id -> detection dict with 'track_id'
        """
        if len(detections) == 0:
            for obj_id in list(self.disappeared.keys()):
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] > self.max_disappeared:
                    self.deregister(obj_id)
            return {}

        input_centroids = []
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            input_centroids.append(((x1 + x2) / 2.0, (y1 + y2) / 2.0))

        if len(self.objects) == 0:
            tracked = {}
            for i, det in enumerate(detections):
                obj_id = self.register(input_centroids[i], det["class"])
                det["track_id"] = obj_id
                tracked[obj_id] = det
            return tracked

        # Match existing objects to new centroids using Euclidean distance
        object_ids = list(self.objects.keys())
        object_centroids = list(self.objects.values())

        # Distances matrix
        distances = []
        for oc in object_centroids:
            row = []
            for ic in input_centroids:
                d = math.hypot(oc[0] - ic[0], oc[1] - ic[1])
                row.append(d)
            distances.append(row)

        used_rows = set()
        used_cols = set()
        tracked = {}

        # Greedy match smallest distance
        import numpy as np
        dist_arr = np.array(distances)
        rows = dist_arr.min(axis=1).argsort()
        cols = dist_arr.argmin(axis=1)[rows]

        for r, c in zip(rows, cols):
            if r in used_rows or c in used_cols:
                continue
            if dist_arr[r][c] > self.max_distance:
                continue

            obj_id = object_ids[r]
            self.objects[obj_id] = input_centroids[c]
            self.disappeared[obj_id] = 0
            det = detections[c]
            det["track_id"] = obj_id
            tracked[obj_id] = det

            used_rows.add(r)
            used_cols.add(c)

        # Unmatched existing objects
        unused_rows = set(range(len(object_ids))) - used_rows
        for r in unused_rows:
            obj_id = object_ids[r]
            self.disappeared[obj_id] += 1
            if self.disappeared[obj_id] > self.max_disappeared:
                self.deregister(obj_id)

        # Unmatched new detections
        unused_cols = set(range(len(input_centroids))) - used_cols
        for c in unused_cols:
            det = detections[c]
            obj_id = self.register(input_centroids[c], det["class"])
            det["track_id"] = obj_id
            tracked[obj_id] = det

        return tracked
