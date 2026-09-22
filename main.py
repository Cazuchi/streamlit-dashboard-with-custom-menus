import streamlit as st
from steps import initial_menu, area_selection_bednights, denmark_bednights_table  #type: ignore

STEP_ROUTER = {
    1: initial_menu.render_page,
    2: area_selection_bednights.render_page,
    3: denmark_bednights_table.render_page,
}

def main():
    st.set_page_config(page_title="Mike's internal data tool :)", layout="wide")

    if "step" not in st.session_state:
        st.session_state.step = 1

    current_step = st.session_state.step

    render_current_step = STEP_ROUTER.get(current_step)

    if render_current_step:
        render_current_step()
    else:
        st.error(f"Invalid step: {current_step}")
        if st.button("Reset"):
            st.session_state.step = 1
            st.rerun()

if __name__ == "__main__":
    main()