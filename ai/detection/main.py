# ai/detection/main.py
import cv2
import asyncio
import logging
from typing import Optional, Callable, Dict, Any
import numpy as np
from .yolov11_model import YOLODetector
from .tracker import SimpleTracker
from .preprocess import Preprocessor
import time

logger = logging.getLogger(__name__)

class DetectionEngine:
    """Orchestrates real-time vehicle detection and tracking from video."""

    def __init__(
        self,
        model_path: str = "yolo11n.pt",
        device: str = "cpu",
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        max_lost: int = 30,
        fps: int = 15,
    ):
        self.detector = YOLODetector(
            model_path=model_path,
            device=device,
            conf_threshold=conf_threshold,
            iou_threshold=iou_threshold,
        )
        self.tracker = SimpleTracker(max_lost=max_lost)
        self.fps = fps
        self.frame_delay = 1.0 / fps
        self.is_running = False

    async def process_video(
        self,
        video_source: str,
        on_detection: Optional[Callable[[list], None]] = None,
        on_track: Optional[Callable[[list], None]] = None,
    ):
        """
        Process video from source (file, webcam, or RTSP).
        Calls callbacks with detections and tracked objects.
        """
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            logger.error(f"Cannot open video source: {video_source}")
            return

        self.is_running = True
        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                logger.warning("End of video or frame read error.")
                break

            # Preprocess
            # Resize to 640x640
            padded, scale, (pad_w, pad_h) = Preprocessor.resize_and_pad(frame, (640, 640))

            # Detect
            detections, tracked = self.detector.detect_and_track(padded, self.tracker)

            # Convert bboxes back to original frame coordinates
            for det in detections:
                x1, y1, x2, y2 = det["bbox"]
                # Remove padding and scale
                x1 = int((x1 - pad_w) / scale)
                y1 = int((y1 - pad_h) / scale)
                x2 = int((x2 - pad_w) / scale)
                y2 = int((y2 - pad_h) / scale)
                det["bbox"] = [x1, y1, x2, y2]

            for trk in tracked:
                x1, y1, x2, y2, track_id = trk["bbox"]  # but we need to handle differently
                # Our tracker returns [x1,y1,x2,y2,track_id] per track
                # Convert to dict with bbox
                trk["bbox"] = [
                    int((x1 - pad_w) / scale),
                    int((y1 - pad_h) / scale),
                    int((x2 - pad_w) / scale),
                    int((y2 - pad_h) / scale),
                ]
                trk["track_id"] = track_id

            # Callbacks
            if on_detection:
                await on_detection(detections)
            if on_track:
                await on_track(tracked)

            # Control frame rate
            await asyncio.sleep(self.frame_delay)

        cap.release()
        self.is_running = False
        logger.info("Video processing stopped.")

    async def process_video_stream(
        self,
        video_source: str,
        callback: Callable[[list, list], None],
    ):
        """Process video and call callback with (detections, tracked)."""
        await self.process_video(
            video_source,
            on_detection=lambda d: callback(d, None),
            on_track=lambda t: callback(None, t),
        )

    def stop(self):
        self.is_running = False