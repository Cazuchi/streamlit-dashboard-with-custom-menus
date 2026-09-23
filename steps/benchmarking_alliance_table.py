import streamlit as st
from functions import create_benchmarking_alliance_table #type: ignore

def render_page():
    styled_df, min_date, max_date = create_benchmarking_alliance_table(st.session_state.df_ba)

    st.write(f'**Hotelbelægning i København By per dag per måned fra {min_date} til {max_date}:**')
    st.table(styled_df, width='content')