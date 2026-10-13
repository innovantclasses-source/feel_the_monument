import os
import tempfile
import streamlit as st

st.set_page_config(page_title="Feel the Monument", layout="wide")
st.title("Feel the Monument")
st.caption("Tactile 3D models for visually impaired students")

col1, col2 = st.columns([1, 2])

with col1:
    uploaded = st.file_uploader(
        "Upload a monument or artwork image",
        type=["jpg", "jpeg", "png", "webp", "bmp"]
    )
    monument_options = ["Taj Mahal", "Qutub Minar", "Red Fort", "Starry Night", "Custom"]
    monument = st.selectbox("Monument / Artwork name", monument_options)
    if monument == "Custom":
        monument = st.text_input("Enter custom name")
    st.markdown("#### STL Settings")
    width_mm  = st.slider("Plate width (mm)",    50, 200, 100)
    relief_mm = st.slider("Relief height (mm)",   2,  20,   8)
    base_mm   = st.slider("Base thickness (mm)",  1,  10,   3)
    smooth    = st.slider("Smoothing",            0,  10,   3) * 0.5
    url = st.text_input("Audio / video URL (optional)")
    generate = st.button("Generate STL", type="primary")

with col2:
    if uploaded:
        st.image(uploaded)
    else:
        st.info("Upload an image to get started")

    if generate and uploaded and monument:
        from depth_engine_small import generate_depth_map
        st.write("step 1: depth engine imported")

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name
            st.write("step 2: file written")

            depth = generate_depth_map(tmp_path)
            os.unlink(tmp_path)
            st.write(f"step 3: depth map generated, shape: {depth.shape}")

        except Exception as e:
            st.error(f"Error: {str(e)}")
