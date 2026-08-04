# ai/detection/yolov11_model.py
import torch
from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from .preprocess import Preprocessor

logger = logging.getLogger(__name__)

class YOLODetector:
    """YOLOv11 wrapper for vehicle detection."""

    def __init__(
        self,
        model_path: str = "yolo11n.pt",
        device: str = "cpu",
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        classes: Optional[List[int]] = None,  # COCO classes: car=2, bus=5, truck=7, motorcycle=3
    ):
        self.model = YOLO(model_path)
        self.device = device
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        # Default vehicle classes (COCO)
        if classes is None:
            self.classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        else:
            self.classes = classes
        self.model.to(device)
        logger.info(f"YOLO model loaded on {device}")

    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run detection on a single image.
        Returns list of detections with keys:
            'bbox': [x1, y1, x2, y2] in original image coordinates
            'class_id': int
            'confidence': float
            'class_name': str
        """
        # Run inference
        results = self.model(
            image,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            classes=self.classes,
            verbose=False,
        )

        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None or len(boxes) == 0:
                continue
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                cls_name = self.model.names[cls_id]
                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "class_id": cls_id,
                    "confidence": conf,
                    "class_name": cls_name,
                })
        return detections

    def detect_and_track(
        self,
        image: np.ndarray,
        tracker: Optional[object] = None
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Detect and optionally track.
        Returns (detections, tracked_objects).
        """
        detections = self.detect(image)
        tracked = []
        if tracker:
            # Convert detections to format expected by tracker
            # Format: [x1, y1, x2, y2, confidence, class_id]
            dets = np.array([
                [d["bbox"][0], d["bbox"][1], d["bbox"][2], d["bbox"][3],
                 d["confidence"], d["class_id"]]
                for d in detections
            ]) if detections else np.empty((0, 6))
            # Update tracker
            tracked_boxes = tracker.update(dets, image)
            # Convert to list of dicts
            for track in tracked_boxes:
                x1, y1, x2, y2, track_id = track[:5]  # depending on tracker
                tracked.append({
                    "track_id": int(track_id),
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                })
        return detections, tracked