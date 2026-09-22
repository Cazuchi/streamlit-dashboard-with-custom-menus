import streamlit as st

def render_page():
    st.write("### Choose Filter Mode")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Filter by Municipality", use_container_width=True):
            st.session_state.filter_type = "municipality"
            st.session_state.step = 2
            st.rerun()
            
    with col2:
        if st.button("Filter by Destination", use_container_width=True):
            st.session_state.filter_type = "destination"
            st.session_state.step = 2
            st.rerun()

    with col3:
        if st.button("Filter by Region", use_container_width=True):
            st.session_state.filter_type = "region"
            st.session_state.step = 2
            st.rerun()