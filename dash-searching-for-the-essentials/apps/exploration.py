"""
Exploration Viz Card
Author: Information First, Esme Middaugh, emiddaugh@info-first.com
Last Updated: 30SEP2020
"""

import os
from datetime import datetime, timedelta
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

from app import app, INPUT_DIR

try:
    ###########################
    # READ IN DATA
    ###########################
    # Replace this section with reading in data from INPUT_DIR
    active_df = pd.read_csv(INPUT_DIR + "active.csv")

    ###########################
    # PREP
    ###########################
    # Any sort of data processing or creation of graph figures that are too bulky to easily go into the layout inline
    test_func = []
    unique_to_record = ["uri", "title", "classification", "date_registered"]
    generated_ids=[]

    for col in active_df.columns:
        if col not in unique_to_record:
            generated_id = f"userfilter_{col}"
            generated_ids.append(generated_id)
            test_func.append(
                html.Div(
                    children=[
                        html.H4(col),
                        dcc.Dropdown(
                            id=generated_id,
                            options=[{'label': x, 'value': x} for x in list(active_df[col].unique())],
                            multi=True
                        )
                    ]
                )

            )

    gen_names = generated_ids.copy()
    ###########################
    # LAYOUT TO BE USED IN INDEX.PY
    ###########################
    layout = html.Div(
        className="viz-card viz-card--exploration",
        children=[
            html.H4(
                className="viz-card__header viz-card__header--template",
                children="Explore Your Content Manager Dataset"
            ),
            html.P(
                id="exploration_output"
            ),
            html.P(
                className="viz-card__explainer viz-card__explainer--template",
                children="Select a option for your y and x axis below. Additionally, add a 'facet' variable to facet your data"
            ),
            html.Div(
                # Because of a bug in the dash system, need a wrapper div
                className="viz-card__controller viz-card__controller--exploration",
                children=[
                    dcc.RadioItems(
                        id="exploration_type_dropdown",
                        options=[{'label': 'Line', 'value': 'Line'},
                                 {'label': 'Bar', 'value': 'Bar'},
                        ]
                    )
                ]
            ),

            html.Div(
                className="row align-center",
                children=[
                    html.Div(
                        # Because of a bug in the dash system, need a wrapper div
                        className="viz-card__controller viz-card__controller--exploration",
                        children=[
                            'Filter',
                            dcc.Dropdown(
                                id="exploration_filter_dropdown",
                                options=[{'label': x, 'value': x} for x in active_df.columns]
                            )
                        ]
                    ),
                    html.Div(
                        # Because of a bug in the dash system, need a wrapper div
                        className="viz-card__controller viz-card__controller--exploration",
                        children=[
                            'X Axis',
                            dcc.Dropdown(
                                id="exploration_xaxis_dropdown",
                                options=[{'label': x, 'value': x} for x in active_df.columns]
                            )
                        ]
                    ),
                    html.Div(
                        # Because of a bug in the dash system, need a wrapper div
                        className="viz-card__controller viz-card__controller--exploration",
                        children=[
                            'Y Axis',
                            dcc.Dropdown(
                                id="exploration_yaxis_dropdown",
                                options=[{'label': x, 'value': x} for x in active_df.columns],
                            )
                        ]
                    ),
                    html.Div(
                        # Because of a bug in the dash system, need a wrapper div
                        className="viz-card__controller viz-card__controller--exploration",
                        children=[
                            "Facet",
                            dcc.Dropdown(
                                id="exploration_facet_dropdown",
                                options=[{'label': x, 'value': x} for x in active_df.columns]
                            )
                        ]
                    )
                ]
            ),
            html.Button(
                id="exploration_submit_button",
                n_clicks=0,
                children="Show Me the Graph"
            ),
            dcc.Graph(
                id="exploration_graph",
                className="viz-card__graph viz-card__graph--template"
            ),
            html.Div(
                children=test_func
            )
        ]
    )

    ###########################
    # CALLBACK FUNCTIONS, IF ANY
    ###########################
    # @app.callback(Output('exploration_graph', 'figure'),
    #               [Input('exploration_xaxis_dropdown', 'value'),
    #                Input('exploration_yaxis_dropdown', 'value'),
    #                Input('exploration_facet_dropdown', 'value')],
    #               [State('exploration_submit_button', 'n_clicks')],
    #               prevent_initial_call=True) # prevent_initial_call=True
    # def exploration_graph(x, y, facet, n_clicks):
    #     """Allow the user to explore their full CM Dataset Present in active.css"""
    #
    #     if x and not facet:
    #         exploration_fig = px.histogram(active_df, x=[x] )
    #     if x and facet:
    #         exploration_fig = px.histogram(active_df, x=[x], facet_col=facet )
    #
    #     # TODO: If y is set and x is not, do a normal bar chart and swap x and y
    #
    #     return exploration_fig


    @app.callback(Output('exploration_output', 'children'),
                  [Input(x, 'value') for x in generated_ids],
                  prevent_initial_call=True)
    def exploration_graph(*generated_ids):
        print(generated_ids)
        #
        # if generated_ids[0]:
        #     # Get the column that is being filtered from the generated id and set equal to the user selection
        #     active_df_filtered = active_df[generated_ids[0].split('_')[-1] == ]
        ctx = dash.callback_context
        user_selections = {}

        # Find the column and the column filter that the user has selected
        filtered_col = ctx.triggered[0]['prop_id'].split('.')[0][11:] # removing userfiltered_
        filtered_val = ctx.triggered[0]['value']
        user_selections[filtered_col] = filtered_val



        # Take your User Selection and Filter the DataFrame
        filtered_active_df = active_df.copy()
        for key, value in user_selections.items():
            if value:
                filtered_active_df = filtered_active_df[filtered_active_df[key].isin(value)]
            print(f"key: {key} value: {value}")


        return dcc.Graph(
            figure=px.histogram(filtered_active_df, x="date_registered")
        )
    # def exploration_graphs(*args):
    #     saved_args = locals()
    #     print(saved_args)
    #
    # exploration_graphs(*generated_ids)

except Exception as e:
    layout = html.H3(f"Problem loading {os.path.basename(__file__)}, please check console for details.")
    # TO DO: Update with logging.
    print(e)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)