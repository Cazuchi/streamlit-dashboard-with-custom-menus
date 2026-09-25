import pandas as pd
import requests as rq
import numpy as np
from pyjstat import pyjstat
import streamlit as st
from datetime import datetime

@st.cache_data(ttl=86400)
def create_hotel_capacity_table(values, hidden_values): 
    start_year = 2017
    current_year = datetime.today().year
    years = list(range(start_year, current_year + 1))
    years = [str(i) for i in years]

    table_one_query = {
    "table": "VDK",
    "format": "JSONSTAT",
    "variables": [
        {
            "code": "OVERNATF",
            "values": [
                "110"
            ]
        },
        {
            "code": "OMRÅDE",
            "values": values
        },
        {
            "code": "KAPACITET",
            "values": [
                "27",
                "35"
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
            "values": years
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

    latest_month = df['periode_num'].loc[(df['tid'] == years[-1]) & (~pd.isna(df['value']))].max()
    latest_year = years[-1]
    lastest_month_string = df['periode'].iloc[(df['periode_num'] == latest_month)].iloc[0]

    df_latest_year = df.loc[(df['tid']) == years[-1]].copy()
    df_latest_year = df_latest_year.loc[(df['periode_num'] <= latest_month)].copy()
    df_other_years = df.loc[(df['tid']) != years[-1]].copy()
    df = pd.concat(objs=[df_other_years, df_latest_year], ignore_index=True)
    length_of_df = len(df)

    if hidden_values == 'excl':
        df = df.groupby([ 
                'område'
            ]).filter(lambda x: ( #Ensure continuity in the dataseries
                (len(x) == length_of_df) and 
                x['value'].notna().all()
            )).copy()
    else:
        df['value'] = pd.to_numeric(df['value'], errors='coerce').fillna(0)
    included_areas = [i for i in df['område'].unique()]
    excluded_areas = [i for i in all_areas if i not in included_areas]

    df = df.pivot_table(index=['overnatningsform', 'område', 'periode', 'periode_num', 'tid'], columns='kapacitet', values='value')
    df.reset_index(inplace=True, drop=False)
    df.rename(columns={
        'Antal værelser eller enheder, Hotel/camping' : 'Hotelkapacitet', 
        'Kapacitetsudnyttelse af værelser eller enheder, hotel/camping (%)' : 'Belægningsgrad'
    }, inplace=True)
    df['Belægningsgrad'] = df['Belægningsgrad'] / 100
    df['Solgte hotelværelser'] = df['Hotelkapacitet'] * df['Belægningsgrad']
    df = df.groupby(['tid', 'periode', 'periode_num'])[['Hotelkapacitet', 'Solgte hotelværelser']].sum()
    df['Belægningsgrad'] = df['Solgte hotelværelser'] / df['Hotelkapacitet']
    df.reset_index(inplace=True, drop=False)
    df.sort_values(by=['tid', 'periode_num'], inplace=True, ascending=True)

    def format_x_labels(row):
        return(row['periode'][:3]+" '"+row['tid'][-2:])
    df['x_labels'] = df.apply(format_x_labels, axis=1)

    melted_df = df.melt(
    id_vars=['tid', 'periode'],
    value_vars=['Hotelkapacitet', 'Belægningsgrad'],
    var_name='metric',
    value_name='val',
    )

    melted_df = melted_df.pivot_table(
        index=['metric', 'tid'], columns='periode', values='val'
    )

    melted_df = melted_df[['Januar', 'Februar', 'Marts', 'April', 'Maj', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'December']]
    melted_df.reset_index(inplace=True, drop=False)
    melted_df_belægning = melted_df.loc[(melted_df['metric'] == 'Belægningsgrad')].copy()
    melted_df_belægning.drop(columns='metric', inplace=True)
    melted_df_hotelkapacitet = melted_df.loc[(melted_df['metric'] == 'Hotelkapacitet')].copy()
    melted_df_hotelkapacitet.drop(columns='metric', inplace=True)
    
    return(df, excluded_areas, included_areas, melted_df_belægning, melted_df_hotelkapacitet, len(all_areas))