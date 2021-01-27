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
    trends_df = pd.read_csv(INPUT_DIR + 'google-trends-difference-terms-ordered.csv', parse_dates=parse_dates)
    trends_df = trends_df[trends_df.score_difference.notna()]
    trends_df["score_difference"] = trends_df["score_difference"].astype("int")
    trends_df['date_str'] = trends_df['date'].astype(str)

    # World Health Organization Covid Data
    who_trends_df = pd.read_csv(INPUT_DIR + 'data_who_clean.csv', )
    who_trends_df["date"] = pd.to_datetime(who_trends_df.Date_reported, format="%d/%m/%Y")

    ###########################
    # PREP
    ###########################

    np.random.seed(1)

    # # Renaming terms for improved labeling:
    # old_terms = ['baking','bananabread','beans','coffee','cooking','facemask','grocerydelivery','hand-sanitizer','pasta',
    #         'restaurant','rice','spices','takeaway','to-go','toiletpaper']
    # new_terms = ['baking','banana bread','beans','coffee','cooking','face mask','grocery delivery','hand sanitizer','pasta',
    #         'restaurant','rice','spices','take away','to go','toiletpaper']
    # new_terms = old_terms
    #
    # def rename_terms(data):
    #     for i in range(0,len(old_terms)):
    #         for index, row in data.iterrows():
    #             if row['term'] == old_terms[i]:
    #                 data.loc[index,'renamed_term'] = new_terms[i]
    #     return data
    #
    # trends_df = rename_terms(trends_df)

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
    trends_df["renamed_term"] = trends_df["display_term"]

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

    trends_df = add_location(trends_df)

    if os.name == 'nt':
        ICON_DIR = os.getcwd() + '\\dash-app\\assets\\icons\\'  # for windows users
    else:
        ICON_DIR = './assets/icons/'

    icons = []
    for name in os.listdir(ICON_DIR):
        if name.endswith(".svg"):
            icons.append(ICON_DIR + name)


    who_linefig = px.line(who_trends_df,
         x="date",
         y="Nom_new_cases", 
         color="Country", 
         hover_name="Country",
         labels={"Nom_new_cases":"COVID-19 Cases per 100.000 Inhabitants",
                    "date":""},
    )

    who_linefig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    ###########################
    # LAYOUT TO BE USED IN INDEX.PY
    ###########################
    layout = html.Div(
        className="viz-card viz-card--country centered flex-one",
        children=[
            html.H4("Select a Country",
                    className="viz-card__header viz-card__header--timeseries"),
            html.Div(
                # Because of a bug in the dash system, need a wrapper div
                className="viz-card__controller viz-card__controller--template",
                children=[
                    dcc.Dropdown(
                        id='country-dropdown',
                        options=[
                            {'label': 'Germany', 'value': 'ger'},
                            {'label': 'The United Kingdom', 'value': 'uk'},
                            {'label': 'The Netherlands', 'value': 'nl'}
                        ],
                        value=['ger', 'uk', 'nl'],
                        multi=True,
                        clearable=False,
                        searchable=False
                    )
                ]
            ),
            html.H4(id="polar-title"),
            html.Div(
                className="row flex",
                children=[
                    dcc.Graph(
                        id="polar-chart",
                        className="centered flex-one"
                    ),
                    dcc.Graph(id="joy-graph",
                              className='viz-card__graph viz-card__graph--timeseries flex-one')
                ]
            ),
            html.H4("\nCOVID-19 Cases per Country"),
            html.Div(
                className="viz-card__header viz-card__header--timeseries",
                # className="viz-card flex-one",
                children=[
                    dcc.Graph(
                        figure=who_linefig
                    )
                ]
            )
        ]
    )

    ###########################
    # CALLBACK FUNCTIONS, IF ANY
    ###########################
    @app.callback(
        [Output('polar-title', 'children'),
         Output('polar-chart', 'figure'),
         Output('joy-graph', 'figure')],
        [Input("country-dropdown", 'value')])
    def map_clicked(selected_country):
        # H3 Header
        abbr_dict = {
            'ger': 'Germany',
            'uk': 'the United Kingdom',
            'nl': 'the Netherlands',
        }

        if type(selected_country) != list: # want a standard input format regardless of number items selected by user
            selected_country = [selected_country]

        # Filter By Selected Country
        selected_country_df = trends_df[trends_df['country'].isin(selected_country)]
        selected_country_df['display_country'] = selected_country_df['country'].map(abbr_dict)

        selected_country_df_ger = selected_country_df[selected_country_df["country"]=="ger"]
        selected_country_df_nl = selected_country_df[selected_country_df["country"]=="nl"]
        selected_country_df_uk = selected_country_df[selected_country_df["country"]=="nl"]
        
        # Polar Header
        polar_header = f"Comparative Search Trends for {' & '.join([abbr_dict[x] for x in selected_country])}"

        # Make Polar Chart
        polar_fig = px.line_polar(
            selected_country_df,
            r="score_difference",
            theta="renamed_term",
            color="display_country",
            category_orders={'country':['ger','nl','uk']},
            #color_discrete_map={'country':['#17becf','#ff7f0e','#7f7f7f']}, # TODO: has to be edited
            line_close=True,
            line_shape="spline",
            range_r=[min(trends_df["score_difference"]), max(trends_df["score_difference"])],
            render_mode="auto",
            animation_frame="date_str",
            width=600,
            height=600,
            labels={"date_str":"Date ",
                    "country":"Country ",
                    "renamed_term":"Term ",
                    "score_difference":'Search term popularity value'},
        )
        # polar_fig = go.Figure()
        # polar_fig.add_trace(go.Scatterpolar(
        #     r=selected_country_df_ger['selected_country'],
        #     theta=selected_country_df_ger['renamed_term'],
        #     mode='lines',
        #     name='Germany',
        #     line_color='orange',
        #     line_close=True,
        #     line_shape="spline",
        #     range_r=[min(trends_df["score_difference"]), max(trends_df["score_difference"])],
        #     render_mode="auto",
        #     animation_frame="date_str",
        #     width=600,
        #     height=600,
        #     labels={"date_str": "Date ",
        #             "country": "Country ",
        #             "renamed_term": "Term ",
        #             "score_difference": 'Search term popularity value'},
        # )
        # )
        polar_fig.update_layout(
            margin=dict(t=25, l=25, r=25, b=25, pad=10),
            legend_title_text='',
            #legend_font_size=12,
            legend=dict(orientation="h",
                        yanchor="bottom",
                        xanchor="left",
                        y=-0.15
                        )
        )

        # JOY MAP
        num_categories = selected_country_df.renamed_term.nunique()
        colors = n_colors('rgb(5, 200, 200)', 'rgb(200, 10, 10)', num_categories, colortype='rgb')
        joy_fig = go.Figure()

        # TODO: modify so that its zipping together trends_df filtered on item type for each color
        for renamed_term, color in zip(trends_df.renamed_term.unique(), colors):
            joy_filtered_data = selected_country_df[selected_country_df.renamed_term == renamed_term]  # show one term at a time
            joy_fig.add_trace(go.Violin(x=joy_filtered_data["score_difference"],
                                        line_color=color,
                                        name=renamed_term,
                                        customdata=["date_str"],
                                        hoverinfo="skip"
                                        )
                              )
        joy_fig.update_traces(orientation='h', side='positive', width=3, points=False)
        joy_fig.update_layout(xaxis_showgrid=False, xaxis_zeroline=False, showlegend=False)
        joy_fig.update_xaxes(showticklabels=False)

        return polar_header, polar_fig, joy_fig


except Exception as e:
    layout = html.H3(f"Problem loading {os.path.basename(__file__)}, please check console for details.")
    # TO DO: Update with logging.
    print(e)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)
