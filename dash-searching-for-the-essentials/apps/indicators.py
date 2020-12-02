"""
Indicators Interaction Block
Author: Information First, Esme Middaugh, emiddaugh@info-first.com
Last Updated: 2020SEP17
"""

import os
from datetime import datetime, timedelta
import pandas as pd

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

from app import app, INPUT_DIR

try:
    ###########################
    # READ IN DATA
    ###########################
    parse_dates = ['date_registered']  # need the correct format
    date_registered_df = pd.read_csv(INPUT_DIR + 'date_registered.csv', parse_dates=parse_dates)
    disposed_date_inactive_df = pd.read_csv(INPUT_DIR + 'disposed_date_inactive.csv')

    ###########################
    # PREP
    ###########################

    # For displaying the range of dates at the top of the dashboard
    start_date = date_registered_df['date_registered'].min().date()
    end_date = date_registered_df['date_registered'].max().date()

    # For Displaying Last Updated -- pulled from the files themselves
    last_updated_timestamp = os.path.getmtime(INPUT_DIR + 'active.csv')
    last_updated = datetime.fromtimestamp(int(last_updated_timestamp)).strftime('%Y-%m-%d %H:%M:%S')[
                   :-3]  # dont want the milliseconds

    # ****** Indicators
    # Setting our ranges for the overall average ingestion time vs
    base_weeks = 2
    time_periods = 4
    recent_time_period = timedelta(weeks=base_weeks)
    avg_time_period = timedelta(weeks=base_weeks * time_periods)  # approx. 2 months

    # Recent time range dates
    end_recent = date_registered_df['date_registered'].max().floor(
        'D')  # pandas uses datetime(ns) so we need to match
    start_recent = end_recent - recent_time_period

    # Overall average time range dates
    end_avg = start_recent  # don't want to include the most recent time period in the calculations
    start_avg = end_avg - avg_time_period  # 3 months

    # How many records created during this time
    avg_count = date_registered_df[date_registered_df['date_registered'].between(start_avg, end_avg)]['count'].sum()
    avg_count_normalized = avg_count / (time_periods)  # the count per base time period
    recent_count = date_registered_df[date_registered_df['date_registered'].between(start_recent, end_recent)][
        'count'].sum()

    # Average Records Per Day
    avg_rate = int(avg_count / avg_time_period.days)
    recent_rate = int(recent_count / recent_time_period.days)

    # Total Disposed
    total_disposed = disposed_date_inactive_df['cumulative_count'].max()

    # Making all the indicators
    #indicator_font_size = 35
    # use with number={'prefix': "", "font": {"size": indicator_font_size}},
    indicator_margin = dict(l=15, r=15, b=0, t=45, pad=2)

    # First
    indicator_total = go.Figure(
        go.Indicator(
            mode="number",
            title={
                "text": "Total Records<br>in Dataset",
            },
            value=date_registered_df['cumulative_count'].max() + disposed_date_inactive_df[
                'cumulative_count'].max(),
            # Total rows in each database = number in system

        )
    ).update_layout(
        margin=indicator_margin
    )

    indicator_active = go.Figure(
        go.Indicator(
            mode="number",
            title="Active<br>Records",
            value=date_registered_df['cumulative_count'].max(),  # final cumulative count = total active

        )
    ).update_layout(
        margin=indicator_margin
    )

    indicator_two_week = go.Figure(
        go.Indicator(
            mode="number+delta",
            title="Two Week<br>Ingestion Count",
            value=recent_count,
            delta={'position': "top", 'reference': avg_count_normalized},
        )
    ).update_layout(
        margin=indicator_margin
    )

    indicator_daily = go.Figure(
        go.Indicator(
            mode="number+delta",
            title="Daily<br>Ingestion Rate",
            value=recent_rate,
            delta={'position': "top", 'reference': avg_rate, 'relative': True},
        )
    ).update_layout(
        margin=indicator_margin
    )
    indicator_disposed = go.Figure(
        go.Indicator(
            mode="number",
            title="Disposed<br>Records",
            value=total_disposed
        )
    ).update_layout(
        margin=indicator_margin
    )

    ###########################
    # LAYOUT TO BE USED IN INDEX.PY
    ###########################
    layout = html.Div(
        className="viz-card viz-card--indicators flex-one",
        children=[
            html.Div(
                className="viz-card__graph viz-card__graph--indicators row",
                children=[
                    dcc.Graph(
                        className="sub-indicator",
                        figure=indicator_total
                    ),
                    dcc.Graph(
                        className="sub-indicator",
                        figure=indicator_active
                    ),
                    dcc.Graph(
                        className="sub-indicator",
                        figure=indicator_two_week
                    ),
                    dcc.Graph(
                        className="sub-indicator",
                        figure=indicator_daily
                    ),
                    dcc.Graph(
                        className="sub-indicator",
                        figure=indicator_disposed
                    )
                ]
            )
        ]
    )

except Exception as e:
    layout = html.H3(f"Problem loading {os.path.basename(__file__)}, please check console for details.")
    # TO DO: Update with logging.
    print(e)

if __name__ == '__main__':
    app.layout = layout
    app.run_server(debug=True)

