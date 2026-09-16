import streamlit as st
from datetime import datetime
from function_table_one import create_table_one #type: ignore

_current_year = datetime.today().year

YEAR_T = str(_current_year)
YEAR_T_MINUS_ONE = str(_current_year - 1)
YEAR_T_MINUS_TWO = str(_current_year - 2)

st.set_page_config(layout="wide")

# 1. Initialize session state keys for navigation and selections
if "step" not in st.session_state:
    st.session_state.step = 1
if "filter_type" not in st.session_state:
    st.session_state.filter_type = None

# Sample data options
MUNICIPALITY_OPTIONS = {
    'København' : '101',
    'Frederiksberg' : '147',
    'Dragør' : '155',
    'Tårnby' : '185',
    'Albertslund' : '165',
    'Ballerup' : '151',
    'Brøndby' : '153',
    'Gentofte' : '157',
    'Gladsaxe' : '159',
    'Glostrup' : '161',
    'Herlev' : '163',
    'Hvidovre' : '167',
    'Høje-Taastrup' : '169',
    'Ishøj' : '183',
    'Lyngby-Taarbæk' : '173',
    'Rødovre' : '175',
    'Vallensbæk' : '187',
    'Allerød' : '201',
    'Egedal' : '240',
    'Fredensborg' : '210',
    'Frederikssund' : '250',
    'Furesø' : '190',
    'Gribskov' : '270',
    'Halsnæs' : '260',
    'Helsingør' : '217',
    'Hillerød' : '219',
    'Hørsholm' : '223',
    'Rudersdal' : '230',
    'Bornholm' : '400',
    'Greve' : '253',
    'Køge' : '259',
    'Lejre' : '350',
    'Roskilde' : '265',
    'Solrød' : '269',
    'Faxe' : '320',
    'Guldborgsund' : '376',
    'Holbæk' : '316',
    'Kalundborg' : '326',
    'Lolland' : '360',
    'Næstved' : '370',
    'Odsherred' : '306',
    'Ringsted' : '329',
    'Slagelse' : '330',
    'Sorø' : '340',
    'Stevns' : '336',
    'Vordingborg' : '390',
    'Assens' : '420',
    'Faaborg-Midtfyn' : '430',
    'Kerteminde' : '440',
    'Langeland' : '482',
    'Middelfart' : '410',
    'Nordfyns' : '480',
    'Nyborg' : '450',
    'Odense' : '461',
    'Svendborg' : '479',
    'Ærø' : '492',
    'Billund' : '530',
    'Esbjerg' : '561',
    'Fanø' : '563',
    'Fredericia' : '607',
    'Haderslev' : '510',
    'Kolding' : '621',
    'Sønderborg' : '540',
    'Tønder' : '550',
    'Varde' : '573',
    'Vejen' : '575',
    'Vejle' : '630',
    'Aabenraa' : '580',
    'Favrskov' : '09',
    'Hedensted' : '710',
    'Horsens' : '766',
    'Norddjurs' : '615',
    'Odder' : '727',
    'Randers' : '730',
    'Samsø' : '741',
    'Silkeborg' : '740',
    'Skanderborg' : '746',
    'Syddjurs' : '706',
    'Aarhus' : '751',
    'Herning' : '657',
    'Holstebro' : '661',
    'Ikast-Brande' : '756',
    'Lemvig' : '665',
    'Ringkøbing-Skjern' : '760',
    'Skive' : '779',
    'Struer' : '671',
    'Viborg' : '791',
    'Brønderslev' : '810',
    'Frederikshavn' : '813',
    'Hjørring' : '860',
    'Jammerbugt' : '849',
    'Læsø' : '825',
    'Mariagerfjord' : '846',
    'Morsø' : '773',
    'Rebild' : '840',
    'Thisted' : '787',
    'Vesthimmerlands' : '820',
    'Aalborg' : '851'
}
DESTINATION_OPTIONS = {
    'Hele landet' : '000',
    'Landsdel Byen København' : '01',
    'Landsdel Københavns omegn' : '02',
    'Landsdel Nordsjælland' : '03',
    'Region Sjælland' : '085',
    'Landsdel Østsjælland' : '05',
    'Landsdel Vest- og Sydsjælland' : '06',
    'Region Syddanmark' : '083',
    'Landsdel Fyn' : '07',
    'Landsdel Sydjylland' : '08',
    'Region Midtjylland' : '082',
    'Region Nordjylland' : '081'
}
REGION_OPTIONS = {
    'Wonderful Copenhagen' : '0100',
    'VisitNordsjælland' : '0300',
    'Destination Bornholm' : '0400',
    'Destination Fjordlandet' : '0500',
    'Destination Sjælland' : '0610',
    'Visit Sydsjælland og Møn' : '0620',
    'VisitLollandFalster' : '0630',
    'Destination Fyn' : '0700',
    'Destination Sønderjylland' : '0860',
    'Destination Trekantområdet' : '0870',
    'Destination Vadehavskysten' : '0880',
    'Destination Vesterhavet' : '0890',
    'Destination Kystlandet' : '0900',
    'Aarhusregionen' : '0910',
    'Destination Limfjorden' : '1010',
    'VisitHerning' : '1011',
    'Destination Himmerland' : '1110',
    'Destination Nord' : '1111',
    'Destination NordVestkysten' : '1112'
}

# STEP 1: Choice Buttons
if st.session_state.step == 1:
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

