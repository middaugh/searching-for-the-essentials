"""
<<TEMPLATE>> Viz Card
Author: <<COMPANY>>, <<NAME>>, <<EMAIL>>
Last Updated: <<DATE HERE>>
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
    # df = pd.read_csv(INPUT_DIR + "_____.csv")

    ###########################
    # PREP
    ###########################
    # Any sort of data processing or creation of graph figures that are too bulky to easily go into the layout inline

    ###########################
    # LAYOUT TO BE USED IN INDEX.PY
    ###########################
    layout = html.Div(
        className="viz-card viz-card--template",
        children=[
            html.H4(
                className="viz-card__header viz-card__header--template",
                children="Template Page"
            ),
            html.P(
                className="viz-card__explainer viz-card__explainer--template",
                children="This is an explanation paragraph. It has the class .viz-card__explainer applied."
            ),
            html.Div(
                # Because of a bug in the dash system, need a wrapper div
                className="viz-card__controller viz-card__controller--template",
                children=[
                    dcc.Dropdown()
                ]
            ),
            dcc.Graph(
                id="template_graph",
                className="viz-card__graph viz-card__graph--template"
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