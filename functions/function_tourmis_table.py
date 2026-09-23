# Standard library imports
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from io import BytesIO
from itertools import batched

# Third-party imports
import numpy as np
import pandas as pd
import pyarrow
import requests as rq
from google.cloud import secretmanager
from pyjstat import pyjstat
import streamlit as st

@st.cache_data(ttl=86400)
def prepare_log_in_info() -> tuple[str, str]:
    """
    Loads login credentials from a local JSON config file.
    Switch to environmental variables if moving to a cloud VM or docker.
    """
    with open(r"C:\Users\mha\OneDrive - Wonderful Copenhagen\Skrivebord\Python\tourmis.json", 'r') as f:
        config = json.load(f)
    username = config['username']
    password = config['password']
    return(username, password)

def get_auth_token(username: str, password: str) -> str:
    '''
    Get an auth token. Note: This is how the API is designed. It expects the username and password as url parameters.
    '''
    url = f'https://www.tourmis.info/api.pl?id={username}&pw={password}'
    result = rq.get(url)
    token = result.content.decode('ISO-8859-1').split('<token>')[1].split('</token>')[0]
    return(token)

@st.cache_data(ttl=86400)
def build_market_dict(username, password) -> dict:
    '''
    Builds a dictionary of shorthand market names to full market names. The API returns shorthand market names, so using this to convert those to full market names is required to make it look nice in the dashboard.

    Note: This function design assumes you run it immediately after grabbing a token. Otherwise the token might have expired and this function needs to be updated to handle token errors, similar to the collect_main_data() function.
    '''
    token = get_auth_token(username, password)
    url = f'https://www.tourmis.info/api.pl?d=CPH&c=NG&x=1&l=en&token={token}'
    result = rq.get(url)
    xml_data = result.content
    xml_file_like = BytesIO(xml_data)
    context = ET.iterparse(xml_file_like, events=('start', 'end'))

    market_dict = {}
    for event, elem in context:
        if event == 'end' and elem.tag == 'data':
            if elem.find('code').text == 'NG': #Filters out an error in the market_dict data
                pass
            else:
                market_dict.update({elem.find('code').text : elem.find('label').text})
    return({value : key for key, value in market_dict.items()})

@st.cache_data(ttl=86400)
def build_city_dict(username, password) -> dict:
    token = get_auth_token(username, password)
    url = f'https://www.tourmis.info/api.pl?c=NG&m=DK&x=1&l=en&token={token}'
    result = rq.get(url)
    
    # Ensure HTTP request succeeded
    result.raise_for_status()

    try:
        root = ET.fromstring(result.content)
    except ET.ParseError:
        print("API did not return valid XML. Check token or endpoint.")
        sys.exit(1)

    city_dict = {}

    # Iterate through elements that contain both code and label children
    for parent in root.iter():
        code_node = parent.find('code')
        label_node = parent.find('label')

        if code_node is not None and label_node is not None:
            if code_node.text and label_node.text:
                city_dict[code_node.text] = label_node.text

    if not city_dict:
        print("Warning: city_dict is empty. Check API response or token validity.")

    to_remove = [
        'AD', 'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'GE', 'DE', 'GR', 
        'HU', 'IS', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'ME', 'NL', 'NO', 'PL', 'PT', 'RO', 
        'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'TR', 'UA', 'UK',
        'BU', 'KA', 'FO', 'BEFLBRU', 'NI', 'SA', 'ST', 'TI', 'OB', 'VO',
        'WI', 'NG', 'JER'
    ]
    for key in to_remove:
        city_dict.pop(key, None)

    return city_dict

@st.cache_data(ttl=86400)
def modify_country_list_for_tourmis(country_list_for_tourmis, market_dict):
    country_list_for_tourmis.extend(['Europe', 'Total foreign', 'Total foreign and domestic'])
    country_list_for_tourmis = ':'.join(market_dict[country] for country in country_list_for_tourmis if country in market_dict)
    return country_list_for_tourmis

