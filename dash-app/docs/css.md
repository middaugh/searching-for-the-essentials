# CSS System 

The CSS for the dashboards is based on 
BEM (Block Element Modifier) and modified ITCSS (Inverted Triangle CSS) principles.
In assets/ the css files are titled:
- 01_settings.css - 
- 02_normalize.css - helps the dashboard to look similar across all modern browsers
- 03_general.css - set any base elements here
- 04_layout.css - overall layout of the dashboard page, including the formatting of the navigation and footer
- 05_viz-card.css - general formatting styles 


All formatting is applied via classes, do not use #IDs. Should you have to use an ID to style something, 
only do so within shame.css & comment with your name, and date with the idea of eventually going back to fix. 

## BEM 

In our case, a dashboard is made up of three main block types: 
- .nav
- .viz-card
- .footer


A great explanation of BEM Can be Found at: 



## Understanding the components of a  viz-card

Each viz-card block represents a set of graphs and headers, explainers and controllers that all share the same 
dataset or are conceptually linked. Oftentimes the elements of a viz-card will be used together in a callback function, 
although not always. 

A viz-card is composed of one or more of each of the following: 
- viz-card__header - typically an html.H#() element
- viz-card__explainer - typically an html.P() or html.P() that helps to explain what the 
graph(s) is showing or how to use the controllers
- viz-card__controller - an html.Div() containing a dcc.Dropdown(), dcc.Radio, etc 
- viz-card__graph - a dcc.Graph() or dash_table.DataTable() element

## How .css and apps/ work together 

Applying the BEM naming system, if a graph component from the timeseries.py needs additional
styling, it would get the class (applied through *className* keyword) of viz-card__graph--timeseries
applied to it. 

All modifier classes that relate to a specific *.py* module are placed in a separate .css file
named according to the time of the *.py* module. For example, all modifying classes that pertain to 
elements from the *timeseries.py* module 


## Peculiarities of Flexbox Containers with Graphs & Layout within Dashboard

It is important that each top-level *.viz-card* block NOT be defined as a flexbox container (eg, with no .column or .row applied). 
This ensures that the graphs within it scale correctly and do not overflow the card (the min-width of the card and the min-width
of the viz-card__graph must be set to the same number). The top level .viz-card should, however, indicate it's desired 
size within the dashboard through .flex-one, .flex-two, etc.; consider where it will be placed relative to other containers.

Within *index.py*, each *module.layout* is placed within a div.row, either by itself (if it is to takeup 
the whole row) or with another if they are to share a row, the proportion of which is determined
by the sizes appplied within the *module.py*. 

Examples: 

    html.Div(
    className="row
    children=module.layout
    )

or 

    html.Div(
        className="row",
        children=[module2.layout] /* In module2.py, .viz-card has .flex-one class and will takeup whole row */
    ),
    html.Div(
        className="row",
        children=[
            moddule3.layout, /* In module3.py, .viz-card has .flex-two class and will takeup 1/3 of the row */
            module4.layout /* In module4.py, .viz-card has .flex-two class and will takeup 2/3 of the row */
        ]
    )