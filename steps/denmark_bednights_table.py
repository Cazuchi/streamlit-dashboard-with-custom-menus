import streamlit as st
from config import YEAR_T, YEAR_T_MINUS_ONE, YEAR_T_MINUS_TWO #type: ignore
from functions import create_table_one #type: ignore

def render_page():
    try:
        table_one, excluded_cities, num_all_areas_selected, lastest_month_string, included_areas = create_table_one(
            YEAR_T, 
            YEAR_T_MINUS_ONE, 
            YEAR_T_MINUS_TWO, 
            st.session_state.selected_codes,
            st.session_state.selected_diskretioneret_option
            )

        st.markdown("###### Udvikling i samlede, danske og internationale overnatninger:")
        st.dataframe(
            table_one.style.format({
            f'Jan.-{lastest_month_string[:3]}. 2025' : '{:,.0f}',
            f'Jan.-{lastest_month_string[:3]}. 2026' : '{:,.0f}',
            'Vækst i absolutte tal' : '{:,.0f}',
            'Vækst i pct.' : '{:.1%}'
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
    except:
        st.write("""
        Alle områder som du har valgt indeholder diskretionerede værdier.
        
        Tryk på nulstil filtre og vælg "Sæt diskretionerede værdier lig med 0" i menuen for udvælgelse af områder. Hvis denne besked stadig vises, er ingen overnatningstal tilgængelige for området. Dette gælder bl.a. for Furesø Kommune.
        """)

    if st.button("**Tilbage til hovedmenuen**"):
        st.session_state.step = 1
        st.rerun()