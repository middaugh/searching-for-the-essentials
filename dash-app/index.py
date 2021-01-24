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
                                    "When the COVID-19 pandemic hit the world in 2020, nearly every aspect of daily life was affected. The food industry was shaken as people began hoarding products like pasta, toilet paper or rice. Due to restaurants and cafés closing in many countries, people were not able to go out for dinner or grab a coffee anymore. Lots of people began experimenting more in the kitchen and doubtless, lots of banana bread have been produced. This interactive web map aims to visualise the impact of COVID-19 on interests in food and other essential items in three European countries based on the Google Trends data of specific products. Enjoy exploring and comparing acroos foods, countries & time."
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
                            country_map.layout,
                        ]
                    ),
                    html.H3("Extra Information", className="text-centered nav__subtitle"),
                    html.Div(
                        className="project-explanation flex-one centered row",
                        children=[
                            "In the radar chart are no absolute values given, but a range from -60 to 100. This displays if a search term has been searched for less often than the previous year (negative value), or more often than the previous year (positive value). Because there were differences in the restrictions per country, some differences in searchterms can clearly be seen. Check out the differences between the search term \"facemask\", or \"toiletpaper\". The chart on the right visualizes the Google Search Trends chronologically for the selected countries. "
                        ],
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
                            food_map.layout,
                        ]
                    ),
                    html.H3("Extra Information", className="text-centered nav__subtitle"),
                    html.Div(
                        className="project-explanation flex-one centered row",
                        children=[
                            "The timeframe for the Google Search Trend data in the map is from November 2018 till November 2020. The first year is the non-covid data, and we compare the second year (Nov 2019-Nov 2020), with the first year (Nov 2018-Nov 2019). A positive search query value means that the search term has been searched more often than in the previous year, and a negative search value means that it has been searched less often. The bigger the circle on the map, the higher the positive or negative difference. In this way the difference between the two years are displayed. The new reported corona cases per day are calculated with the data from the World Health Organisation. To be able to compare the COVID-19 outbreaks per country, we calculated the new reported corona cases per day per 100 000 inhabitants. Note that the countries had less test capacity during the first wave, resulting in the first wave to be less accurate than the second wave. "
                        ]
                    ),
                ]
            ),
        else:
            page_content = html.Div([html.H1('404 Error - Page not found')])
        return page_content
    except ImportError:
        return html.Div("Something went wrong with one of your imported graphs! Please check.")


app.layout = serve_layout
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
