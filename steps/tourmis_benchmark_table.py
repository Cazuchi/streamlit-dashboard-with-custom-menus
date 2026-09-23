import streamlit as st
from config import YEAR_T, YEAR_T_MINUS_ONE, YEAR_T_MINUS_TWO #type: ignore
from functions import create_tourmis_table #type: ignore
import time
from concurrent.futures import ThreadPoolExecutor
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

def render_page():

    if not st.session_state.get("step_6_cleared"):
        st.session_state.step_6_cleared = True
        st.rerun()

    def load_all_data():
        tourmis_table = create_tourmis_table(
            YEAR_T, 
            YEAR_T_MINUS_ONE, 
            YEAR_T_MINUS_TWO, 
            ['01'],
            'excl'
            )
        return tourmis_table

    def run_pipeline_with_context(ctx):
        #Ensures that the pipeline context and cache is synced across inner and outer functions. St.cache settings are defined in INNER functions.
        add_script_run_ctx(ctx=ctx)
        return load_all_data()

    ctx = get_script_run_ctx()

    info_slot = st.empty()
    info_slot.info(
        "Data opdateres. Vent venligst."
    )
    timer_placeholder = st.empty()
    progress_bar = st.progress(0)
    total_estimated_seconds = 300 

    with ThreadPoolExecutor() as executor:
        future = executor.submit(run_pipeline_with_context, ctx)
        start_time = time.time()

        while not future.done():
            elapsed = int(time.time() - start_time)
            remaining = max(0, total_estimated_seconds - elapsed)

            elapsed_str = time.strftime("%M:%S", time.gmtime(elapsed))
            remaining_str = time.strftime("%M:%S", time.gmtime(remaining))

            timer_placeholder.metric(
                label=f"Tid gået (Forventet tid tilbage: {remaining_str})",
                value=elapsed_str,
            )
            progress_bar.progress(min(1.0, elapsed / total_estimated_seconds))
            time.sleep(1)

        tourmis_table = future.result()

    timer_placeholder.empty()
    progress_bar.empty()
    info_slot.empty()

    st.markdown("###### Benchmark mellem København By og den gennemsnitlige Europæiske by på udvalgte markeder:")
    st.dataframe(
        tourmis_table.rename_axis('')
        .reset_index()
        .style.format(
            {
                'Copenhagen (NA)': '{:.1%}',
                'CityDNA': '{:.1%}',
                'Antal byer': '{:,.0f}',
            },
            thousands=".",
            decimal=",",
        ),
        column_config={
            '': st.column_config.TextColumn(
                '', 
                width=200
            )
        },
        hide_index=True,
        width='content',
        height='content',
    )

    if st.button("Nulstil filtre"):
        st.session_state.step = 1
        st.rerun()