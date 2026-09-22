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

    col1, col2, col3 = st.columns([1, 1, 1])

    STORBY_OPTIONS = {
    'Landsdel Byen København' : '01',
    'Landsdel Københavns omegn' : '02',
    'Odense' : '461',
    'Aarhus' : '751',
    'Aalborg' : '851'
    }

    with col1:
        if st.button("Filter by storby", use_container_width=True):
            st.session_state.filter_type = "storby"
            st.session_state.selected_diskretioneret_option = "excl"
            active_dict = STORBY_OPTIONS
            options = sorted(active_dict.keys())
            selected_names = []
            for option in options:
                selected_names.append(option)
            st.session_state.selected_names = selected_names
            st.session_state.selected_codes = [active_dict[name] for name in selected_names]
            st.session_state.step = 3
            st.rerun()