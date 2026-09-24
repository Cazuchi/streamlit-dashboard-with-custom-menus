import pandas as pd
import requests as rq
import numpy as np
from pyjstat import pyjstat

def create_tøbbe_table(chosen_cities, values):
    df = pd.read_excel(r"C:\Users\mha\OneDrive - Wonderful Copenhagen\General\2. Statistik\TØBBE\2024\TØBBE konverteret til excel - nationality.xlsx")
    df.sort_values(by=['Geography Type', 'Geography'], ascending=[False, True], inplace=True)
    df = df.loc[(df['Geography'].isin(chosen_cities))]
    df = df.groupby(['Category', 'Year', 'Nationality'])[['Value']].sum()
    df.reset_index(inplace=True, drop=False)
    estimates_2025 = pd.DataFrame([
        {
            'Category' : 'Jobs',
            'Year' : 2025,
            'Nationality' : 'Total',
            'Value' : int(( 
                df['Value'].loc[(df['Category'] == 'Jobs') & (df['Year'] == 2024) & (df['Nationality'] == 'Total')].iloc[0] / 
                df['Value'].loc[(df['Category'] == 'Revenue') & (df['Year'] == 2024) & (df['Nationality'] == 'Total')].iloc[0]
                ) * df['Value'].loc[(df['Category'] == 'Revenue') & (df['Year'] == 2025) & (df['Nationality'] == 'Total')].iloc[0])
        },
        {
            'Category' : 'Tax',
            'Year' : 2025,
            'Nationality' : 'Total',
            'Value' : int(( 
                df['Value'].loc[(df['Category'] == 'Tax') & (df['Year'] == 2024) & (df['Nationality'] == 'Total')].iloc[0] / 
                df['Value'].loc[(df['Category'] == 'Revenue') & (df['Year'] == 2024) & (df['Nationality'] == 'Total')].iloc[0]
                ) * df['Value'].loc[(df['Category'] == 'Revenue') & (df['Year'] == 2025) & (df['Nationality'] == 'Total')].iloc[0])
        },
    ])

    df = pd.concat([df, estimates_2025], ignore_index=True)

    def create_table_one(y1, y2, values, hidden_values): 
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
                    y2
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
        df = df.groupby(['tid', 'gæstens nationalitet'])['value'].sum()
        df = df.reset_index()
        df = df.pivot(columns = 'tid', index = 'gæstens nationalitet', values = 'value')
        df = df.reset_index()
        df['Vækst i pct.'] = df['2026']/df['2025']
        return(df, excluded_areas, included_areas, latest_year, lastest_month_string)

    df_dst, excluded_areas, included_areas, latest_year, lastest_month_string = create_table_one('2026', '2025', values, 'excel')

    if len(excluded_areas) == 0:
        vækst_int = df_dst['Vækst i pct.'].loc[(df_dst['gæstens nationalitet'] == 'Verden udenfor Danmark')].iloc[0]
        vækst_dk = df_dst['Vækst i pct.'].loc[(df_dst['gæstens nationalitet'] == 'Danmark')].iloc[0]

        revenue_2026_dk = int(df['Value'].loc[(df['Category'] == 'Revenue') & (df['Year'] == 2025) & (df['Nationality'] == 'Danish')].iloc[0] * vækst_dk)
        revenue_2026_int = int(df['Value'].loc[(df['Category'] == 'Revenue') & (df['Year'] == 2025) & (df['Nationality'] == 'International')].iloc[0] * vækst_int)

        estimates_2025 = pd.DataFrame([
            {
                'Category' : 'Revenue',
                'Year' : 2026,
                'Nationality' : 'Danish',
                'Value' : revenue_2026_dk
            },
            {
                'Category' : 'Revenue',
                'Year' : 2026,
                'Nationality' : 'International',
                'Value' : revenue_2026_int
            },
            {
                'Category' : 'Revenue',
                'Year' : 2026,
                'Nationality' : 'Total',
                'Value' : revenue_2026_dk + revenue_2026_int
            },
            {
                'Category' : 'Jobs',
                'Year' : 2026,
                'Nationality' : 'Total',
                'Value' : int(( 
                    df['Value'].loc[(df['Category'] == 'Jobs') & (df['Year'] == 2024) & (df['Nationality'] == 'Total')].iloc[0] / 
                    df['Value'].loc[(df['Category'] == 'Revenue') & (df['Year'] == 2024) & (df['Nationality'] == 'Total')].iloc[0]
                    ) * revenue_2026_dk + revenue_2026_int)
            },
            {
                'Category' : 'Tax',
                'Year' : 2026,
                'Nationality' : 'Total',
                'Value' : int(( 
                    df['Value'].loc[(df['Category'] == 'Tax') & (df['Year'] == 2024) & (df['Nationality'] == 'Total')].iloc[0] / 
                    df['Value'].loc[(df['Category'] == 'Revenue') & (df['Year'] == 2024) & (df['Nationality'] == 'Total')].iloc[0]
                    ) * revenue_2026_dk + revenue_2026_int)
            },
        ])

        df = pd.concat([df, estimates_2025], ignore_index=True)
    else:
        pass

    df = df.loc[(df['Nationality'] == 'Total')].pivot_table(index=['Category'], columns='Year', values='Value')
    df.reset_index(drop=False, inplace=True)
    df_sort = {
        'Revenue' : 1,
        'Jobs' : 2,
        'Tax' : 3
    }
    df_rename = {
        'Revenue' : 'Turismeomsætning (mio. kr.)',
        'Jobs' : 'Jobskabelse',
        'Tax' : 'Skatteprovenue (mio. kr.)'
    }
    df['sort'] = df['Category'].map(df_sort)
    df.sort_values(by='sort', ascending=True, inplace=True)
    df['Category'] = df['Category'].map(df_rename)
    df.set_index(keys='Category', drop=True, inplace=True)
    df.drop(columns='sort', inplace=True)
    df.columns.name = None
    df.index.name = None
    return(df, excluded_areas, included_areas, len(included_areas), latest_year, lastest_month_string)