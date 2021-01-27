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
                                className="project-explanation project-explanation-first flex-one centered",
                                children=[
                                    "When the COVID-19 pandemic hit the world in 2020, nearly every aspect of daily life was affected. The food industry was shaken as people began hoarding products like pasta, toilet paper or rice. Due to restaurants and cafes closing in many countries, people were not able to go out for dinner or grab a coffee anymore. Lots of people began experimenting more in the kitchen and doubtless, huge amounts of banana bread were being produced. This interactive web map aims to visualize the impact of COVID-19 on interests in food and other essential items in three European countries based on Google Trends data of specific products. Enjoy exploring and comparing across foods, countries & time."
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
                    html.H3("ABOUT", className="text-centered nav__link"),
                    html.Div(
                        className="nav_container",
                        children=[
                            dcc.Markdown(
                            className="project-explanation flex-one centered",
                            children='''Searching For The Essentials is an interactive web map experience allowing the user to explore the evolution of 
                            [Google Trends](https://trends.google.com)  data during the COVID-19 pandemic. We used the 
                            Google data from November 2018 to November 2020 and calculated the Search Trends differences 
                            between the first year (11/2018-11/2019) and the second year with COVID-19 impact (11/2019-11/2020). 
                            The result from this calculation is used for the data visualizations. 
                            A positive search query value indicates that the search term was searched more often during the 
                            pandemic than in the previous year, whereas a negative search value indicates a lower search 
                            frequency during the pandemic compared to the year before.
                            '''),
                            dcc.Markdown(
                            className="project-explanation flex-one centered",
                            children='''The COVID-19 cases per 100.000 inhabitants per country were calculated from the daily 
                            reported COVID-19 data available on the website of the [World Health Organization](https://www.who.int/). 
                            Note, that the countries were having lest testing capacity during the start of the pandemic 
                            in March 2020 resulting in less accuracy than for the second wave starting in autumn 2020. 
                            '''),
                            dcc.Markdown(
                            className="project-explanation flex-one centered row",
                            children='''
                            In contrast to the values shown in the map, the radar chart includes negative and positive 
                            values indicating a lower or higher search frequency than in the previous year.
                            ''')
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
                    html.H3("ABOUT", className="text-centered nav__link"),
                    html.Div(
                        className="nav_container",
                        children=[
                            dcc.Markdown(
                            className="project-explanation flex-one centered",
                            children='''Searching For The Essentials is an interactive web map experience allowing the user to explore the evolution of 
                            [Google Trends](https://trends.google.com)  data during the COVID-19 pandemic. We used the 
                            Google data from November 2018 to November 2020 and calculated the Search Trends differences 
                            between the first year (11/2018-11/2019) and the second year with COVID-19 impact (11/2019-11/2020). 
                            The result from this calculation is used for the data visualizations. 
                            A positive search query value indicates that the search term was searched more often during the 
                            pandemic than in the previous year, whereas a negative search value indicates a lower search 
                            frequency during the pandemic compared to the year before.
                            '''),
                            dcc.Markdown(
                            className="project-explanation flex-one centered",
                            children='''The COVID-19 cases per 100.000 inhabitants per country were calculated from the daily 
                            reported COVID-19 data available on the website of the [World Health Organization](https://www.who.int/). 
                            Note, that the countries were having lest testing capacity during the start of the pandemic 
                            in March 2020 resulting in less accuracy than for the second wave starting in autumn 2020. 
                            '''),
                            dcc.Markdown(
                            className="project-explanation flex-one centered row",
                            children='''
                            In contrast to the values shown in the map, the radar chart includes negative and positive 
                            values indicating a lower or higher search frequency than in the previous year.
                            ''')
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
