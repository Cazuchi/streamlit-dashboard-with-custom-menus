import streamlit as st
from functions import create_hotel_capacity_table, create_hotel_capacity_graph, create_styled_capacity_table, create_styled_occupancy_table #type: ignore

def render_page():
    df, excluded_cities, included_areas, melted_df_belægning, melted_df_hotelkapacitet, num_all_areas_selected = create_hotel_capacity_table(st.session_state.selected_codes, 'excl')
    hotel_capacity_graph = create_hotel_capacity_graph(df)
    melted_df_hotelkapacitet = create_styled_capacity_table(melted_df_hotelkapacitet)
    melted_df_belægning = create_styled_occupancy_table(melted_df_belægning)

    st.write('#### Scatterplot - Hotelkapacitet og belægningsgrad over tid:')
    st.plotly_chart(hotel_capacity_graph)
    st.write('#### Belægningsgrad på hoteller per måned per år:')
    st.table(melted_df_belægning, width='content')
    st.write('#### Hotelkapacitet (værelser) per måned per år:')
    st.table(melted_df_hotelkapacitet, width='content')

    def join_with_custom_last(iterable, sep=', ', last_sep=' og '):
        items = list(iterable)
        
        if not items:
            return ''
        if len(items) == 1:
            return str(items[0])
        if len(items) == 2:
            return f"{items[0]} and {items[1]}"
            
        return f"{sep.join(items[:-1])}{last_sep}{items[-1]}"

    area_text = '**Følgende områder er inkluderet i ovenstående tal:**'
    area_text_body = join_with_custom_last(included_areas)
    st.write(f"""
        {area_text}

        {area_text_body}
    """)
    table_one_description_header = f'**Følgende områder er udeladt af summen grundet manglende eller diskretionerede overnatningstal ({f'svarende til {len(excluded_cities)} ud af {num_all_areas_selected} valgte områder'}):**'
    table_one_description_body = join_with_custom_last(excluded_cities)
    if len(excluded_cities) >= 1:
        st.write(f"""
        {table_one_description_header}

        {table_one_description_body}
        """)
    else:
        pass

    if st.button("**Tilbage til hovedmenuen**"):
        st.session_state.step = 1
        st.rerun()