@st.cache_data(ttl=86400)
def collect_main_data(city_dict: dict, username: str, password: str, y1, y2, y3, country_string) -> pd.DataFrame:
    '''
    This is the main data collection loop. 
    Use historical_year_set if historical data (2017 and onwards) needs to be recollected for whatever reason.
    Define a new variable for specific years, if, for instance, a destination goes back and updates XYZ specific years. In that case replace the city loop with just that city as well, otherwise this will pull A LOT of unnecessary
    rows and take much longer than necessary.
    Use year_set to just grab the most recent data which is what is most likely to have been adjusted since the last data pull. This heavily limits the amount of data requested from the API and, as a result of API thresholds,
    quite heavily limits the time it takes to pull that data.
    '''
    token = get_auth_token(username, password)
    collected_data_monthly = {
        'Destinations' : [],
        'Definition' : [],
        'Market' : [],
        'Year' : [],
        'Month' : [],
        'Bed nights' : []
    }

    cities = [i for i in city_dict.keys()]
    pairs = [':'.join(cities[i:i+2]) for i in range(0, len(cities), 2)]

    break_all = False #Used in the retry logic. If 3 attempts to get data from the API fails for a specific combination of parameters, data collection is aborted. 
    #Has never been an issue, but stability issues with the API did cause it to drop connection every now and then at one point, so that's why this is here.
    for city in pairs:
            
        if break_all:
            break

        for attempt in range(3):
            try:
                url = f'https://www.tourmis.info/api.pl?d={city}&c=N&m={country_string}&y={y1}:{y2}:{y3}&token={token}'
                result = rq.get(url)

                #Check if the token has expired and request a new token if that's the case
                if any(token in result.content.decode('ISO-8859-1') for token in ['Token invalid', 'Token missing']) == True:
                    token = get_auth_token(username, password)       

                    url = f'https://www.tourmis.info/api.pl?d={city}&c=N&m={country_string}&y={y1}:{y2}:{y3}&token={token}'
                    result = rq.get(url)

                xml_data = result.content
                xml_file_like = BytesIO(xml_data)
                context = ET.iterparse(xml_file_like, events=('start', 'end'))

                for event, elem in context:
                    if event == 'end' and elem.tag == 'data':
                        destination = elem.find('destination').text
                        market = elem.find('market').text
                        year_variable = elem.find('year').text
                        total_value = elem.find('value').text
                        definition = elem.find('content').text

                        for value in elem.findall('value'): #Grab monthly data values
                            month = value.get('month')
                            if month:

                                collected_data_monthly['Destinations'].append(destination)
                                collected_data_monthly['Definition'].append(definition)
                                collected_data_monthly['Market'].append(market)
                                collected_data_monthly['Year'].append(year_variable)
                                collected_data_monthly['Month'].append(month)
                                collected_data_monthly['Bed nights'].append(value.text)

                time.sleep(1.2) #Based on testing and API thresholds for the number of allowed requests per minute. Non-negotiable.
                elem.clear()
                break

            except ConnectionError as e: #The API used to have connection issues that would result in random drops of the connection. Leaving this here just in case, but it doesn't seem to trigger much anymore. Seems the API stability has been drastically improved.

                if attempt < 2:
                    print(f"Connection failed: {e}")
                    print("Waiting 5 minutes before trying again...")
                    #This cooldown might not be necessary anymore. It's a long cooldown because the API was VERY temperamental a while ago. It doesn't really seem to drop connections anymore,
                    #but it did it a lot at one point and needed some time to recover. Leaving this for now, since the exception doesn't seem to trigger anymore, but if it starts happening again,
                    #it'd be prudent to do some testing for how long of a timeout the API needs to recover. Last time I tested what cooldown duration would give me reproducible, successful data
                    #collection runs was mid-august 2025.
                    time.sleep(300)

                else:
                    print('Connection failed 3 times. Aborting.')
                    break_all = True
                    break

        if break_all:
            break

    df = pd.DataFrame(collected_data_monthly)
    return(df)

