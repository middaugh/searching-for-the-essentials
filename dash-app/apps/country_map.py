"""
Food Map Interaction Block

Esme Middaugh
December 7, 2020

"""

import os
from datetime import datetime
import pandas as pd
import numpy as np


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
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
    trends_df["orig_score_diff"] = trends_df["score_difference"]
    trends_df['date_str'] = trends_df['date'].astype(str)

    # World Health Organization Covid Data
    who_trends_df = pd.read_csv(INPUT_DIR + 'data_who_clean.csv', )
    who_trends_df["date"] = pd.to_datetime(who_trends_df.Date_reported, format="%d/%m/%Y")

    # Start in January when WHO COVID data is starting
    trends_df = trends_df[trends_df["date"] >= who_trends_df["date"].min()]


    ###########################
    # PREP
    ###########################
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
         line_shape="spline",
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
            html.H4("COVID-19 Infection Rate"),
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
        
        # Polar Header
        polar_header = f"Comparative Search Trends for {' & '.join([abbr_dict[x] for x in selected_country])}"

        # Make Polar Chart
        polar_fig = px.line_polar(
            selected_country_df,
            r="score_difference",
            theta="renamed_term",
            color="display_country",
            category_orders={'country': ['ger', 'nl', 'uk']},
            line_close=True,
            line_shape="spline",
            range_r=[min(trends_df["orig_score_diff"]), max(trends_df["orig_score_diff"])],
            render_mode="auto",
            animation_frame="date_str",
            width=600,
            height=600,
            labels={"date_str": "Date ",
                    "country": "Country ",
                    "renamed_term": "Term ",
                    "score_difference": 'Search term popularity value'},
        )
        polar_fig.update_layout(
            margin=dict(t=25, l=25, r=25, b=25, pad=10),
            legend_title_text='',
            # legend_font_size=12,
            legend=dict(orientation="h",
                        yanchor="bottom",
                        xanchor="left",
                        y=-0.15
                        )
        )

        # Facet Plot
        selected_country_df_agg = selected_country_df.groupby(["date", "display_term"], as_index=False).mean()
        selected_country_df["orig_score_diff"] = selected_country_df["orig_score_diff"].astype(float)
        facet_fig = px.line(selected_country_df_agg,
                            x='date', y='orig_score_diff',
                            hover_data={
                                "display_term": True,
                                "date": True,
                                "orig_score_diff": True,
                            },
                            facet_col='display_term',
                            facet_col_wrap=3)
        facet_fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        facet_fig.update_yaxes(title=None, showticklabels=False)
        facet_fig.update_xaxes(title=None)
        facet_fig.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>%{x}<br>Score Difference from Previous Year: %{y:0f}<extra></extra>",
            line_color = "#a0a0a0"
        )
        # print("plotly express hovertemplate:", facet_fig.data[0].hovertemplate)

        return polar_header, polar_fig, facet_fig


except Exception as e:
    layout = html.H3(f"Problem loading {os.path.basename(__file__)}, please check console for details.")
    # TO DO: Update with logging.
    print(e)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)
