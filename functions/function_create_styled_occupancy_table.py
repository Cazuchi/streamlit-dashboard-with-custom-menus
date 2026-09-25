import pandas as pd

def create_styled_occupancy_table(df):
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
    numeric_cols = [col for col in df.columns if col not in ['tid']]
    styled_df = df.style.map(color_cells, subset=numeric_cols)

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
            ('padding', '2px'), # Drop shadow
            ('min-width', '60px')
        ]},
        {'selector': 'tbody td:first-child', 'props': [ #FORMAT THE MONTH COLUMN
            ('background-color', 'white'),  # Light gray background
            ('color', 'black'),
            ('font-weight', 'bold'),
            ('text-align', 'left'),
            ('padding-left', '10px'),
        ]},
        {'selector': 'table', 'props': [
            ('border-collapse', 'collapse'),
            ('border', '1px solid black'),
            ('margin', '20px'),  # Add margin around the entire table
            ('width', 'auto'),  # Center the table
            ('font-family', 'Arial, sans-serif'),  # Better font
            ('box-shadow', '0 4px 8px rgba(0,0,0,0.1)'),
        ]}
    ])

    # Style the Month column specifically
    styled_df = styled_df.map(lambda x: 'background-color: white; color: black; font-weight: bold', subset=['tid'])

    # Add this line to hide the index:
    styled_df = styled_df.hide(axis='index')
    styled_df = styled_df.set_properties(
        subset=numeric_cols, **{'text-align': 'center'}
    )
    return styled_df