import cv2
import numpy as np
from PIL import Image


def generate_depth_map(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (21, 21), 0)

    # Use Laplacian for edge-aware depth approximation
    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
    laplacian = np.abs(laplacian)

    # Combine with luminance-based depth cue
    # Brighter areas are typically foreground in monument photos
    luminance = gray.astype(np.float64)

    # Weighted combination
    depth = 0.6 * luminance + 0.4 * laplacian

    # Smooth the result
    depth = cv2.GaussianBlur(depth.astype(np.float32), (15, 15), 0)

    # Normalise to 0-1
    depth = (depth - depth.min()) / (depth.max() - depth.min())
    return depth.astype('float32')
