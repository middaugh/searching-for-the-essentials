"""
Food Map Interaction Block

Esme Middaugh
December 7, 2020

"""

import os
from datetime import datetime
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
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
    trends_df = trends_df.sort_values(by="date_str", axis=0)

    abbr_dict = {
        'ger': 'Germany',
        'uk': 'the United Kingdom',
        'nl': 'the Netherlands',
    }
    trends_df['display_country'] = trends_df['country'].map(abbr_dict)

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

    #Test for WHO
    who_fig = px.bar(who_trends_df,
                x="Country", 
                y="Nom_new_cases",
                hover_name="Country",
                labels={
                    "Nom_new_cases":"Cases per 100000 inhabitants",
                    "Country":"Country"},
    )

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

            html.H4(id="food_map_header",
                    className="viz-card__header viz-card__header--timeseries"
                    ),
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
                    dcc.Slider(
                        id='my-slider',
                        min=0,
                        max=20,
                        step=0.5,
                        value=10,
                    ),
                    html.Div(id='slider-output-container')
                ]
            )
        ])
    ###########################
    # CALLBACK FUNCTIONS, IF ANY
    ###########################
    # Time Series and Record Types

    ## Create the callbacks in a loop
    @app.callback(
         [Output("test_map", "figure"),
          Output("food_map_header", "children")],
        [Input(x, 'n_clicks') for x in icon_ids])
    def update_output_div(*icon_ids):
        ctx = dash.callback_context
        if not ctx.triggered:
            button_id = 'toiletpaper-button'
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        search_term = button_id[:-7]
        
        # Human Readable Formating
        display_terms = {'baking': 'baking',
                        'bananabread': 'banana bread',
                        'beans': 'beans' ,
                        'coffee': 'coffee' ,
                        'cooking': 'cooking',
                        'facemask': 'face mask',
                        'grocerydelivery': 'grocery delivery',
                        'hand-sanitizer': 'hand sanitizer',
                        'pasta': 'pasta',
                        'restaurant': 'restaurant',
                        'rice': 'rice',
                        'spices': 'spices',
                        'takeaway': 'takeaway',
                        'to-go': 'to go',
                        'toiletpaper': 'toilet paper'
                         }

        # Header to display based on selected item
        header = f"Search Trend Popularity & WHO COVID-19 Cases for {display_terms[search_term].capitalize()}"

        # Attempt to generate map
        filtered_data = trends_df[trends_df.term == search_term]

        transformed_data = transform_data(filtered_data)
        transformed_data = transformed_data.sort_values(by="date_str", axis=0)
        color_discrete_map = {"positive": "#419D78", "negative": "#DE6449"}
        test_fig = px.scatter_geo(transformed_data,
                                  locations="iso_alpha",
                                  color="score_diff_positive",
                                  color_discrete_map=color_discrete_map,
                                  hover_name="country",
                                  size="score_difference",
                                  size_max=50,
                                  animation_frame="date_str",  # has to be edited
                                  projection="conic conformal", # for Europe: conic conformal OR azimuthal equal area
                                  height=600,
                                  hover_data={
                                      "term": True,
                                      "date_str": True,
                                      "display_country": True,
                                      "score_difference": True,
                                      "score_diff_positive": True,
                                      "iso_alpha": False
                                  },
                                  labels={
                                      "score_diff_positive": "Search term popularity compared to previous year ",
                                      "date_str": "Date ",
                                      "display_country": "Country ",
                                      "score_difference": "Search query value ",
                                      "renamed_term": "Term "
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
            )
        )

        test_fig.update_geos(projection_scale=4,  # set value; default = 1 (Europe scale)
                             # set map extent
                             center_lon=4.895168,  # set coordinates of Amsterdam as center of map
                             center_lat=52.370216,
                             # fitbounds= "locations"
                             showland=False,
                             showocean=True,
                             oceancolor="#eee" # try with "#fffff" for white background
                             )


        return test_fig, header


    @app.callback(
        dash.dependencies.Output('slider-output-container', 'children'),
        [dash.dependencies.Input('my-slider', 'value')])
    def update_output(value):
        return 'You have selected "{}"'.format(value)

except Exception as e:
    layout = html.H3(f"Problem loading {os.path.basename(__file__)}, please check console for details.")
    # TO DO: Update with logging.
    print(e)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)



