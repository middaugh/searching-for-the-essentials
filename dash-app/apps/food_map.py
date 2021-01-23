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
    who_trends_df = pd.read_csv(INPUT_DIR + 'data_who_clean.csv', )
    trends_df['date_str'] = trends_df['date'].astype(str)

    ###########################
    # PREP FOR MAPPING
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

    #Test for WHO
    who_fig = px.bar(who_trends_df,
                x="Country", 
                y="Nom_new_cases",
                hover_name="Country",
                labels={
                    "Nom_new_cases":"Cases per 100000 inhabitants",
                    "Country":"Country"},
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
    if os.name == 'nt':
        ICON_DIR = os.getcwd() + '\\dash-app\\assets\\icons\\'  # for windows users
    else:
        ICON_DIR = './assets/icons/'

    icons = []
    for name in os.listdir(ICON_DIR):
        if name.endswith(".svg"):
            icons.append(ICON_DIR + name)
    #icons = icons = glob.glob(ICON_DIR + '*.svg')
    icon_ids = []
    icons = np.array(icons).reshape((3, -1))
    icon_layout = []

    for row in icons:
        row_children = []
        for icon in row:
            name_stripped = re.sub(r'\d+', '', icon.split('/')[-1][:-4]) # extract the main product name from the path, removing numbers and .svg
            button = html.Button(
                id=f"{name_stripped}-button",
                className="nav__link striped-bg-dark",
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

    #TODO: modify so that its zipping together trends_df filtered on item type for each color
    for term, color in zip(trends_df.term.unique(), colors):
        filtered_data = trends_df[(trends_df.country == "nl") & (trends_df.term == term)] # keep only one country and one term at a time
        joy_fig.add_trace(go.Violin(x=filtered_data["score_difference"], line_color=color, name=term))
    joy_fig.update_traces(orientation='h', side='positive', width=3, points=False)
    joy_fig.update_layout(xaxis_showgrid=False, xaxis_zeroline=False, showlegend=False)


    ###########################
    # LAYOUT TO BE USED IN INDEX.PY
    ###########################
    layout = html.Div(
        className="viz-card flex-one",
        children=[
            dcc.Store(id="timeseries_output"),

            html.H4("Select a Search Term",
                    className="viz-card__header viz-card__header--timeseries"),
            *icon_layout,

            html.H4("Search Trend Popularity & WHO COVID-19 Cases",
                    className="viz-card__header viz-card__header--timeseries"),
            html.Div(
                className="row mobile-interaction-disabled",
                children=[
                    dcc.Graph(id="test_map",
                              className='viz-card__graph viz-card__graph--timeseries flex-three'
                              ),
                    dcc.Graph(id="who_fig",
                              className='viz-card__graph flex-one',
                              figure=who_fig)
                ]
            ),
            html.Div(
                className="row",
                children=[
                    html.Div(
                        id="test-map-output",
                        className="flex-one"
                    )
                ]
            ),

            html.H3("Extra information", className="text-centered nav__subtitle"),
            html.Div(
                className="nav_container",
                children=[
                    html.Div(
                        className="project-explanation flex-one centered row",
                        children=[
                            # TODO: Update with proper explanation, taken from the project proposal
                            "For displaying the Google Search Trend data in the map, we have used data from November 2018 till November 2020. The first year is the non-covid data, and we compare the second year (Nov 2019-Nov 2020), with the first year (Nov 2018-Nov 2019). In this way the difference between the two years are displayed. The new reported corona cases per day are calculated with the data that is available on the site of the World Health Organisation. To be able to compare the Corona outbreaks per country, we calculated the new reported corona cases per day. Note that the countries had lest test capacity during the first day, therefore the first wave is less accurate than for the second wave. "
                        ]
                    ),
                ]
            )
        ])
    ###########################
    # CALLBACK FUNCTIONS, IF ANY
    ###########################
    # Time Series and Record Types

    ## Create the callbacks in a loop
    @app.callback(
         Output("test_map", "figure"),
        [Input(x, 'n_clicks') for x in icon_ids])
    def update_output_div(*icon_ids):
        ctx = dash.callback_context
        if not ctx.triggered:
            button_id = 'No clicks yet'
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        # Attempt to generate map
        try:
            filtered_data = trends_df[trends_df.term == button_id.split("-")[0]] # test term, should be exchanged
            if len(filtered_data) == 0:
                filtered_data = trends_df[trends_df.term == "restaurant"]  # baseline
        except Exception as e:
            filtered_data = trends_df[trends_df.term == "restaurant"] # baseline
            raise e

        #filtered_data = trends_df[trends_df.term == "restaurant"] # baseline
        transformed_data = transform_data(filtered_data)
        transformed_data["modified_score_difference"] = transformed_data["score_difference"] * 8
        color_discrete_map = {"positive": "#419D78", "negative": "#DE6449"}
        test_fig = px.scatter_geo(transformed_data,
                                  locations="iso_alpha",
                                  color="score_diff_positive",
                                  color_discrete_map=color_discrete_map,
                                  hover_name="country",
                                  hover_data={"country": True, "term": True, "score_difference": True},
                                  size="score_difference",
                                  size_max=50,
                                  animation_frame="date_str",  # has to be edited
                                  projection="conic conformal", # for Europe: conic conformal OR azimuthal equal area
                                  height=600,
                                  labels = {
                                           "score_diff_positive":"Search term popularity compared to previous year ",
                                           "date_str": "Date ",
                                           "iso_alpha":"Country abbreviation ",
                                           "country":"Country ",
                                           "score_difference":"Search query value ",
                                           "term":"Term "
                                     }
                                  )  

        test_fig.update_layout(geo_scope="europe")
        test_fig.update_layout(legend_title_text='Search term popularity compared to previous year')
        test_fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))

        test_fig.update_geos(projection_scale=4,  # set value; default = 1 (Europe scale)
                             # set map extent
                             center_lon=4.895168,  # set coordinates of Amsterdam as center of map
                             center_lat=52.370216,
                             # fitbounds= "locations"
                             showland=False,
                             showocean=True,
                             oceancolor="#eee" # try with "#fffff" for white background
                             )


        return test_fig

    # What user has selected on map
    @app.callback(
        Output('test-map-output', 'children'),
        [Input("test-map", 'relayoutData')])
    def map_clicked(selected_country):
        ctx = dash.callback_context
        if not ctx.triggered:
            return 'BUBBLE'
        return "zoom"

except Exception as e:
    layout = html.H3(f"Problem loading {os.path.basename(__file__)}, please check console for details.")
    # TO DO: Update with logging.
    print(e)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)



