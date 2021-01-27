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
    trends_df['date_str'] = trends_df['date'].astype(str)
    trends_df = trends_df.sort_values(by="date_str", axis=0)

    display_terms = {'baking': 'baking',
                     'bananabread': 'banana bread',
                     'beans': 'beans',
                     'coffee': 'coffee',
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

    trends_df["display_term"] = trends_df.term.map(display_terms)

    # World Health Organization Covid Data
    who_trends_df = pd.read_csv(INPUT_DIR + 'data_who_clean.csv', )
    who_trends_df["date"] = pd.to_datetime(who_trends_df.Date_reported, format="%d/%m/%Y")

    abbr_dict = {
        'ger': 'Germany',
        'uk': 'the United Kingdom',
        'nl': 'the Netherlands',
    }
    trends_df['display_country'] = trends_df['country'].map(abbr_dict)

    ###########################
    # PREP
    ###########################

    # MAPPING
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


    # SLIDER
    # transform every unique date to a number & only get days that have matching WHO Covid data
    slider_dict = {i: x for i, x in enumerate(trends_df[trends_df["date"].isin(who_trends_df["date"])]["date"].sort_values().unique())}

    slider = dcc.Slider(
        id='map-date-slider',
        min=min(slider_dict.keys()),
        max=max(slider_dict.keys()),
        value=min(slider_dict.keys()),
        marks={key: pd.to_datetime(str(value)).strftime('%d/%m/%y') for key, value in slider_dict.items()},
        included=False,
        updatemode='drag'
    )


    ###########################
    # LAYOUT TO BE USED IN INDEX.PY
    ###########################
    layout = html.Div(
        className="viz-card flex-one",
        children=[
            dcc.Store(id="icon_store"),
            dcc.Store(id="slider_store"),

            html.H4("Select a Search Term",
                    className="viz-card__header viz-card__header--timeseries"),

            *icon_layout, # all 15 icons laid out in three rows

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
                              className='viz-card__graph flex-two'
                              )
                ]
            ),
            html.Div(
                children=[
                    slider
                ]
            )
        ]
    )
    ###########################
    # CALLBACK FUNCTIONS, IF ANY
    ###########################
    # Time Series and Record Types

    ## Create the callbacks in a loop
    callback_inputs = [Input(x, 'n_clicks') for x in icon_ids]
    callback_inputs.append(Input('my-slider', 'value'))

    # Get which icon has been clicked and update the store
    @app.callback(
          Output("icon_store", "data"),
        [Input(x, 'n_clicks') for x in icon_ids])
    def update_output_div(*icon_ids):
        ctx = dash.callback_context
        if not ctx.triggered:
            button_id = 'toiletpaper-button'
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        search_term = button_id[:-7]
        return search_term

    # Update another store with the value of the slider
    @app.callback(
            Output("slider_store", "data"),
            [Input("map-date-slider", "value")])
    def update_from_date_slider(slider_choice):
        date_selected = slider_dict[slider_choice]
        date_selected = pd.to_datetime(str(date_selected)).strftime('%Y-%m-%d') # match the date_str format from transformed_Df
        return date_selected

    @app.callback(
        [Output("test_map", "figure"),
         Output("food_map_header", "children"),
         Output("who_fig", "figure")],
        [Input("icon_store", "data"),
         Input("slider_store", "data")])
    def update_from_store(search_term, date_selected):
        ### Prep
        # Limit to selected term and date
        filtered_data = trends_df[(trends_df.term == search_term) & (trends_df.date_str == date_selected)]
        transformed_data = transform_data(filtered_data)
        transformed_data["choropleth"] = "grey"

        ### Map
        color_discrete_map = {"positive": "#419D78", "negative": "#DE6449"}
        map_fig = px.scatter_geo(
            transformed_data,
            locations="iso_alpha",
            color="score_diff_positive",
            color_discrete_map=color_discrete_map,
            hover_name="country",
            size="score_difference",
            size_max=50,
            projection="conic conformal",  # for Europe: conic conformal OR azimuthal equal area
            height=600,
            hover_data={
              "display_term": True,
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

        map_fig_choropleth = px.choropleth(
                            transformed_data,
                                locations="iso_alpha",
                                color="choropleth",  # lifeExp is a column of gapminder
                                hover_name=None,  # column to add to hover information
                                hover_data={
                                    "display_term": True,
                                    "date_str": True,
                                    "display_country": True,
                                    "score_difference": True,
                                    "score_diff_positive": True,
                                    "iso_alpha": False
                                },
                                color_discrete_map={
                                    "grey": "#CECECE"
                                }
                            )


        # Add background color to map & ensure it doesn't show up in legend
        map_fig_choropleth.update_traces(name='background_color', showlegend=True)
        map_fig.add_trace(map_fig_choropleth.data[0])

        map_fig.for_each_trace(
            lambda trace: trace.update(showlegend=False) if trace.name == "background_color" else (),
        )

        map_fig.update_layout(
            geo_scope="europe",
            legend_title_text='Search Term Popularity Compared to Previous Year',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            margin=dict(l=0, r=0, t=0, b=0),
        )


        map_fig.update_geos(
            projection_scale=4,  # set value; default = 1 (Europe scale)
            # set map extent
            center_lon=4.895168,  # set coordinates of Amsterdam as center of map
            center_lat=52.370216,
            # fitbounds= "locations"
            showland=False,
            showocean=True,
            oceancolor="#eee",  # try with "#fffff" for white background
            countrycolor="#aaa" # outline of countries
        )

        map_fig.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>Date: %{customdata[1]}<br>Country: %{customdata[2]}<br>Score Difference: %{customdata[3]}<extra></extra>",
            # print("plotly express hovertemplate:", disposed_lifecycle_fig.data[0].hovertemplate)
        )

        ### Header
        header = f"Search Trend Popularity for {display_terms[search_term].capitalize()} and average COVID-19 Rate for Germany, the Netherlands, and the UK"

        ### WHO Bar Graph
        date_selected_datetime = pd.to_datetime(date_selected)

        # WHO Line Fig with Vertical Line
        who_fig = px.line(who_trends_df,
                              x="date",
                              y="Nom_new_cases",
                              color="Country",
                              hover_name="Country",
                              line_shape="spline",
                              labels={"Nom_new_cases": "Cases per 100.000 inhabitants",
                                      "date": ""},
                              )
        who_fig.add_vline(x=date_selected_datetime, line_color="#f0f0f0", line_dash="dash")
        who_fig.update_xaxes(title_text=None)
        who_fig.update_layout(
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        return map_fig, header, who_fig

except Exception as e:
    layout = html.H3(f"Problem loading {os.path.basename(__file__)}, please check console for details.")
    # TO DO: Update with logging.
    print(e)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)
