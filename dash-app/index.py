"""HTML structure for the base app.

Utilizes app.py for the dash app, and pulls in the various
contents of apps/ into page-content.
"""

import glob

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, TITLE
from apps import food_map, country_map


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
                        className="nav",
                        children=[
                            html.Div(
                                className="nav__wrapper row flex-one centered align-baseline",
                                children=[
                                    html.H1("Searching for the Essentials", id="title", className="nav__title")
                                ]
                            ),
                            html.H3("Impacts of COVID-19 on Web Searches for Food & Other Necessities", className="text-centered nav__subtitle"),
                            html.Div(
                                className="project-explanation flex-one centered row",
                                children=[
                                    # TODO: Update with proper explanation, taken from the project proposal
                                    "When the COVID-19 pandemic hit the world, nearly every aspect of daily life was affected. The food industry was shaken as people began hoarding products like pasta, toilet paper or dried beans. Due to restaurants and cafés closing in many countries, people were not able to go out for dinner or grab a coffee. Also, lots of people began experimenting more in the kitchen. This interactive web map aims to visualise the impact of COVID-19 on interests in food and other essential items, based on the Google Trends data of specific products. "
                                ]
                            ),
                            html.Div(
                                id="nav_links",
                                className="nav__links flex-one row",
                                children=[
                                    dcc.Link(
                                        "FOOD",
                                        href="/food",
                                        className="nav__link"
                                    ),
                                    dcc.Link(
                                        "COUNTRY",
                                        href="/country",
                                        className="nav__link"
                                    ),
                                ]
                            ),

                        ]
                    ),
                ]
            ),

            # Where all of the content will go
            html.Div(className="page-content centered", id='page-content'),

            html.H3("Extra information", className="text-centered nav__subtitle"),
            html.Div(
                className="nav_container",
                children=[
                    html.Div(
                        className="project-explanation flex-one centered row",
                        children=[
                            # TODO: Update with proper explanation, taken from the project proposal
                            "For displaying the Google Search Trend data in the map, we have used data from November 2018 till November 2020. The first year is the non-covid data, and we compare the second year (Nov 2019-Nov 2020), with the first year (Nov 2018-Nov 2019). A positive search query value means that the search term has been searched more often than in the previous year, and a negative search value means that it has been searched less often. In this way the difference between the two years are displayed. The new reported corona cases per day are calculated with the data that is available on the site of the World Health Organisation. To be able to compare the Corona outbreaks per country, we calculated the new reported corona cases per day. Note that the countries had lest test capacity during the first day, therefore the first wave is less accurate than for the second wave. "
                        ]
                    ),
                ]
            ),

            html.H3("Extra information", className="text-centered nav__subtitle"),
            html.Div(
                className="nav_container",
                children=[
                    html.Div(
                        className="project-explanation flex-one centered row",
                        children=[
                            # TODO: Update with proper explanation, taken from the project proposal
                            "In the radar chart are no absolute values given, but a range from -60 to 100. This displays if a search term has been searched for less often than the previous year (negative value), or more often than the previous year (positive value).  "
                        ]
                    ),
                ]
            ),

            html.Footer(
                id='footer',
                className="footer clearfix centered",
                children=[
                    html.Div(
                        children=[
                            """Created for Erasmus Mundus Joint Master's in Cartography Mapping Project. """,
                            html.Br(),
                            "Vivien, Nele, & Esmé",
                            html.Br()
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
        if pathname == "/country":
            page_content = html.Div(
                className="",
                children=[
                    html.Div(
                        className="row",
                        children=[
                            country_map.layout
                        ]
                    ),
                ]
            )
        elif pathname is None or pathname == "/" or pathname == "/food":
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
