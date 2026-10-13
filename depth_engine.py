import torch
import cv2
import numpy as np


def generate_depth_map(image_path):
    torch.hub._validate_not_a_forked_repo = lambda a, b, c: True

    model = torch.hub.load('intel-isl/MiDaS', 'DPT_Large', trust_repo=True)
    device = torch.device('cpu')
    model.to(device).eval()

    transforms = torch.hub.load('intel-isl/MiDaS', 'transforms', trust_repo=True)
    transform = transforms.dpt_transform

    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    input_batch = transform(img_rgb).to(device)
    with torch.no_grad():
        prediction = model(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img_rgb.shape[:2],
            mode='bicubic',
            align_corners=False,
        ).squeeze()

    depth = prediction.cpu().numpy()
    depth = (depth - depth.min()) / (depth.max() - depth.min())
    return depth.astype('float32')
