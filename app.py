{\rtf1\ansi\ansicpg1252\cocoartf2907
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import sys\
import os\
import io\
import tempfile\
\
import streamlit as st\
from PIL import Image\
\
from depth_engine_small import generate_depth_map\
from stl_generator import depth_to_bas_relief, depth_to_lithophane, generate_label_plate_stl\
from braille_engine import get_monument_info, text_to_braille_unicode\
from qr_generator import generate_qr_code\
\
st.set_page_config(page_title="Feel the Monument", layout="wide")\
\
st.title("Feel the Monument")\
st.caption("Tactile 3D models for visually impaired students")\
\
col1, col2 = st.columns([1, 2])\
\
with col1:\
    uploaded = st.file_uploader(\
        "Upload a monument or artwork image",\
        type=["jpg", "jpeg", "png", "webp", "bmp"]\
    )\
\
    monument_options = ["Taj Mahal", "Qutub Minar", "Red Fort", "Starry Night", "Custom"]\
    monument = st.selectbox("Monument / Artwork name", monument_options)\
\
    if monument == "Custom":\
        monument = st.text_input("Enter custom name")\
\
    st.markdown("#### STL Settings")\
    width_mm  = st.slider("Plate width (mm)",    50,  200, 100)\
    relief_mm = st.slider("Relief height (mm)",   2,   20,   8)\
    base_mm   = st.slider("Base thickness (mm)",  1,   10,   3)\
    smooth    = st.slider("Smoothing",            0,   10,   3) * 0.5\
\
    url = st.text_input(\
        "Audio / video URL (optional)",\
        placeholder="https://drive.google.com/file/d/yourfileid/view"\
    )\
\
    generate = st.button("Generate STL", type="primary", disabled=not uploaded or not monument)\
\
with col2:\
    if uploaded:\
        st.image(uploaded, use_column_width=True)\
\
    if generate and uploaded and monument:\
        with st.spinner("Running depth AI model..."):\
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:\
                tmp.write(uploaded.read())\
                tmp_path = tmp.name\
            depth = generate_depth_map(tmp_path)\
            os.unlink(tmp_path)\
\
        with st.spinner("Generating STL files..."):\
            out_dir = tempfile.mkdtemp()\
            name_safe = monument.replace(" ", "_")\
\
            bas_path = os.path.join(out_dir, name_safe + "_bas_relief.stl")\
            depth_to_bas_relief(depth, bas_path,\
                base_mm=base_mm, relief_mm=relief_mm,\
                width_mm=width_mm, smooth=smooth)\
\
            lit_path = os.path.join(out_dir, name_safe + "_lithophane.stl")\
            depth_to_lithophane(depth, lit_path, width_mm=width_mm)\
\
            plate_path = None\
            if url and url.startswith("http"):\
                plate_path = os.path.join(out_dir, name_safe + "_label_plate.stl")\
                generate_label_plate_stl(monument, url, plate_path)\
\
        st.success("Done! Download your files below.")\
\
        info = get_monument_info(monument)\
        braille = text_to_braille_unicode(info["short"])\
        st.markdown("**Braille preview:**")\
        st.text(braille)\
\
        col_a, col_b, col_c = st.columns(3)\
\
        with open(bas_path, "rb") as f:\
            col_a.download_button(\
                "Download Bas-Relief STL",\
                f, file_name=name_safe + "_bas_relief.stl"\
            )\
\
        with open(lit_path, "rb") as f:\
            col_b.download_button(\
                "Download Lithophane STL",\
                f, file_name=name_safe + "_lithophane.stl"\
            )\
\
        if plate_path:\
            with open(plate_path, "rb") as f:\
                col_c.download_button(\
                    "Download Label Plate STL",\
                    f, file_name=name_safe + "_label_plate.stl"\
                )\
\
            qr_path, _ = generate_qr_code(url, out_dir, monument)\
            if qr_path:\
                st.image(qr_path, caption="QR code linking to your audio", width=200)}