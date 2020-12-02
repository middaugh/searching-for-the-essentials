"""
Disposition Interaction Block
Author: Information First, Esme Middaugh, emiddaugh@info-first.com
Last Updated: 2020SEP17
"""

import os

import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px


from app import app, INPUT_DIR

try:
    ###########################
    # READ IN DATA
    ###########################
    parse_dates = ['date_registered']  # need the correct format
    date_registered_df = pd.read_csv(INPUT_DIR + 'date_registered.csv', parse_dates=parse_dates)
    disposed_status_df = pd.read_csv(INPUT_DIR + 'disposed_status.csv')
    disposed_date_registered_df = pd.read_csv(INPUT_DIR + 'disposed_date_registered.csv')
    disposed_date_inactive_df = pd.read_csv(INPUT_DIR + 'disposed_date_inactive.csv')
    due_for_destruction_df = pd.read_csv(INPUT_DIR + 'due_for_destruction.csv')

    ###########################
    # PREP
    ###########################
    due_count = due_for_destruction_df['count'].sum()
    active_count = date_registered_df['cumulative_count'].max()
    disposed_count = disposed_date_inactive_df['cumulative_count'].max()
    no_disposition_set_count = date_registered_df['cumulative_count'].max() - due_for_destruction_df['count'].sum()

    total_count = due_count + no_disposition_set_count + disposed_count
    lifecycle_df = pd.DataFrame(columns=["stage", "count", "percent", "y"],
                                data=[
                                    ["disposed", disposed_count, disposed_count * 100 / total_count, 10],
                                    ["due", due_count, due_count * 100 / total_count, 10],
                                    ["no disposition set", no_disposition_set_count,
                                     no_disposition_set_count * 100 / total_count, 10]
                                ])

    disposed_lifecycle_fig = px.bar(
        lifecycle_df,
        x="count",
        y="stage",
        text="percent",
        orientation='h',
        height=200,
        hover_data={
            'stage': True,
            'count': True,
            'percent': ':.1f'
        }
    )
    disposed_lifecycle_fig.update_layout(
        #margin=dict(r=100, b=20, t=60, pad=10),
        xaxis=dict(
            range=[0, lifecycle_df["count"].max() * 1.3],  # sets the range of xaxis, helps add more space for labels
            constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
        ),
    )
    disposed_lifecycle_fig.update_xaxes(title="").update_yaxes(title="")
    disposed_lifecycle_fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>Records: %{customdata[1]}<br>Percent: %{customdata[2]:.1f}<extra></extra>", #print("plotly express hovertemplate:", disposed_lifecycle_fig.data[0].hovertemplate)
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )


    ###########################
    # LAYOUT TO BE USED IN INDEX.PY
    ###########################
    layout = html.Div(
                className="viz-card viz-card--lifecycle flex-one",
                children=[
                    html.H4(
                        className="viz-card__header viz-card__header--lifecycle",
                        children="Records Lifecycle"),
                    html.Div(
                        className="viz-card__explainer viz-card__explainer--lifecycle",
                        children="Proportion of all records in their various lifecycle phases."
                    ),
                    dcc.Graph(
                        className="viz-card__graph viz-card__graph--lifecycle",
                        figure=disposed_lifecycle_fig
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

