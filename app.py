import streamlit as st
from depth_engine_small import generate_depth_map
from stl_generator import depth_to_bas_relief, depth_to_lithophane, generate_label_plate_stl
from braille_engine import get_monument_info, text_to_braille_unicode
from qr_generator import generate_qr_code
st.write("local imports ok")
