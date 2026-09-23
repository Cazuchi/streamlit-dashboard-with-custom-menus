import streamlit as st
import pandas as pd

def render_page():
    st.header("Step 1: Upload Data")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=["xlsx"])

    if uploaded_file is not None:
        # Load and store in session_state
        st.session_state.df_ba = pd.read_excel(uploaded_file)
        st.success("Data uploaded.")
        st.session_state.step = 8
        st.rerun()