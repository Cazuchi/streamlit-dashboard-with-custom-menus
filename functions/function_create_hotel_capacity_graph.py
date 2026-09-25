import plotly.express as px
import pandas as pd

def create_hotel_capacity_graph(df):
    # 2. Create the scatter plot

    df['score_bracket'] = pd.cut(
        df['Belægningsgrad'],
        bins=[0.0, 0.5, 0.6, 0.8, 0.9, 1.0],
        labels=[
            '0–50%',
            '50–60%',
            '60–80%',
            '80–90%',
            '90–100%',
        ],
        include_lowest=True,
    )

    # Custom 10-step palette: Blue -> Light Center -> Green
    blue_to_green_colors = [
        '#6F5000',
        '#DD9F00',
        '#FFFFFF',
        '#3EBA64',
        '#1F5D32'
    ]

    fig = px.scatter(
        df,
        x='x_labels',
        y='Hotelkapacitet',
        title=None,
        color='score_bracket',
        color_discrete_sequence=blue_to_green_colors,
        category_orders={
            'x_labels': df['x_labels'].unique().tolist(),
            'score_bracket': [
                '0–50%',
                '50–60%',
                '60–80%',
                '80–90%',
                '90–100%',
            ],
        },
        height=800,
    )

    # 3. Optional: Customize layout/styling
    fig.update_layout(
        xaxis_title=None,
        yaxis_title='Hotelkapacitet (værelser)',
        template='plotly_white',
        legend=dict(
            orientation='h',     # Horizontal layout
            yanchor='top',
            y=-0.1,              # Positioned just below the x-axis (adjust if needed)
            xanchor='center',
            x=0.5,               # Horizontally centered
            title_text='Belægningsgrad'
        )
    )

    fig.update_traces(
        marker=dict(
            size=12,
            line=dict(width=1, color='black')  # <-- Adds a thin black border
        ))

    fig.update_coloraxes(colorbar_tickformat='.0%')

    fig.update_yaxes(dtick=1000)

    unique_x = df['x_labels'].unique().tolist()
    tick_texts = [val if i % 2 == 0 else '' for i, val in enumerate(unique_x)]

    fig.update_xaxes(
        range=[-1, len(unique_x) + 0],
        tickangle=-45, # Optional: angles timestamps if they overlap,
        tickmode='array',
        tickvals=unique_x,
        ticktext=tick_texts
    )

    # 4. Display the chart
    return fig