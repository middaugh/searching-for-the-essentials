"""
<<TEMPLATE>> Interaction Block
Author: <<COMPANY>>, <<NAME>>, <<EMAIL>>
Last Updated: <<DATE HERE>>
"""
import os
import pandas as pd

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from colour import Color

from app import app, INPUT_DIR, COLOR_PALETTE_GRADIENT

try:
    ###########################
    # READ IN DATA
    ###########################
    record_owner_df = pd.read_csv(INPUT_DIR + 'record_owner.csv')
    record_classification_df = pd.read_csv(INPUT_DIR + 'record_classification.csv')
    record_owner_classification_df = pd.read_csv(INPUT_DIR + 'record_owner_classification.csv')

    ###########################
    # PREP
    ###########################

    ###########################
    # LAYOUT TO BE USED IN INDEX.PY
    ###########################
    layout = html.Div(
        className="viz-card viz-card--owner_classification flex-one",
        children=[
            html.H4("Record Owners & Classification", className='viz-card__header'),
            html.Div(
                className="flex-container row",
                children=[
                    html.P(
                        className="viz-card__explainer viz-card__explainer--owner_classification flex-two",
                        children="The bar graph on the left shows the record owners, ordered from most records to least. Select a record owner (inner circle) in the sunburst chart at right to view the classification types for that owner, \
                        and reselect that owner to zoom back out. Note that 'Not Set' for a classification type means that no classification was set in Content Manager.",
                    ),
                    # wrap all dcc.Dropdown in Div with className because otherwise not applied to outermost div, https://github.com/plotly/dash-core-components/issues/606
                    html.Div(
                        className="viz-card__controller viz-card__controller--timeseries flex-one",
                        children=[
                            dcc.Dropdown(
                                id="limit_record_owners",
                                className="viz-card__controller viz-card__controller--owner_classification",
                                options=[
                                    {'label': 'Show All', 'value': 'None'},
                                    {'label': 'Top 5', 'value': '5'},
                                    {'label': 'Top 10', 'value': '10'},
                                    {'label': 'Top 15', 'value': '15'},
                                    {'label': 'Bottom 5', 'value': '-5'},
                                    {'label': 'Bottom 10', 'value': '-10'},
                                    {'label': 'Bottom 15', 'value': '-15'},
                                ],
                                placeholder="Limit number of record owners to: "
                            )
                        ]
                    )
                ]
            ),

            # Owner Bar Graph, Classification Drill Down, and Table Section
            html.Div(
                id='owner-section',
                className="flex-container row",
                children=[
                    dcc.Store(id="limit_record_owners_output"),
                    dcc.Graph(
                        id="owner_bar_graph",
                        className="viz-card__graph viz-card__graph--owner_classification-owner-bar-graph"
                    ),
                    dcc.Graph(
                        id="classification_sunburst_graph",
                        className="viz-card__graph"
                    )
                ]
            )

        ]
    )
    ###########################
    # CALLBACK FUNCTIONS, IF ANY
    ###########################
    @app.callback(Output('limit_record_owners_output', 'data'),
                  [Input('limit_record_owners', 'value')])
    def filter_record_owners_data(filter):
        """if filter is None:
            # prevent the None callbacks is important with the store component.
            # you don't want to update the store for nothing.
            raise PreventUpdate"""
        filtered_df = record_owner_df.copy()

        if (filter != "None") and (
                filter is not None):  # user hasn't selected anything, or selected "Show All" from the Dropdown
            rows_to_display = int(filter)
            if rows_to_display > 0:
                filtered_df = filtered_df.nlargest(rows_to_display, columns="count")
            else:
                filtered_df = filtered_df.nsmallest(abs(rows_to_display),
                                                    columns="count")  # abs() because we need a positive number of rows

        return filtered_df['record_owner'].tolist()


    @app.callback([Output('owner_bar_graph', 'figure'),
                   Output('classification_sunburst_graph', 'figure')],
                  [Input('limit_record_owners_output', 'data')])
    def set_owner_graphs(selected_owners):
        """
        Set one or more owner graphs based on the output of limit_record_owners_output.
        Parameters
        ----------
        selected_owners: list
            The owners selected by the user in limit_record_owners dcc.Dropdown() which is then passed to limi_record_owners_output
        Returns
        -------
        bar_fig: px.bar()
            Filtered horizontal bar graph for record owners
        sunburst_fig: px.sunburst()
            Filtered sunburst graph with record_owner as center
        """

        filtered_record_owner_df = record_owner_df[record_owner_df['record_owner'].isin(selected_owners)].sort_values(
            by="count", ascending=False)
        filtered_record_owner_classification_df = record_owner_classification_df[
            record_owner_classification_df['record_owner'].isin(selected_owners)]

        # number of lines
        N = filtered_record_owner_classification_df.record_owner.nunique()  # number of unique record owners that we need colors for

        start_color = COLOR_PALETTE_GRADIENT[0]
        end_color = COLOR_PALETTE_GRADIENT[1]

        # list of "N" colors between "start_color" and "end_color"
        owner_colorscale = [x.hex for x in list(Color(start_color).range_to(Color(end_color), N))]
        ordered_owners = filtered_record_owner_classification_df.groupby("record_owner", as_index=False) \
            .sum() \
            .sort_values(by="count")['record_owner'] \
            .tolist()

        owner_color_dict = dict(zip(ordered_owners, owner_colorscale))
        owner_color_dict["?"] = "black"

        bar_fig = px.bar(filtered_record_owner_df.sort_values(by="count", ascending=False),
                         x="count",
                         y="record_owner",
                         orientation="h",
                         height=650,
                         color="record_owner",
                         color_discrete_map=owner_color_dict
                         )

        bar_fig.update_layout(
            margin=dict(l=300, r=20, b=20, t=60, pad=10),
            showlegend=False,
            uniformtext=dict(minsize=10, mode='show'),
        )
        bar_fig.update_yaxes(title="", tickfont=dict(size=12))
        bar_fig.update_xaxes(title="", automargin=True)
        bar_fig.update_traces(
            go.Bar(
                name=" ",
                hovertemplate="<b>Owner:</b> %{label} <br> <b>Number of Records:</b> %{value} "
            )
        )

        sunburst_fig = px.sunburst(filtered_record_owner_classification_df,
                                   path=['record_owner', 'classification'],
                                   values='count',
                                   color="record_owner",
                                   color_discrete_map=owner_color_dict,
                                   )

        sunburst_fig.update_traces(
            go.Sunburst(
                hovertemplate='<b>Owner: </b> %{parent} <br> <b>Classification: </b> %{label} <br> <b>Count:</b> %{value:,.0f}'),
            insidetextorientation='radial'
        )

        sunburst_fig.update_layout(autosize=True)

        return bar_fig, sunburst_fig


except:
    layout = html.H3(f"Problem loading {os.path.basename(__file__)}, please check console for details.")
    # TO DO: Update with logging.

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)







