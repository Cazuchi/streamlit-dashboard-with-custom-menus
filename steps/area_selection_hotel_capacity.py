import streamlit as st
import pandas as pd

TØBBE_OPTIONS = {
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
    'Aalborg' : '851',
    'Wonderful Copenhagen' : '0100',
    'VisitNordsjælland' : '0300',
    'Destination Bornholm' : '0400',
    'Destination Fjordlandet' : '0500',
    'Destination Sjælland' : '0610',
    'Visit Sydsjælland & Møn' : '0620',
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

def render_page():
    st.subheader(f"Vælg kommuner:")

    options = (sorted(TØBBE_OPTIONS.keys()))
    box_height = 710
    active_dict = TØBBE_OPTIONS
    pre_check_values = False

    btn_col1, btn_col2, _, btn_col3, btn_col4 = st.columns([1, 1, 7, 1, 1])
    
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

    with btn_col3:
        if st.button("København By", use_container_width=True):
            st.session_state.selected_names = ['København', 'Frederiksberg', 'Dragør', 'Tårnby']
            st.session_state.selected_codes = ['01']
            st.session_state.step = 12
            st.rerun()

    with btn_col4:
        if st.button("Storbyerne", use_container_width=True):
            st.session_state.selected_names = ['København', 'Odense', 'Aarhus', 'Aalborg']
            st.session_state.selected_codes = ['01', '02', '461', '751', '851']
            st.session_state.step = 12
            st.rerun()

    error_containter = st.empty()
    
    # st.form keeps the UI responsive while users uncheck multiple items
    with st.form("selection_form"):
        
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

        col1, col2, _ = st.columns([1, 2, 8])
        with col1:
            if st.form_submit_button("**Run Data Collection**", type="primary"):
                if not selected_names:
                    error_containter.error('Vælg et eller flere områder før du fortsætter.')
                    error_containter_two.error('Vælg et eller flere områder før du fortsætter.')
                else:
                    st.session_state.selected_names = selected_names
                    st.session_state.selected_codes = [active_dict[name] for name in selected_names]
                    st.session_state.step = 12
                    st.rerun()
        with col2:
            if st.form_submit_button("**Tilbage til hovedmenuen**", type="primary"):
                st.session_state.step = 1
                st.rerun()