import streamlit as st

st.set_page_config(page_title="Feel the Monument", layout="wide")
st.title("Feel the Monument")

col1, col2 = st.columns([1, 2])

with col1:
    st.write("left column works")

with col2:
    st.write("right column works")
