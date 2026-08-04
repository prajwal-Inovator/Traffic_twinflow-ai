# ai/detection/tracker.py
import numpy as np
from scipy.optimize import linear_sum_assignment
from collections import defaultdict
import time

class SimpleTracker:
    """Simple centroid-based tracker with IoU matching."""

    def __init__(self, max_lost: int = 30, iou_threshold: float = 0.3):
        self.max_lost = max_lost
        self.iou_threshold = iou_threshold
        self.next_id = 0
        self.tracks = {}  # track_id -> {bbox, last_seen, age, class_id}
        self.lost = set()

    def update(self, detections: np.ndarray, frame: np.ndarray) -> np.ndarray:
        """
        Update tracker with new detections.
        detections: array of [x1, y1, x2, y2, conf, class_id]
        Returns: array of tracked objects [x1, y1, x2, y2, track_id]
        """
        if len(detections) == 0:
            # No detections, increment ages and remove lost tracks
            self._increment_ages()
            self._remove_lost()
            return np.empty((0, 5))

        # Compute centroids of existing tracks
        track_ids = list(self.tracks.keys())
        if track_ids:
            track_boxes = np.array([self.tracks[tid]["bbox"] for tid in track_ids])
            track_centroids = (track_boxes[:, :2] + track_boxes[:, 2:]) / 2
        else:
            track_centroids = np.empty((0, 2))

        # Compute centroids of detections
        det_centroids = (detections[:, :2] + detections[:, 2:4]) / 2

        # Compute cost matrix (IoU or distance)
        if len(track_ids) > 0 and len(detections) > 0:
            # Use IoU as cost
            cost_matrix = 1 - self._iou(track_boxes, detections[:, :4])
        else:
            cost_matrix = np.zeros((len(track_ids), len(detections)))

        # Hungarian assignment
        row_ind, col_ind = linear_sum_assignment(cost_matrix) if cost_matrix.size > 0 else ([], [])

        # Matched tracks
        matched_tracks = []
        for r, c in zip(row_ind, col_ind):
            if cost_matrix[r, c] < 1 - self.iou_threshold:
                matched_tracks.append((track_ids[r], c, detections[c]))

        # Update matched tracks
        for track_id, det_idx, det in matched_tracks:
            self.tracks[track_id]["bbox"] = det[:4].tolist()
            self.tracks[track_id]["last_seen"] = time.time()
            self.tracks[track_id]["age"] = 0
            self.tracks[track_id]["class_id"] = int(det[5])
            self.lost.discard(track_id)

        # Unmatched detections -> new tracks
        unmatched_det = [c for c in range(len(detections)) if c not in col_ind]
        for det_idx in unmatched_det:
            new_id = self.next_id
            self.next_id += 1
            self.tracks[new_id] = {
                "bbox": detections[det_idx][:4].tolist(),
                "last_seen": time.time(),
                "age": 0,
                "class_id": int(detections[det_idx][5]),
            }

        # Unmatched tracks -> lost
        unmatched_tracks = [tid for tid in track_ids if tid not in [t[0] for t in matched_tracks]]
        for tid in unmatched_tracks:
            self.tracks[tid]["age"] += 1
            if self.tracks[tid]["age"] > self.max_lost:
                self.lost.add(tid)

        # Remove lost tracks
        for tid in list(self.lost):
            del self.tracks[tid]
        self.lost.clear()

        # Return tracked objects
        tracked = []
        for tid, data in self.tracks.items():
            bbox = data["bbox"]
            tracked.append([bbox[0], bbox[1], bbox[2], bbox[3], tid])
        return np.array(tracked)

    def _iou(self, boxes1: np.ndarray, boxes2: np.ndarray) -> np.ndarray:
        """Compute IoU between two sets of boxes."""
        # boxes: [x1, y1, x2, y2]
        # Expand dimensions
        boxes1 = boxes1[:, None, :]
        boxes2 = boxes2[None, :, :]
        x1 = np.maximum(boxes1[..., 0], boxes2[..., 0])
        y1 = np.maximum(boxes1[..., 1], boxes2[..., 1])
        x2 = np.minimum(boxes1[..., 2], boxes2[..., 2])
        y2 = np.minimum(boxes1[..., 3], boxes2[..., 3])
        inter = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
        area1 = (boxes1[..., 2] - boxes1[..., 0]) * (boxes1[..., 3] - boxes1[..., 1])
        area2 = (boxes2[..., 2] - boxes2[..., 0]) * (boxes2[..., 3] - boxes2[..., 1])
        union = area1 + area2 - inter
        return inter / (union + 1e-6)

    def _increment_ages(self):
        for tid in self.tracks:
            self.tracks[tid]["age"] += 1
            if self.tracks[tid]["age"] > self.max_lost:
                self.lost.add(tid)

    def _remove_lost(self):
        for tid in list(self.lost):
            if tid in self.tracks:
                del self.tracks[tid]
        self.lost.clear()