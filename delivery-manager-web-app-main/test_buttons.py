import streamlit as st

st.title("Button Test Page")

st.write("Testing buttons...")

if st.button("Test Button 1"):
    st.write("Button 1 clicked!")

if st.button("Test Button 2", type="primary"):
    st.write("Button 2 clicked!")

if st.button("Test Button 3", use_container_width=True):
    st.write("Button 3 clicked!")

st.write("End of test")
