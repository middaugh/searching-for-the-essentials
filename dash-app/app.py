"""
Searching for the Essentials
Mapping Project

Modify this script to suit color preferences & various directory setups.

"""
import os
import dash
import plotly.graph_objects as go
import plotly.io as pio

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # absolute path to parent directory, aka dashboard_app
INPUT_DIR = os.path.join(BASE_DIR, 'output-data/')  # data stored from model.py
TITLE = "SEARCHING FOR THE ESSENTIALS"
COLOR_PALETTE_CATEGORICAL = ["#419d78", "#13262f", "#de6449", "#eac435", "#6d9dc5", "#a74482", "#f5e5fc"]
COLOR_PALETTE_GRADIENT = ["#73cfaa", "#0f6b46"]

###########################
# Creating and Setting our Base Theme
###########################
config = {'displaylogo': False, 'scrollZoom': False, 'displayModeBar': False}
base_font = dict(family='Roboto, Helvetica, HelveticaNeue, Open Sans, sans-serif', size=15, color="#111111")
base_colorway = COLOR_PALETTE_CATEGORICAL  # from config.ini, pulled in above

base_theme_fig = go.Figure(
    layout={
        'font': base_font,
        'colorway': base_colorway,
        'xaxis': {'tickfont': {'color': '#707070'}},
        'yaxis': {'tickfont': {'color': '#707070'}},
    }
)

# Uncomment if in Draft Mode
base_theme_fig.layout.annotations = [
    dict(
        name="draft watermark",
        text="DRAFT",
        textangle=-30,
        opacity=0.1,
        font=dict(color="black", size=100),
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
    )
]

base_theme_fig.update_layout(
    xaxis_tickfont_size=14,
    template="plotly_white",
    title={
        'y': .3,
        'x': 0.5,
        'xanchor': 'left',
        'yanchor': 'top'
    },
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=10, l=10, r=10, b=10, pad=5)
)

# Axis Titles & Labels to Dark Gray
base_theme_fig.update_yaxes(color="#505050")
base_theme_fig.update_xaxes(color="#505050")

# Setting our Theme to Default
templated_base_theme = pio.to_templated(base_theme_fig)
pio.templates['base_theme'] = templated_base_theme.layout.template
pio.templates.default = "base_theme"

###########################
# BASE DASH APP FLASK SETUP
###########################
external_scripts = ['https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js'] # jquery is used for URL / Navigation highlight
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_scripts=external_scripts)
app.config.suppress_callback_exceptions = True  # see https://community.plotly.com/t/dcc-tabs-filling-tabs-with-dynamic-content-how-to-organize-the-callbacks/6377
#server = app.server  # necessary for WSGI server

###########################
# LAYOUT
###########################
app.title = TITLE
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%} Dashboard</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,700,900|Roboto+Mono|Economica:300,400,700&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css?family=Monoton&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css?family=Playfair+Display:300,400,700,900&display=swap" rel="stylesheet">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=yes">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

