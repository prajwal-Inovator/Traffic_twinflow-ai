# ai/detection/preprocess.py
import cv2
import numpy as np
from typing import Tuple, Optional

class Preprocessor:
    """Image preprocessing for YOLO detection."""

    @staticmethod
    def resize_and_pad(
        image: np.ndarray,
        target_size: Tuple[int, int] = (640, 640)
    ) -> Tuple[np.ndarray, float, Tuple[int, int]]:
        """
        Resize and pad image to target size while maintaining aspect ratio.
        Returns: padded image, scale factor, (pad_w, pad_h)
        """
        h, w = image.shape[:2]
        target_w, target_h = target_size
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(image, (new_w, new_h))
        pad_w = (target_w - new_w) // 2
        pad_h = (target_h - new_h) // 2
        padded = np.ones((target_h, target_w, 3), dtype=np.uint8) * 114
        padded[pad_h:pad_h+new_h, pad_w:pad_w+new_w] = resized
        return padded, scale, (pad_w, pad_h)

    @staticmethod
    def normalize(image: np.ndarray) -> np.ndarray:
        """Normalize image to [0,1]."""
        return image.astype(np.float32) / 255.0