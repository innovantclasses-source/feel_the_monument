import cv2
import numpy as np

def generate_depth_map(image_path):
    img = cv2.imread(image_path)

    # Force resize to small dimensions regardless of input size
    img = cv2.resize(img, (200, 150))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
    laplacian = np.abs(laplacian)
    luminance = gray.astype(np.float64)
    depth = 0.6 * luminance + 0.4 * laplacian
    depth = cv2.GaussianBlur(depth.astype(np.float32), (9, 9), 0)
    depth = (depth - depth.min()) / (depth.max() - depth.min())
    return depth.astype('float32')
