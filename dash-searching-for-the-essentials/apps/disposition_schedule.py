"""
Disposition Schedule Viz Card
Author: Information First, Esme Middaugh, emiddaugh@info-first.com
Last Updated: 2020SEP25
"""

import os
from datetime import datetime, timedelta
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go

from app import app, INPUT_DIR

try:
    ###########################
    # READ IN DATA
    ###########################
    # Replace this section with reading in data from INPUT_DIR
    due_for_destruction_df = pd.read_csv(INPUT_DIR + 'due_for_destruction.csv')

    ###########################
    # PREP
    ###########################
    # Any sort of data processing or creation of graph figures that are too bulky to easily go into the layout inline

    ###########################
    # LAYOUT TO BE USED IN INDEX.PY
    ###########################
    layout = html.Div(
                className="viz-card flex-two",
                children=[
                    html.H3(
                        className="viz-card__header",
                        children="Records Due for Destruction"
                    ),
                    dcc.Graph(
                        id='due_for_destruction_graph',
                        className="viz-card__graph viz-card__graph--disposition_schedule",
                        figure=go.Figure(
                            go.Bar(
                                x=due_for_destruction_df['year'],
                                y=due_for_destruction_df['count'],
                                name="",
                                hovertemplate="Year: %{label} <br> Records due for Destruction: %{value} "
                            )
                        ).update_yaxes(title_text="# of Records"
                        ).update_layout(autosize=True)
                    )
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