# STEP 2: Selection Grid & Execution Trigger
elif st.session_state.step == 2:

    st.write(f"### Vælg hvordan diskretionerede værdier skal håndteres:")

    # 1. Initialize state key
    if "selected_diskretioneret_option" not in st.session_state:
        st.session_state.selected_diskretioneret_option = None  # Stores 'X', 'Y', or None

    # 2. Layout buttons side-by-side
    col1, col2, col3, _ = st.columns([1, 1, 1, 2])

    with col1:
        type_x = "primary" if st.session_state.selected_diskretioneret_option == "excl" else "secondary"
        if st.button("Eksluder områder med diskretionerede værdier", type=type_x, use_container_width=True):
            st.session_state.selected_diskretioneret_option = "excl"
            st.rerun()

    with col2:
        type_y = "primary" if st.session_state.selected_diskretioneret_option == "incl" else "secondary"
        if st.button("Sæt diskretionerede værdier lig med 0", type=type_y, use_container_width=True):
            st.session_state.selected_diskretioneret_option = "incl"
            st.rerun()

    with col3:
        with st.popover("Info"):
            st.markdown("""
                Danmarks Statistik diskretionere værdier hvis der er mindre end tre overnatningssteder i et område, hvorfor det ikke altid er muligt at se antallet af overnatninger i et område. 
                Dette er primært et problem for enkeltstående kommuner og ikke for større områder.

                Hvis du skal bruge overnatningstallet for flere kommuner samlet, så vælg "ekskluder områder med diskretionerede værdier". Resultatet viser dig hvilke kommuner som er ekskluderet,
                så du kan videreformidle det.
            """
            )

    filter_label = st.session_state.filter_type.capitalize()
    st.subheader(f"Select {filter_label} Data Points")

    if st.session_state.filter_type == "municipality":
        options = (sorted(MUNICIPALITY_OPTIONS.keys()))
        box_height = 600
        active_dict = MUNICIPALITY_OPTIONS
        pre_check_values = False
    elif st.session_state.filter_type == "destination":
        options = (sorted(DESTINATION_OPTIONS.keys()))
        box_height = 110
        active_dict = DESTINATION_OPTIONS
        pre_check_values = False
    else:
        options = (sorted(REGION_OPTIONS.keys()))
        box_height = 150
        active_dict = REGION_OPTIONS
        pre_check_values = False

    options = sorted(active_dict.keys())

    btn_col1, btn_col2, _ = st.columns([1, 1, 8])
    
    with btn_col1:
        if st.button("Select All", use_container_width=True):
            for option in options:
                st.session_state[f"chk_{option}"] = True
            st.rerun()

    with btn_col2:
        if st.button("Deselect All", use_container_width=True):
            for option in options:
                st.session_state[f"chk_{option}"] = False
            st.rerun()

    error_containter = st.empty()
    
    # st.form keeps the UI responsive while users uncheck multiple items
    with st.form("selection_form"):
        st.write("Uncheck any options to exclude:")
        
        selected_names = []
        # Fixed-height scrollable container containing a 3-column grid
        with st.container(height=box_height):
            cols = st.columns(7)
            for idx, option in enumerate(options):
                col = cols[idx % 7]  # Distribute across columns 0, 1, 2
                
                # value=True pre-checks the box
                if col.checkbox(option, value=pre_check_values, key=f"chk_{option}"):
                    selected_names.append(option)

        error_containter_two = st.empty()

        col1, col2, _ = st.columns([1, 1, 9])
        with col1:
            if st.form_submit_button("Run Data Collection", type="primary"):
                if st.session_state.get('selected_diskretioneret_option') == None:
                    error_containter.error('Vælg "Eksluder områder med diskretionerede værdier" eller "Sæt diskretionerede værdier lig med 0" i toppen af siden før du går videre.')
                    error_containter_two.error('Vælg "Eksluder områder med diskretionerede værdier" eller "Sæt diskretionerede værdier lig med 0" i toppen af siden før du går videre.')
                elif not selected_names:
                    error_containter.error('Vælg et eller flere områder før du fortsætter.')
                    error_containter_two.error('Vælg et eller flere områder før du fortsætter.')
                else:
                    st.session_state.selected_names = selected_names
                    st.session_state.selected_codes = [active_dict[name] for name in selected_names]
                    st.session_state.step = 3
                    st.rerun()
        with col2:
            if st.form_submit_button("Go back", type="primary"):
                st.session_state.step = 1
                st.rerun()

# STEP 3: Print Selected Options
elif st.session_state.step == 3:
    try:
        table_one, excluded_cities, num_all_areas_selected, included_areas = create_table_one(
            YEAR_T, 
            YEAR_T_MINUS_ONE, 
            YEAR_T_MINUS_TWO, 
            st.session_state.selected_codes,
            st.session_state.selected_diskretioneret_option
            )

        st.markdown("###### Tabel 1:")
        st.dataframe(
            table_one.style.format({
            '2025' : '{:,.0f}',
            '2026' : '{:,.0f}',
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

        table_one_description_header = f'**Følgende områder er udeladt af summen grundet manglende eller diskretionerede overnatningstal ({f'svarende til {len(excluded_cities)} ud af {num_all_areas_selected} valgte områder'}):**'
        table_one_description_body = join_with_custom_last(excluded_cities)
        if len(excluded_cities) > 1:
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

    if st.button("Nulstil filtre"):
        st.session_state.step = 1
        st.rerun()