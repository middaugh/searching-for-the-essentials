"""
Time Series Interaction Block
Author: Information First, Esme Middaugh, emiddaugh@info-first.com
Last Updated: 2020SEP17
"""

import os
from datetime import datetime
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

from app import app, INPUT_DIR

try:
    ###########################
    # READ IN DATA
    ###########################
    parse_dates = ['date_registered']  # need the correct format
    date_registered_df = pd.read_csv(INPUT_DIR + 'date_registered.csv', parse_dates=parse_dates)
    record_type_date_registered_df = pd.read_csv(INPUT_DIR + 'record_type_date_registered.csv', infer_datetime_format=True, parse_dates=parse_dates)

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
                    dict(count=2,
                         label="2y",
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
    # Count Per Day Bars
    timeseries_fig.add_trace(go.Bar(x=date_registered_df['date_registered'],
                                     y=date_registered_df['count'],
                                     name="Per Day"))
    # Cumulative Registered
    timeseries_fig.add_trace(go.Scatter(x=date_registered_df['date_registered'],
                                         y=date_registered_df['cumulative_count'],
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

    ###########################
    # LAYOUT TO BE USED IN INDEX.PY
    ###########################
    layout = html.Div(
        className="viz-card viz-card--timeseries flex-one",
        children=[
            dcc.Store(id="timeseries_output"),
            html.H4("Active Records: Timeline of Record Registration & Types",
                    className="viz-card__header viz-card__header--timeseries"),
            html.Div(
                className="row",
                children=[
                    html.P(
                        className="viz-card__explainer viz-card_explainer--timeseries flex-two",
                        children="Select a time range (1Y, 6M, etc. or with the slider at bottom of graph)\
                         or an individual date to drill into Record Types. Click a legend item once to hide it, and again to redisplay.\
                         Use the dropdown at right to limit the number of record types displayed (note that this does not affect the registration graph)."
                    ),
                    # wrap all dcc.Dropdown in Div with className because otherwise not applied to outermost div, https://github.com/plotly/dash-core-components/issues/606
                    html.Div(
                        className="viz-card__controller viz-card__controller--timeseries flex-one",
                        children=[
                            dcc.Dropdown(
                                id="limit_record_types",
                                options=[
                                    {'label': 'Show All', 'value': 'None'},
                                    {'label': 'Top 5', 'value': '5'},
                                    {'label': 'Top 10', 'value': '10'},
                                    {'label': 'Top 15', 'value': '15'},
                                    {'label': 'Bottom 5', 'value': '-5'},
                                    {'label': 'Bottom 10', 'value': '-10'},
                                    {'label': 'Bottom 15', 'value': '-15'},

                                ],
                                placeholder="Limit number of record types to: "
                            )
                        ]
                    )
                ]
            ),
            html.Div(
                className="row mobile-interaction-disabled",
                children=[
                    dcc.Graph(id="timeseries_graph",
                              className='viz-card__graph viz-card__graph--timeseries flex-three',
                              figure=timeseries_fig
                              ),
                    dcc.Graph(id="record_type_graph",
                              className='viz-card__graph viz-card__graph--timeseries flex-two')
                ]
            )
        ])

    ###########################
    # CALLBACK FUNCTIONS, IF ANY
    ###########################
    # Time Series and Record Types
    @app.callback(Output('timeseries_output', 'data'),
                  [Input('timeseries_graph', 'relayoutData'),
                   Input('timeseries_graph', 'clickData')])
    def filter_record_types(relayoutData, clickData):
        if relayoutData is None and clickData is None:
            # prevent the None callbacks is important with the store component.
            # you don't want to update the store for nothing.
            raise PreventUpdate

        ctx = dash.callback_context
        triggered_event = ctx.triggered[0]['prop_id'].split('.')[
            1]  # the actual event that is called, eg, relayout or click

        if triggered_event == 'relayoutData':

            ## Starting Value with Everything Selected or , or if 'All' selected from Range SLider
            if 'autosize' in relayoutData.keys() or 'xaxis.autorange' in relayoutData.keys():
                xmin = record_type_date_registered_df['date_registered'].min()
                xmax = record_type_date_registered_df['date_registered'].max()  # return fig

            # Selected via the Range Slider
            elif 'xaxis.range' in relayoutData.keys():
                xrange = relayoutData['xaxis.range']
                xmin = datetime.strptime(xrange[0].split()[0], '%Y-%m-%d')
                xmax = datetime.strptime(xrange[1].split()[0], '%Y-%m-%d')

            # Selected via the graph
            elif "xaxis.range[0]" in relayoutData.keys():
                xmin = datetime.strptime(relayoutData["xaxis.range[0]"].split()[0], '%Y-%m-%d')
                xmax = datetime.strptime(relayoutData["xaxis.range[1]"].split()[0], '%Y-%m-%d')

        # Single point selected from inside the graph
        elif triggered_event == 'clickData':  # first part of split is input ID, eg. timeseries_graph
            x = clickData['points'][0]['x']
            xmin = datetime.strptime(x, '%Y-%m-%d')
            xmax = xmin + timedelta(days=1)

        else:
            xmin = record_type_date_registered_df['date_registered'].min()
            xmax = record_type_date_registered_df['date_registered'].max()

        filtered_df = record_type_date_registered_df[
            record_type_date_registered_df['date_registered'].between(xmin, xmax)]
        agg = filtered_df.groupby('record_type', as_index=False).sum()
        return agg.to_dict('records')

    @app.callback(Output('record_type_graph', 'figure'),
                  [Input('timeseries_output', 'data'),
                   Input('limit_record_types', 'value')])
    def set_record_type_graph(data, limit_record_types):
        if data is None:
            raise PreventUpdate

        agg = pd.DataFrame.from_dict(data).sort_values(by="count", ascending=False)

        if (limit_record_types is not None) & (
                limit_record_types != "None"):  # if the user hasn'nt selected anything or if the user has selected "Show All" from the Dropdown
            rows_to_display = int(limit_record_types)
            if rows_to_display > 0:
                agg = agg.nlargest(rows_to_display, columns="count")
            else:
                agg = agg.nsmallest(abs(rows_to_display),
                                    columns="count")  # abs() because we need a positive number of rows to take the smallest of

        fig = go.Figure([go.Bar(x=agg['record_type'], y=agg['count'], name=" ",
                                hovertemplate="Record Type: %{label} <br> Number of Records: %{value} ")])
        fig.update_xaxes(tickangle=-45)
        fig.update_yaxes(title_text="# of Records")
        fig.update_layout(title_text=None)

        return fig

except Exception as e:
    layout = html.H3(f"Problem loading {os.path.basename(__file__)}, please check console for details.")
    # TO DO: Update with logging.
    print(e)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)



