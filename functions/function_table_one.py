import requests as rq
import pandas as pd
import numpy as np
from pyjstat import pyjstat
import streamlit as st

@st.cache_data(ttl=86400)
def create_table_one(y1, y2, y3, values, hidden_values): 
    table_one_query = {
    "table": "VDK",
    "format": "JSONSTAT",
    "variables": [
        {
            "code": "OVERNATF",
            "values": [
                "100"
            ]
        },
        {
            "code": "OMRÅDE",
            "values": [i for i in values]
        },
        {
            "code": "NATION1",
            "values": [
                "TOT",
                "UDLAN",
                "DAN"
            ]
        },
                {
            "code": "PERIODE",
            "values": [
                "01",
                "02",
                "03",
                "04",
                "05",
                "06",
                "07",
                "08",
                "09",
                "10",
                "11",
                "12",
            ]
        },
                {
            "code": "Tid",
            "values": [
                y1,
                y2,
                y3
            ]
        }
    ]
    }

    r = rq.post(url = 'https://api.statbank.dk/v1/s12/data/vdk/', json = table_one_query)

    df = pyjstat.Dataset.read(r.text).write("dataframe")
    all_areas = [i for i in df['område'].unique()]
    month_mapping = [
    (df['periode'] == 'Januar', 1),
    (df['periode'] == 'Februar', 2),
    (df['periode'] == 'Marts', 3),
    (df['periode'] == 'April', 4),
    (df['periode'] == 'Maj', 5),
    (df['periode'] == 'Juni', 6),
    (df['periode'] == 'Juli', 7),
    (df['periode'] == 'August', 8),
    (df['periode'] == 'September', 9),
    (df['periode'] == 'Oktober', 10),
    (df['periode'] == 'November', 11),
    (df['periode'] == 'December', 12)
    ]
    conditions, replacement_values = zip(*month_mapping)
    df['periode_num'] = np.select(conditions, replacement_values, default=df['periode'])

    if pd.isna(df['periode_num'].loc[(df['tid'] == y1) & (~pd.isna(df['value']))].max()):
        latest_month = df['periode_num'].loc[(df['tid'] == y2) & (~pd.isna(df['value']))].max()
        latest_year = y2
        lastest_month_string = df['periode'].iloc[(df['periode_num'] == latest_month)].iloc[0]
        df = df.loc[(df['periode_num'] <= latest_month) & ((df['tid'] == y2) | (df['tid'] == y3))].copy()
    else:
        latest_month = df['periode_num'].loc[(df['tid'] == y1) & (~pd.isna(df['value']))].max()
        latest_year = y1
        lastest_month_string = df['periode'].iloc[(df['periode_num'] == latest_month)].iloc[0]
        df = df.loc[(df['periode_num'] <= latest_month) & ((df['tid'] == y1) | (df['tid'] == y2))].copy()

    if hidden_values == 'excl':
        df = df.groupby([ 
                'område', 
                'gæstens nationalitet'
            ]).filter(lambda x: (not x[ #Filter out destinations that DO NOT have valid data for January
                (x['periode_num'] == 1) &
                (
                    (~x['value'].isna()) &
                    (x['value'] > 0)
                )
                ].empty
            )).groupby([
                'område', 
                'gæstens nationalitet'
            ]).filter(lambda x: ( #Ensure continuity in the dataseries
                (x['periode_num'].nunique() == latest_month) and 
                x['value'].notna().all()
            )).copy()
    else:
        df['value'] = pd.to_numeric(df['value'], errors='coerce').fillna(0)
    included_areas = [i for i in df['område'].unique()]
    excluded_areas = [i for i in all_areas if i not in included_areas]
    df = df.groupby(['gæstens nationalitet', 'tid'])['value'].sum()
    df = df.reset_index()
    df = df.pivot(columns = 'tid', index = 'gæstens nationalitet', values = 'value')
    df['Vækst i absolutte tal'] = df['2026'] - df['2025']
    df['Vækst i pct.'] = df['2026']/df['2025']-1
    df.columns.name = None
    df.index.name = None

    df.rename(columns={'2025' : f'Jan.-{lastest_month_string[:3]}. 2025', '2026' : f'Jan.-{lastest_month_string[:3]}. 2026'}, inplace=True)

    sort_nationality = {
        'I alt' : 1,
        'Verden udenfor Danmark' : 2,
        'Damnark' : 3
    }

    df['nationality_sorting'] = df.index.map(sort_nationality)
    df.sort_values(by='nationality_sorting', inplace=True, ascending=True)
    df.drop(columns='nationality_sorting', inplace=True)

    return(df, excluded_areas, len(all_areas), lastest_month_string, included_areas)