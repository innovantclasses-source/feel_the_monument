import cv2
import numpy as np

MAX_DIM = 150  # keeps memory under 500MB on free tier

def generate_depth_map(image_path):
    img = cv2.imread(image_path)

    # Resize to small dimensions before any processing
    h, w = img.shape[:2]
    if max(h, w) > MAX_DIM:
        scale = MAX_DIM / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
    laplacian = np.abs(laplacian)
    luminance = gray.astype(np.float64)
    depth = 0.6 * luminance + 0.4 * laplacian
    depth = cv2.GaussianBlur(depth.astype(np.float32), (9, 9), 0)
    depth = (depth - depth.min()) / (depth.max() - depth.min())
    return depth.astype('float32')