@st.cache_data(ttl=86400)
def clean_data(df, country_translation_dict, market_dict, y1, y2, y3, latest_month, latest_year):
    df = df.copy()
    df['Month'] = df['Month'].astype('Int64')

    if latest_year == y1:
        df = df.loc[((df['Year'] == y1) | (df['Year'] == y2)) & (df['Month'] <= latest_month)]
    else:
        df = df.loc[((df['Year'] == y2) | (df['Year'] == y3)) & (df['Month'] <= latest_month)]

    df['Bed nights'] = pd.to_numeric(df['Bed nights'], errors='coerce')

    exclude_cities_by_country = {
        'AT': ['BRZ', 'EIS', 'GRZ', 'INN', 'KLA', 'LNZ', 'SPO', 'SZG', 'VIE'],
        'BE': ['ANR', 'BGN', 'BRU', 'GNE', 'LVN', 'MEQ', 'MOJ', 'NAX', 'OST'],
        'BG': ['SOF'],
        'CH': ['BIE', 'BRN', 'BSL', 'GVA', 'LUG', 'MOX', 'QGL', 'QLJ', 'QLS', 'WIN', 'ZRH'],
        'CY': ['NIC'],
        'CZ': ['BRQ', 'BUW', 'GTW', 'HKR', 'JIH', 'KLV', 'LIB', 'OLO', 'OSR', 'PDB', 'PLS', 'PRG', 'UNL'],
        'DE': ['AAH', 'AGB', 'BAD', 'BER', 'BNJ', 'BRE', 'CGN', 'DAS', 'DRS', 'FMO', 'FRA', 'HAJ', 'HAM', 'LBC', 'LPZ', 'MHG', 'MUC', 'MZY', 'NUE', 'POT', 'QDU', 'QFB', 'QHD', 'QKA', 'QWU', 'RCK', 'REB', 'STR', 'TRI', 'WER'],
        'DK': ['AAL', 'AAR', 'CPH', 'ODE'],
        'EE': ['TLL'],
        'ES': ['AGP', 'BCN', 'BEX', 'BIO', 'COR', 'EAS', 'GIJ', 'GIO', 'GRX', 'LCG', 'LM2', 'LPV', 'MAD', 'PMI', 'QGN', 'SCQ', 'SVQ', 'TFS', 'VLC', 'ZAZ'],
        'FI': ['ESX', 'HEL', 'JYV', 'OUL', 'TKU', 'TMP'],
        'FO': ['FAE'],
        'FR': ['AVN', 'BIQ', 'BOD', 'DIJ', 'EBU', 'ENC', 'ETZ', 'JCA', 'LIL', 'LYS', 'MLH', 'MPL', 'MRS', 'NCE', 'NTE', 'PAR', 'QXB', 'RHE', 'TLN', 'TLS', 'URO'],
        'UK': ['BHD', 'BHX', 'BRS', 'CWL', 'EDI', 'GLA', 'LBA', 'LON', 'LPL', 'MAN', 'NOT', 'YOR'],
        'GE': ['TBS'],
        'GR': ['ATH', 'IOA', 'SKG'],
        'HR': ['DBV', 'OPT', 'RJK', 'SPU', 'ZAG'],
        'HU': ['BUD'],
        'IE': ['DBN', 'ORK'],
        'IL': ['JRS', 'TLV'],
        'IS': ['REK'],
        'IT': ['BLQ', 'BRI', 'BZO', 'CAG', 'FLR', 'GOA', 'MIL', 'NAP', 'PAL', 'PMO', 'QPA', 'RAN', 'RMI', 'ROM', 'SAY', 'TRN', 'TRS', 'UDN', 'VCE', 'VIC', 'VRN'],
        'LT': ['KUN', 'VON'],
        'LU': ['LUX'],
        'LV': ['LPX', 'LV0002000', 'LV0003000', 'LV0004000', 'LV0006000', 'LV0007000', 'LV0031010', 'LV0040010', 'LV0054010', 'RIX'],
        'MC': ['MC'],
        'ME': ['TGD'],
        'MK': ['SKP'],
        'MT': ['MLA'],
        'NL': ['AMS', 'HAG', 'HAQ', 'MST', 'RTM', 'UTC'],
        'NO': ['BGO', 'OSL', 'TRD', 'TRO'],
        'PL': ['GDN', 'KRK', 'LUZ', 'POZ', 'WAW'],
        'PT': ['BGZ', 'CBP', 'FAO', 'FNC', 'LIS', 'LPCS', 'LPEV', 'OPO', 'SRY', 'XSZ'],
        'RO': ['OTB', 'TSR'],
        'RS': ['BEG', 'NOS'],
        'RU': ['LED', 'MOW', 'SVX'],
        'SE': ['GOT', 'HMA', 'STO', 'UPP'],
        'SI': ['BL2', 'LJU', 'MBX', 'SI009', 'SI090'],
        'SK': ['BTS'],
        'TR': ['ESB', 'IST'],
        'UA': ['KBP', 'LWO', 'ODS'],
        'CHINA' : [],
        'IN' : [],
        'EUR' : [],
        'ZA' : [],
        'ZZ' : [],
        'US' : []
    }

    df = df.groupby([ 
        'Destinations', 
        'Definition', 
        'Market', 
        'Year'
    ]).filter(lambda x: (not x[ #Filter out destinations that DO NOT have valid data for January
        (x['Month'] == 1) &
        (
            (~x['Bed nights'].isna()) &
            (x['Bed nights'] > 0)
        )
        ].empty
    )).groupby([
        'Destinations', 
        'Definition', 
        'Market', 
        'Year'
    ]).filter(lambda x: ( #Ensure continuity in the dataseries
        (x['Month'].nunique() == latest_month) and 
        x['Bed nights'].notna().all() and
        (x.name[0] not in exclude_cities_by_country[x.name[2]])
    )).copy()

    df = df.loc[(~pd.isna(df['Bed nights']))].copy()

    df['Bed nights'] = df['Bed nights'].astype('Int64')

    df = pd.DataFrame(df.groupby(['Destinations', 'Market', 'Year'])['Bed nights'].sum())
    df.reset_index(inplace=True, drop=False)

    df = df.groupby([
    'Destinations', 
    'Market'
    ]).filter(lambda x: (x['Year'].nunique() == 2)).copy()

    city_count = df.groupby(['Market'])['Market'].agg(lambda x: x.count() / 2).to_dict()

    df_cph = df.loc[(df['Destinations'] == 'CPH')].copy()
    df_osl = df.loc[(df['Destinations'] == 'OSL')].copy()
    df_sto = df.loc[(df['Destinations'] == 'STO')].copy()
    df_hel = df.loc[(df['Destinations'] == 'HEL')].copy()
    df_others = df.copy()

    df_scandinavia = pd.concat([df_cph, df_osl, df_sto, df_hel])
    df_scandinavia = df_scandinavia.loc[(df_scandinavia['Market'] == 'ZA') | (df_scandinavia['Market'] == 'ZZ')].copy()

    df_others = pd.DataFrame(df_others.groupby(['Market', 'Year'])['Bed nights'].mean())
    df_others.reset_index(inplace=True, drop=False)
    df_others['Destinations'] = 'Average destination'
    df_others = df_others[['Destinations', 'Market', 'Year', 'Bed nights']]
    df = pd.concat([df_cph, df_others])

    df = df.pivot(columns=['Destinations', 'Year'], index='Market', values='Bed nights')
    df_scandinavia = df_scandinavia.pivot(columns=['Destinations', 'Year'], index='Market', values='Bed nights')

    sort_markets = {
        'CHINA' : 5,
        'IN' : 4,
        'EUR' : 3,
        'ZA' : 2,
        'ZZ' : 1
    }

    df['Sort markets'] = df.index.map(sort_markets).fillna(6)

    if latest_year == y1:
        df['Copenhagen (NA)'] = df[('CPH', y1)] / df[('CPH', y2)] - 1
        df['CityDNA'] = df[('Average destination', y1)] / df[('Average destination', y2)] - 1
        df = df.sort_values(by=[('Sort markets', ''), ('CPH', y1)], ascending=False)

        df_scandinavia['CPH growth'] = df_scandinavia[('CPH', y1)] / df_scandinavia[('CPH', y2)] - 1
        df_scandinavia['OSL growth'] = df_scandinavia[('OSL', y1)] / df_scandinavia[('OSL', y2)] - 1
        df_scandinavia['STO growth'] = df_scandinavia[('STO', y1)] / df_scandinavia[('STO', y2)] - 1
        df_scandinavia['HEL growth'] = df_scandinavia[('HEL', y1)] / df_scandinavia[('HEL', y2)] - 1
    else:
        df['Copenhagen (NA)'] = df[('CPH', y2)] / df[('CPH', y3)] - 1
        df['CityDNA'] = df[('Average destination', y2)] / df[('Average destination', y3)] - 1
        df = df.sort_values(by=[('Sort markets', ''), ('CPH', y2)], ascending=False)

        df_scandinavia['CPH growth'] = df_scandinavia[('CPH', y2)] / df_scandinavia[('CPH', y3)] - 1
        df_scandinavia['OSL growth'] = df_scandinavia[('OSL', y2)] / df_scandinavia[('OSL', y3)] - 1
        df_scandinavia['STO growth'] = df_scandinavia[('STO', y2)] / df_scandinavia[('STO', y3)] - 1
        df_scandinavia['HEL growth'] = df_scandinavia[('HEL', y2)] / df_scandinavia[('HEL', y3)] - 1

    df['Antal byer'] = df.index.map(city_count)

    market_dict = {value : key for key, value in market_dict.items()}
    df.index = df.index.map(market_dict)
    df_scandinavia.index = df_scandinavia.index.map(market_dict)

    country_translation_dict = {value : key for key, value in country_translation_dict.items()}
    country_translation_dict.update({
        'China' : 'Kina*',
        'India' : 'Indien*',
        'Europe' : 'Europa',
        'Total foreign' : 'Internationale overnatninger',
        'Total foreign and domestic' : 'Alle overnatninger'
    })

    df.index = df.index.map(country_translation_dict)
    df_scandinavia.index = df_scandinavia.index.map(country_translation_dict)

    df = df[[('Copenhagen (NA)', ''), ('CityDNA', ''), ('Antal byer', '')]]
    df_scandinavia = df_scandinavia[[('CPH growth', ''), ('OSL growth', ''), ('STO growth', ''), ('HEL growth', '')]]

    df.columns = df.columns.get_level_values(0)
    df_scandinavia.columns = df_scandinavia.columns.get_level_values(0)
    df.columns.name = None
    df_scandinavia.columns.name = None
    df.index.name = None
    df_scandinavia.index.name = None

    df_scandinavia.rename(columns={
    'CPH growth' : 'Copenhagen pct. growth',
    'OSL growth' : 'Oslo pct. growth',
    'STO growth' : 'Stockholm pct. growth',
    'HEL growth' : 'Helsinki pct. growth'
    },
    inplace=True)

    return(df, df_scandinavia)

#@st.cache_data(ttl=3600)
def create_tourmis_table(y1, y2, y3, country_list_for_tourmis, country_translation_dict, latest_month, latest_year):
    username, password = prepare_log_in_info()
    market_dict = build_market_dict(username, password)
    city_dict = build_city_dict(username, password)
    country_string = modify_country_list_for_tourmis(country_list_for_tourmis, market_dict)
    raw_df = collect_main_data(city_dict, username, password, y1, y2, y3, country_string)
    clean_df, df_scandinavia = clean_data(raw_df, country_translation_dict, market_dict, y1, y2, y3, latest_month, latest_year)
    return(clean_df, df_scandinavia)