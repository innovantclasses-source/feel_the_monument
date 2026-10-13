{\rtf1\ansi\ansicpg1252\cocoartf2907
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import torch\
import cv2\
import numpy as np\
\
\
def generate_depth_map(image_path):\
    torch.hub._validate_not_a_forked_repo = lambda a, b, c: True\
\
    model = torch.hub.load('intel-isl/MiDaS', 'MiDaS_small', trust_repo=True)\
    device = torch.device('cpu')\
    model.to(device).eval()\
\
    transforms = torch.hub.load('intel-isl/MiDaS', 'transforms', trust_repo=True)\
    transform = transforms.small_transform\
\
    img = cv2.imread(image_path)\
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)\
\
    input_batch = transform(img_rgb).to(device)\
    with torch.no_grad():\
        prediction = model(input_batch)\
        prediction = torch.nn.functional.interpolate(\
            prediction.unsqueeze(1),\
            size=img_rgb.shape[:2],\
            mode='bicubic',\
            align_corners=False,\
        ).squeeze()\
\
    depth = prediction.cpu().numpy()\
    depth = (depth - depth.min()) / (depth.max() - depth.min())\
    return depth.astype('float32')}