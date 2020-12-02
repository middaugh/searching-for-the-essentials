"""HTML structure for Content Manager Dashboard Layout.

Utilizes app.py for the dash app, and pulls in the various
contents of apps/ into page-content.

Author: Information First, Esme Middaugh, emiddaugh@info-first.com
"""

import glob

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, TITLE
from apps import disposition_categories
from apps import disposition_schedule
from apps import indicators
from apps import lifecycle
from apps import owner_classification
from apps import timeseries

# TO DO: Find a better solution / a way to work into app.py. Leave for now.
logo = glob.glob('./assets/logo.*')[0]  # any file named "logo" in assets, used in footer


def serve_layout():
    """Dashboard Layout to be rendered with React"""
    layout = html.Div(
        children=[
            # represents the URL bar, doesn't render anything
            dcc.Location(id='url', refresh=False),
            html.Div(
                className="nav__container",
                children=[
                    html.Div(
                        id="nav",
                        className="nav nav--top",
                        children=[
                            html.Div(
                                className="nav__wrapper--left row flex-two centered align-baseline",
                                children=[
                                    html.H1(f"{TITLE}", id="title", className="nav__title"),
                                ]
                            ),
                            html.Div(
                                id="nav_links",
                                className="nav__links flex-one row",
                                children=[
                                    dcc.Link(
                                        "FOOD",
                                        href="/ingestion",
                                        className="nav__link nav__link--current"
                                    ),
                                    dcc.Link(
                                        "COUNTRY",
                                        href="/disposition",
                                        className="nav__link"
                                    ),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            # Where all of the content will go
            html.Div(className="page-content", id='page-content'),
            html.Footer(
                id='footer',
                className="footer clearfix centered",
                children=[
                    html.Img(src=glob.glob('assets/logo.*')[0], className="logo"),
                    html.Div(
                        children=[
                            """Under Active Development.
                            Copyright Information First, 2020.
                            Utilizing Plotly Dash.""",
                            html.Br(),
                            """Notes: 'Recent Ingestion' is set to the past two weeks.
                            The % & count up/down is based off of the 'Average Ingestion' time
                            frame, calculated as two months prior to the recent time frame.""",
                            html.Br(),
                        ]
                    )
                ]
            )
        ]
    )
    return layout


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    """Callback function to render different page-content depending on the url passed."""
    try:
        if pathname is None or pathname == "/" or pathname == "/ingestion":
            page_content = html.Div(
                className="",
                children=[
                    html.Div(
                        className="row",
                        children=[
                            indicators.layout
                        ]
                    ),
                    html.Div(
                        className="row print__page-break",
                        children=[
                            timeseries.layout
                        ]
                    ),
                    html.Div(
                        className="row",
                        children=[
                            owner_classification.layout
                        ]
                    )
                ]
            )
        elif pathname == '/disposition':
            page_content = html.Div(
                className="",
                children=[
                    html.Div(
                        className="row",
                        children=[lifecycle.layout]
                    ),
                    html.Div(
                        className="row",
                        children=[
                            disposition_categories.layout,
                            disposition_schedule.layout
                        ]
                    )
                ]
            )
        else:
            page_content = html.Div([html.H1('404 Error - Page not found')])
        return page_content
    except ImportError:
        return html.Div("Something went wrong with one of your imported graphs! Please check.")


app.layout = serve_layout
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
