"""HTML structure for the base app.

Utilizes app.py for the dash app, and pulls in the various
contents of apps/ into page-content.
"""

import glob

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, TITLE
from apps import food_map

# TO DO: Find a better solution / a way to work into app.py. Leave for now.
logo = glob.glob('./assets/logo.*')[0]  # any file named "logo" in assets, used in footer


def serve_layout():
    """Dashboard Layout to be rendered with React"""
    layout = html.Div(
        children=[
            # represents the URL bar, doesn't render anything
            dcc.Location(id='url', refresh=False),
            html.Div(
                className="nav__container nav--side",
                children=[
                    html.Div(
                        id="nav",
                        className="nav nav--side",
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
                                        href="/food",
                                        className="nav__link nav__link--current"
                                    ),
                                    dcc.Link(
                                        "COUNTRY",
                                        href="/country",
                                        className="nav__link"
                                    ),
                                ]
                            ),
                            html.Div(
                                className="nav__explainer",
                                children=[
                                    "Impacts of COVID-19 on Web Searches for Food & Other Necessities"
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
                    html.Div(
                        children=[
                            """Created for Erasmus Mundus Joint Master's in Cartography Mapping Project""",
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
        if pathname is None or pathname == "/" or pathname == "/food" or pathname:
            page_content = html.Div(
                className="",
                children=[
                    html.Div(
                        className="row",
                        children=[
                            food_map.layout
                        ]
                    ),
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
