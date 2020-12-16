"""
Food Map Interaction Block

Esme Middaugh
December 7, 2020

"""

import os
from datetime import datetime
import pandas as pd
import numpy as np
import glob
import re

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from plotly.colors import n_colors

from app import app, INPUT_DIR

try:
    ###########################
    # READ IN DATA
    ###########################
    parse_dates = ['date']  # need the correct format
    trends_df = pd.read_csv(INPUT_DIR + 'google-trends-difference.csv', parse_dates=parse_dates)

    ###########################
    # PREP
    ###########################
    timeseries_update_layout_range_selector = dict(
        # title_text='Records Ingested by Day',
        margin=dict(l=75, r=40, b=40, t=75, pad=4),
        clickmode='event+select',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )

    )

    # *** Time Series Figure Creation
    timeseries_fig = go.Figure()
    # Cumulative Registered
    timeseries_fig.add_trace(go.Scatter(x=trends_df['date'],
                                         y=trends_df['score_difference'],
                                         name="Cumulative",
                                         line_color='lightgrey', line=dict(shape="spline")))

    timeseries_fig.update_layout(
        **timeseries_update_layout_range_selector,
        legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    # *** End Time Series Figure

    ## GENERATE ICONS
    ICON_DIR = './assets/icons/'
    icons = glob.glob(ICON_DIR + '*.svg')

    icon_ids = []
    icons = np.array(icons).reshape((3, -1))
    icon_layout = []

    for row in icons:
        row_children = []
        for icon in row:
            name_stripped = re.sub(r'\d+', '', icon.split('/')[-1][:-4]) # extract the main product name from the path, removing numbers and .svg
            button = html.Button(
                id=f"{name_stripped}-button",
                className="nav__link nav__link--current",
                children=
                    html.Img(
                        src=icon,
                        className="icon"
                    )
            )
            row_children.append(button)
            icon_ids.append(f"{name_stripped}-button")

        row_layout = html.Div(
            className="row centered",
            children=row_children
        )

        print(row_layout)
        icon_layout.append(row_layout)



    # Placeholder Joy Map
    np.random.seed(1)

    # 12 sets of normal distributed random data, with increasing mean and standard deviation
    data = (np.linspace(1, 2, 12)[:, np.newaxis] * np.random.randn(12, 200) +
            (np.arange(12) + 2 * np.random.random(12))[:, np.newaxis])

    colors = n_colors('rgb(5, 200, 200)', 'rgb(200, 10, 10)', 12, colortype='rgb')

    joy_fig = go.Figure()
    for data_line, color in zip(data, colors):
        joy_fig.add_trace(go.Violin(x=data_line, line_color=color))

    joy_fig.update_traces(orientation='h', side='positive', width=3, points=False)
    joy_fig.update_layout(xaxis_showgrid=False, xaxis_zeroline=False, showlegend=False)

    ###########################
    # LAYOUT TO BE USED IN INDEX.PY
    ###########################
    layout = html.Div(
        className="viz-card viz-card--timeseries flex-one",
        children=[
            dcc.Store(id="timeseries_output"),

            html.H4("Step 1: Select an Icon",
                    className="viz-card__header viz-card__header--timeseries"),
            *icon_layout,
            html.Div(id="test-output"),

            html.H4("Step 2: Map",
                    className="viz-card__header viz-card__header--timeseries"),
            html.Div(
                className="row mobile-interaction-disabled",
                children=[
                    dcc.Graph(id="timeseries_graph",
                              className='viz-card__graph viz-card__graph--timeseries flex-three',
                              figure=timeseries_fig
                              ),
                    html.Div(
                        className="viz-card__controller viz-card__controller--timeseries flex-one",
                        children=[
                            html.H4(className="viz-card__header viz-card__header--timeseries", children="In Depth Info"),
                            dcc.Graph(id="joy_graph",
                                      className='viz-card__graph viz-card__graph--timeseries flex-two',
                                      figure=joy_fig)
                        ]
                    )

                ]
            )

        ])

    ###########################
    # CALLBACK FUNCTIONS, IF ANY
    ###########################
    # Time Series and Record Types

    ## Create the callbacks in a loop
    @app.callback(
        Output(component_id='test-output', component_property='children'),
        [Input('baking-button', 'n_clicks')])
    def update_output_div(input_value):
        print(input_value)
        print(icon_ids)
        return 'Output: {}'.format(input_value)

except Exception as e:
    layout = html.H3(f"Problem loading {os.path.basename(__file__)}, please check console for details.")
    # TO DO: Update with logging.
    print(e)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)



