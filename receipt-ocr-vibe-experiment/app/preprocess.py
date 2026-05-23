"""
preprocess.py
OpenCV preprocessing pipeline for receipt images.
Makes images more OCR-friendly before sending to Google Vision.
"""

import cv2
import numpy as np
from PIL import Image
import io


def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """Load image from bytes (from Streamlit uploader)."""
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return image


def load_image_from_path(path: str) -> np.ndarray:
    """Load image from file path."""
    return cv2.imread(path)


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert BGR image to grayscale."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def denoise(image: np.ndarray) -> np.ndarray:
    """
    Remove noise from grayscale image.
    h=10 is a good balance between noise removal and detail preservation.
    """
    return cv2.fastNlMeansDenoising(image, h=10)


def threshold(image: np.ndarray) -> np.ndarray:
    """
    Apply adaptive thresholding.
    Better than global threshold for receipts with uneven lighting.
    blockSize=15 and C=8 work well for most thermal/paper receipts.
    """
    return cv2.adaptiveThreshold(
        image,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY,
        blockSize=15,
        C=8
    )


def resize(image: np.ndarray, target_height: int = 1200) -> np.ndarray:
    """
    Resize image to target height while maintaining aspect ratio.
    1200px height gives Google Vision enough detail without overshooting quota.
    """
    h, w = image.shape[:2]
    if h >= target_height:
        return image

    scale = target_height / h
    new_w = int(w * scale)
    return cv2.resize(image, (new_w, target_height), interpolation=cv2.INTER_CUBIC)


def sharpen(image: np.ndarray) -> np.ndarray:
    """
    Sharpen image using unsharp masking.
    Helps OCR read blurry or low-res receipts.
    """
    gaussian = cv2.GaussianBlur(image, (0, 0), sigmaX=2)
    return cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)


def deskew(image: np.ndarray) -> np.ndarray:
    """
    Auto-correct slight rotation/skew using Hough line detection.
    Returns corrected image. Skips if angle is negligible.
    """
    coords = np.column_stack(np.where(image < 128))
    if coords.shape[0] == 0:
        return image

    angle = cv2.minAreaRect(coords.astype(np.float32))[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) < 0.5:
        return image

    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )
    return rotated


def preprocess(image_input, source: str = "bytes") -> tuple[np.ndarray, np.ndarray]:
    """
    Full preprocessing pipeline.

    Args:
        image_input: bytes (from Streamlit) or str (file path)
        source: "bytes" or "path"

    Returns:
        (original_image_bgr, processed_image_gray)
    """
    # Load
    if source == "bytes":
        original = load_image_from_bytes(image_input)
    else:
        original = load_image_from_path(image_input)

    if original is None:
        raise ValueError("Image could not be loaded. Check format or path.")

    # Pipeline
    gray = to_grayscale(original)
    resized = resize(gray, target_height=1400)
    denoised = denoise(resized)
    sharpened = sharpen(denoised)
    deskewed = deskew(sharpened)
    thresholded = threshold(deskewed)

    return original, thresholded


def to_pil(cv_image: np.ndarray) -> Image.Image:
    """Convert OpenCV image to PIL Image (for Streamlit display)."""
    if len(cv_image.shape) == 2:
        return Image.fromarray(cv_image)
    return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))


def to_bytes(cv_image: np.ndarray, ext: str = ".jpg") -> bytes:
    """Convert OpenCV image to bytes (to send to Vision API)."""
    _, buffer = cv2.imencode(ext, cv_image)
    return buffer.tobytes()
