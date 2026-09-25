import streamlit as st
from steps import ( #type: ignore
    initial_menu, 
    area_selection_bednights, 
    denmark_bednights_table, 
    area_selection_top_10_markets, 
    top_10_bednights_table, 
    tourmis_benchmark_table,
    upload_benchmarking_alliance_data,
    benchmarking_alliance_table,
    area_selection_tøbbe,
    tøbbe_table,
    area_selection_hotel_capacity,
    hotel_capacity_table_and_graph,
  )

STEP_ROUTER = {
    #Regular bednights tables for a given area for total, domestic and international bednights
    1: initial_menu.render_page,
    2: area_selection_bednights.render_page,
    3: denmark_bednights_table.render_page,
    #Top 10 international markets tables
    4: area_selection_top_10_markets.render_page, #This is essentially just a duplicate of step 2 that reroutes to step 5 instead of step 3. Maybe refactor step 2 later to redirect to step 3/5 depending on some binary variable
    5: top_10_bednights_table.render_page,
    #TourMIS benchmark table
    6: tourmis_benchmark_table.render_page,
    #Benchmarking Alliance table
    7: upload_benchmarking_alliance_data.render_page,
    8: benchmarking_alliance_table.render_page,
    #TØBBE table
    9: area_selection_tøbbe.render_page,
    10: tøbbe_table.render_page,
    #Hotel capacity and occupancy graph and tables
    11: area_selection_hotel_capacity.render_page,
    12: hotel_capacity_table_and_graph.render_page,
}

def main():
    st.set_page_config(page_title="Mike's internal data tool :)", layout="wide")

    if "step" not in st.session_state:
        st.session_state.step = 1

    current_step = st.session_state.step

    render_current_step = STEP_ROUTER.get(current_step)

    page_container = st.empty()
    with page_container.container():
        if render_current_step:
            render_current_step()
        else:
            st.error(f"Invalid step: {current_step}")
            if st.button("Reset"):
                st.session_state.step = 1
                st.rerun()

if __name__ == "__main__":
    main()