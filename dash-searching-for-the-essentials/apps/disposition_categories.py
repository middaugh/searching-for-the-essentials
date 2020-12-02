"""
Disposition Interaction Block
Author: Information First, Esme Middaugh, emiddaugh@info-first.com
Last Updated: 2020SEP17
"""

import os

import pandas as pd
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go


from app import app, INPUT_DIR, COLOR_PALETTE_CATEGORICAL

try:
    ###########################
    # READ IN DATA
    ###########################
    disposed_status_df = pd.read_csv(INPUT_DIR + 'disposed_status.csv')

    ###########################
    # PREP
    ###########################
    disposed_status_fig = go.Figure(
        data=[go.Pie(
            labels=disposed_status_df["disposition_status"],
            values=disposed_status_df['count'],
            hole=.5,
            name='Status',
            textinfo=None,
            hoverinfo='label+percent+name+value',
            insidetextorientation='horizontal')
        ]
    )
    disposed_status_fig.update_layout(
        showlegend=True,
        legend_orientation='h',
        title=None,
        legend=dict(
            traceorder="normal",
            font=dict(
                size=12,
                color="gray"
            ))).update_traces(
        marker=dict(colors=COLOR_PALETTE_CATEGORICAL))

    ###########################
    # LAYOUT TO BE USED IN INDEX.PY
    ###########################
    layout = html.Div(
                className="viz-card flex-one",
                children=[
                    html.H3(
                        className="viz-card__header",
                        children="Disposed Records by Type"
                    ),
                    dcc.Graph(
                        id="disposition_pie_graph",
                        className='viz-card__graph',
                        figure=disposed_status_fig
                    ),
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