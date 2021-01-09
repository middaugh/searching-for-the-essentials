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
import plotly.express as px

from app import app, INPUT_DIR

try:
    ###########################
    # READ IN DATA
    ###########################
    parse_dates = ['date']  # need the correct format
    trends_df = pd.read_csv(INPUT_DIR + 'google-trends-difference.csv', parse_dates=parse_dates)
    trends_df = trends_df[trends_df.score_difference.notna()]
    trends_df["score_difference"] = trends_df["score_difference"].astype("int")

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
            name_stripped = re.sub(r'\d+', '', icon.split('/')[-1][
                                               :-4])  # extract the main product name from the path, removing numbers and .svg
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
        icon_layout.append(row_layout)

    ## DETAILS JOY MAP --- JUST NETHERLANDS FOR NOW< TODO Turn into Callback
    np.random.seed(1)

    num_categories = len(icon_ids)

    data = (np.linspace(1, 2, num_categories)[:, np.newaxis] * np.random.randn(num_categories, 200) +
            (np.arange(num_categories) + 2 * np.random.random(num_categories))[:, np.newaxis])

    colors = n_colors('rgb(5, 200, 200)', 'rgb(200, 10, 10)', num_categories, colortype='rgb')

    joy_fig = go.Figure()

    # TODO: modify so that its zipping together trends_df filtered on item type for each color

    for term, color in zip(trends_df.term.unique(), colors):
        filtered_data = trends_df[
            (trends_df.country == "nl") & (trends_df.term == term)]  # keep only one country and one term at a time
        joy_fig.add_trace(go.Violin(x=filtered_data["score_difference"], line_color=color, name=term))
    joy_fig.update_traces(orientation='h', side='positive', width=3, points=False)
    joy_fig.update_layout(xaxis_showgrid=False, xaxis_zeroline=False, showlegend=False)


    ###########################
    # FIRST TRY TO CREATE A MAP
    ###########################
    # Adding iso_alpha and iso_num to df to use it as location for creating the map
    def add_location(data):
        for index, row in data.iterrows():
            if row['country'] == "ger":
                data.at[index, 'iso_num'] = 276
                data.at[index, 'iso_alpha'] = "DEU"
            elif row['country'] == "nl":
                data.at[index, 'iso_num'] = 533
                data.at[index, 'iso_alpha'] = "NLD"
            elif row['country'] == "uk":
                data.at[index, 'iso_num'] = 826
                data.at[index, 'iso_alpha'] = "GBR"
        return data


    trends_df = add_location(trends_df)


    # Filter data by search term
    def filter_data(data, term):
        queryable_data = data.copy()
        queryable_data.query('term == "' + term + '"', inplace=True)
        return queryable_data


    # Transform score_difference into absolute values and create additional column "score_diff_positive"
    # To distinguish and use different colors for positive and negative score differences
    def transform_data(data):
        data['date_str'] = data['date'].astype(str)
        for index, row in data.iterrows():
            if row['score_difference'] >= 0:
                data.at[index, 'score_diff_positive'] = "positive"
            else:
                data.at[index, 'score_diff_positive'] = "negative"
            data.at[index, 'score_difference'] = abs(data.at[index, 'score_difference'])
        return data


    filtered_data = filter_data(trends_df, "restaurant")  # test term, should be exchanged
    transformed_data = transform_data(filtered_data)

    test_fig = px.scatter_geo(transformed_data,
                              locations="iso_alpha",
                              color="score_diff_positive",
                              hover_name="country",
                              size="score_difference",
                              # has to be changed to score_difference as soon as values have been transformed to positive values
                              animation_frame="date_str",  # has to be edited
                              projection="conic conformal")  # to represent Europe: conic conformal OR azimuthal equal area;
    # to represent ONLY nl, uk and ger use conic equal area OR azimuthal equal area

    test_fig.update_layout(geo_scope="europe")

    test_fig.update_geos(projection_scale=4,  # set value; default = 1 (Europe scale)
                         # set map extent
                         center_lon=4.895168,  # set coordinates of Amsterdam as center of map
                         center_lat=52.370216,
                         # fitbounds= "locations"
                         showland=False,
                         showocean=True,
                         oceancolor="#eee")


    ###########################
    # LAYOUT TO BE USED IN INDEX.PY
    ###########################
    layout = html.Div(
        className="viz-card viz-card--template",
        children=[
            html.H4("Step 1: Select a Country",
                    className="viz-card__header viz-card__header--timeseries"),
            html.Div(
                # Because of a bug in the dash system, need a wrapper div
                className="viz-card__controller viz-card__controller--template",
                children=[
                    dcc.Dropdown(
                        id='country-dropdown',
                        options=[
                            {'label': 'Germany', 'value': 'ger'},
                            {'label': 'England', 'value': 'uk'},
                            {'label': 'Netherlands', 'value': 'nl'}
                        ],
                        value='ger'
                    )
                ]
            ),
            html.H4("Step 2: Map of All terms for that country over time:"),
            dcc.Graph()

        ]
    )

    ###########################
    # CALLBACK FUNCTIONS, IF ANY
    ###########################

except Exception as e:
    layout = html.H3(f"Problem loading {os.path.basename(__file__)}, please check console for details.")
    # TO DO: Update with logging.
    print(e)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)

