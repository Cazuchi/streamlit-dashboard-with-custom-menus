import requests as rq
import pandas as pd
import numpy as np
from pyjstat import pyjstat
import streamlit as st

@st.cache_data(ttl=86400)
def create_table_two(y1, y2, y3, values, hidden_values): 
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
                "*"
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
        other_year = y3
        lastest_month_string = df['periode'].iloc[(df['periode_num'] == latest_month)].iloc[0]
        df = df.loc[(df['periode_num'] <= latest_month)].copy()
        df = df.loc[(df['tid'] == y2) | (df['tid'] == y3)].copy()
    else:
        latest_month = df['periode_num'].loc[(df['tid'] == y1) & (~pd.isna(df['value']))].max()
        latest_year = y1
        other_year = y2
        lastest_month_string = df['periode'].iloc[(df['periode_num'] == latest_month)].iloc[0]
        df = df.loc[(df['periode_num'] <= latest_month)].copy()
        df = df.loc[(df['tid'] == y1) | (df['tid'] == y2)].copy()

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
    
    exclude_countries = [
    'Afrika uden Sydafrika',
    'Asien uden Kina, Japan, Sydkorea, Indien og Thailand', 
    'Europa i øvrigt',
    'I alt',
    'Oceanien uden Australien', 
    'Syd- og Mellemamerika uden Brasilien',
    'Ukendt land', 
    'Verden udenfor Danmark',
    'Danmark'
    ]

    df = df.loc[(~df.index.isin(exclude_countries))]

    china_india_df = df.loc[(df.index == 'Kina') | (df.index == 'Indien')].sort_values(by=latest_year, ascending=False)
    china_india_mapping = {'Kina' : 'Kina*', 'Indien' : 'Indien*'}
    china_india_df.index = china_india_df.index.map(china_india_mapping)
    df_top_10 = df.nlargest(10, latest_year)
    
    df_top_10['Vækst i absolutte tal'] = df_top_10[latest_year] - df_top_10[other_year]
    df_top_10['Vækst i pct.'] = (df_top_10[latest_year]/df_top_10[other_year]-1)
    china_india_df['Vækst i absolutte tal'] = china_india_df[latest_year] - china_india_df[other_year]
    china_india_df['Vækst i pct.'] = (china_india_df[latest_year]/china_india_df[other_year]-1)

    df = pd.concat([df_top_10, china_india_df])
    df.columns.name = None
    df.index.name = None

    sort_nationality = {
        'USA' : 1,
        'Tyskland' : 1,
        'Storbritannien' : 1,
        'Sverige' : 1,
        'Italien' : 1,
        'Norge' : 1,
        'Frankrig' : 1,
        'Spanien' : 1,
        'Nederlandene' : 1,
        'Tyrkiet' : 1,
        'Polen' : 1,
        'Schweiz' : 1,
        'Finland' : 1,
        'Kina*' : 0,
        'Indien*' : 0,
    }

    df['nationality_sorting'] = df.index.map(sort_nationality)
    df.sort_values(by=[latest_year, 'nationality_sorting'], inplace=True, ascending=False)
    df.drop(columns='nationality_sorting', inplace=True)

    df.rename(columns={'2025' : f'Jan.-{lastest_month_string[:3]}. 2025', '2026' : f'Jan.-{lastest_month_string[:3]}. 2026'}, inplace=True)

    country_translation_dict = {
    'USA' : 'United States',
    'Tyskland' : 'Germany',
    'Storbritannien' : 'United Kingdom',
    'Sverige' : 'Sweden',
    'Italien' : 'Italy',
    'Norge' : 'Norway',
    'Frankrig' : 'France',
    'Spanien' : 'Spain',
    'Nederlandene' : 'Netherlands',
    'Tyrkiet' : 'Turkiye',
    'Polen' : 'Poland',
    'Schweiz' : 'Switzerland',
    'Finland' : 'Finland',
    'Kina*' : 'China',
    'Indien*' : 'India',
    }

    country_list_for_tourmis = df.index.map(country_translation_dict).to_list()

    return(df, excluded_areas, len(all_areas), lastest_month_string, country_list_for_tourmis, country_translation_dict)