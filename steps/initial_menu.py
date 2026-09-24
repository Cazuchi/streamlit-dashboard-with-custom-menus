import streamlit as st

def render_page():
    st.write("## Vælg hvilken data du ønsker at set")
    st.divider()
    st.write("##### Samlede, danske og internationale overnatninger vs. forrige periode:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Overnatninger filtreret på kommune", use_container_width=True):
            st.session_state.filter_type = "municipality"
            st.session_state.step = 2
            st.rerun()
            
    with col2:
        if st.button("Overnatninger filtreret på landsdel/region", use_container_width=True):
            st.session_state.filter_type = "destination"
            st.session_state.step = 2
            st.rerun()

    with col3:
        if st.button("Overnatninger filtreret på destination", use_container_width=True):
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

    with col2:
        if st.button("Storbyovernatninger", use_container_width=True):
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

    st.divider()
    st.write("##### Top 10 internationale markeder vs. forrige periode:")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Top 10 internationale markeder filtreret på kommune", use_container_width=True):
            st.session_state.filter_type = "municipality"
            st.session_state.step = 4
            st.rerun()
            
    with col2:
        if st.button("Top 10 internationale markeder filtreret på landsdel/region", use_container_width=True):
            st.session_state.filter_type = "destination"
            st.session_state.step = 4
            st.rerun()

    with col3:
        if st.button("Top 10 internationale markeder filtreret på destination", use_container_width=True):
            st.session_state.filter_type = "region"
            st.session_state.step = 4
            st.rerun()

    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
            
    with col1:
        st.write("##### TourMIS benchmark:")
        if st.button("København benchmark vs. andre Europæiske byer (TourMIS)", use_container_width=True):
            st.session_state.step = 6
            st.rerun()

    with col2:
        st.write("##### Benchmarking Alliance:")
        if st.button("Hotelbelægning per dag for de seneste 365 dage", use_container_width=True):
            st.session_state.step = 7
            st.rerun()
    with col3:
        st.write("##### TØBBE tal:")
        if st.button("Udvikling i turismeomsætning, jobs og skatteprovenue", use_container_width=True):
            st.session_state.step = 9
            st.rerun()