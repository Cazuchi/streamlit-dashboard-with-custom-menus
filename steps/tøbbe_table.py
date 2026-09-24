import streamlit as st
from config import YEAR_T, YEAR_T_MINUS_ONE, YEAR_T_MINUS_TWO #type: ignore
from functions import create_tøbbe_table #type: ignore

def render_page():
    try:
        df, excluded_cities, included_areas, num_all_areas_selected, latest_year, lastest_month_string = create_tøbbe_table(st.session_state.selected_names, st.session_state.selected_codes)

        st.markdown("###### Udvikling i turismeomsætning, jobskabelse og skatteprovenue:")
        if 2026 in df.columns:
            st.write(f'OBS: 2026 tallene er baseret på overnatningstal i perioden jan.-{lastest_month_string.lower()[:3]}. {latest_year}')
        st.dataframe(
            df.style.format({
            2021 : '{:,.0f}',
            2022 : '{:,.0f}',
            2023 : '{:,.0f}',
            2024 : '{:,.0f}',
            2025 : '{:,.0f}',
            2026 : '{:,.0f}',
            },
            thousands=".",
            decimal=",",),
            width='content'
        )

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
    except Exception as e:
        st.write(e)
        st.write("""
        Alle områder som du har valgt indeholder diskretionerede værdier.
        
        Tryk på nulstil filtre og vælg "Sæt diskretionerede værdier lig med 0" i menuen for udvælgelse af områder. Hvis denne besked stadig vises, er ingen overnatningstal tilgængelige for området. Dette gælder bl.a. for Furesø Kommune.
        """)

    if st.button("**Tilbage til hovedmenuen**"):
        st.session_state.step = 1
        st.rerun()