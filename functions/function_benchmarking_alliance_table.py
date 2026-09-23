import streamlit as st
import pandas as pd

def create_benchmarking_alliance_table(df):
    df = df[['Unnamed: 0', 'Unnamed: 10']]
    df = df[30:396]
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])
    df.reset_index(inplace = True, drop = True)
    df.rename(columns = {'Date' : 'Datetime', 'TY' : 'Occupancy'}, inplace = True)

    def get_month(row):
        return(row.month)

    def get_day(row):
        return(row.day)

    df['Month'], df['Day'] = df['Datetime'].apply(get_month), df['Datetime'].apply(get_day)
    min_date = df['Datetime'].min()
    min_date = min_date.date()
    max_date = df['Datetime'].max()
    max_date = max_date.date()
    df = df.pivot(index = 'Month', columns = 'Day', values = 'Occupancy')

    # Step 1: Clean up the DataFrame structure (don't multiply by 100 yet!)
    df_clean = df.reset_index()

    # ADD THIS: Monthly averages column
    numeric_cols = [col for col in df_clean.columns if col not in ['Month']]
    df_clean['Gns.'] = df_clean[numeric_cols].mean(axis=1)

    # Map month numbers to names
    month_mapping = {1: 'Jan.', 2: 'Feb.', 3: 'Mar.', 4: 'Apr.', 5: 'Maj', 6: 'Jun.',
                    7: 'Jul.', 8: 'Aug.', 9: 'Sep.', 10: 'Okt.', 11: 'Nov.', 12: 'Dec.'}

    df_clean['Month'] = df_clean.iloc[:, 0].map(month_mapping)

    # Step 2: Define color function that works with decimal values
    def color_cells(val):
        if pd.isna(val):
            return 'background-color: white; color: white'
        
        # Convert decimal to percentage for comparison
        pct = val * 100
        
        if pct < 50:
            return 'background-color: #6F5000; color: white'  # Red
        elif 50 <= pct < 60:
            return 'background-color: #DD9F00; color: white'  # Light red  
        elif 60 <= pct <= 80:
            return 'background-color: white; color: black'     # White
        elif 80 < pct <= 90:
            return 'background-color: #3EBA64; color: white'  # Light blue
        else:  # > 90
            return 'background-color: #1F5D32; color: white'  # Green

    # Step 3: Apply styling with percentage format
    numeric_cols = [col for col in df_clean.columns if col not in ['Month']]
    styled_df = df_clean.style.map(color_cells, subset=numeric_cols)

    # Format as percentages for display
    styled_df = styled_df.format({col: '{:.0%}' for col in numeric_cols})

    # Style the headers and Month column
    styled_df = styled_df.set_table_styles([
        {'selector': 'thead th:not(:first-child)', 'props': [ #FORMAT THE COLUMN HEADERS
            ('background-color', 'white'), 
            ('color', 'black'), 
            ('border', '1px solid black'),
            ('padding', '2px'),
            ('text-align', 'center')
        ]},
        {'selector': 'thead th:first-child', 'props': [ #FORMAT THE FIRST and 33rd COLUMN HEADER ONLY
            ('background-color', 'white'), 
            ('color', 'white'),  # Make text white (invisible)
            ('border', '1px solid black'),
            ('padding', '2px')
        ]},
        {'selector': 'tbody td', 'props': [
            ('border', '1px solid black'),
            ('padding', '2px')
        ]},
        {'selector': 'tbody td:first-child', 'props': [ #FORMAT THE MONTH COLUMN
            ('background-color', 'white'),  # Light gray background
            ('color', 'black'),
            ('font-weight', 'bold'),
            ('text-align', 'left'),
            ('padding-left', '10px')  # More left padding
        ]},
        {'selector': 'table', 'props': [
            ('border-collapse', 'collapse'),
            ('border', '1px solid black'),
            ('margin', '20px'),  # Add margin around the entire table
            ('width', 'auto'),  # Center the table
            ('font-family', 'Arial, sans-serif'),  # Better font
            ('box-shadow', '0 4px 8px rgba(0,0,0,0.1)')  # Drop shadow
        ]}
    ])

    # Style the Month column specifically
    styled_df = styled_df.map(lambda x: 'background-color: white; color: black; font-weight: bold', subset=['Month'])

    # Add this line to hide the index:
    styled_df = styled_df.hide(axis='index')
    return(styled_df, min_date, max_date)