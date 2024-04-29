from datetime import datetime

import streamlit as st
import data_access as data
import altair as alt
from charts import make_donut, make_delay_per_hour_chart, make_disruption_chart


def calculate_yesterday_percent_delayed():
    threshold = 5
    n_delayed = data.get_total_delays_for_station(threshold, selected_station)
    return (100 * n_delayed) / (n_arrivals + n_cancelled)


def get_color_for_value(value):
    if value < 5:
        return "green"
    elif value < 20:
        return "orange"
    else:
        return "red"


if __name__ == "__main__":
    st.set_page_config(
        page_title="RailWatch",
        page_icon="🚆",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    alt.themes.enable("dark")

    with st.sidebar:
        st.title("Station Performance Dashboard")

        stations = data.get_station_names()

        selected_station = st.selectbox("Select a station:", stations, index=0)

        df_arrivals = data.get_arrivals_for_station(selected_station)


col = st.columns((1.25, 3.5, 3), gap="medium")

with col[0]:
    st.markdown(
        "<h3 style='text-align: center; color: white;'>Yesterday's stats</h3>",
        unsafe_allow_html=True,
    )

    n_arrivals = data.get_total_arrivals_for_station(selected_station)
    n_cancelled = data.get_total_cancellations_for_station(selected_station)
    pct_cancelled = (100 * n_cancelled) / (n_arrivals + n_cancelled)
    color_cancelled = get_color_for_value(pct_cancelled)

    pct_delayed = calculate_yesterday_percent_delayed()
    color_delayed = get_color_for_value(pct_delayed)
    donut_chart_cancellations = make_donut(pct_cancelled, "Cancelled", color_cancelled)
    donut_chart_delays = make_donut(pct_delayed, "Delayed", color_delayed)

    stats_col = st.columns((0.2, 1, 0.2))
    with stats_col[1]:
        st.markdown("Cancellations")
        st.altair_chart(donut_chart_cancellations)
        st.markdown("Delays", help="Greater than 5 minutes.")
        st.altair_chart(donut_chart_delays)

with col[1]:
    st.markdown(
        "<h3 style='text-align: center; color: white;'>Hourly Breakdown</h3>",
        unsafe_allow_html=True,
    )

    time_range = st.radio(
        "Select time range:",
        options=["24 hours", "7 days", "30 days"],
        horizontal=True,
        index=2,
    )
    if time_range == "24 hours":
        days_delta = 1
    elif time_range == "7 days":
        days_delta = 7
    else:
        days_delta = 30

    delay_breakdown = data.get_delay_breakdown_for_station(
        selected_station, 5, days_delta
    )
    delay_breakdown["pct_delayed"] = (
        delay_breakdown["pct_delayed"].apply(float).apply(lambda x: x / 100)
    )
    delay_breakdown["interval_start"] = delay_breakdown["interval_start"].apply(
        lambda x: datetime.strptime(x.strftime("%H:%M") + ":00", "%H:%M:%S")
    )

    chart = make_delay_per_hour_chart(delay_breakdown)
    st.altair_chart(chart)


with col[2]:
    st.markdown(
        "<h3 style='text-align: center; color: white;'>Daily breakdown</h3>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    time_range = col1.radio(
        "Select time range:",
        options=["7 days", "30 days"],
        horizontal=True,
        index=1,
    )

    option = col2.selectbox(
        "Select disruption type:",
        ("Delay", "Cancellation"),
    )

    if time_range == "7 days":
        days_delta = 7
    else:
        days_delta = 30

    df = data.get_daily_stats(selected_station, 5, days_delta)

    st.altair_chart(make_disruption_chart(df, option))


incidents = data.get_current_incidents(selected_station)

incidents = incidents.drop(
    [
        "incident_id",
        "operator_id",
        "info_link",
        "description",
        "incident_uuid",
        "last_updated",
        "creation_date",
    ],
    axis=1,
)

st.markdown(
    "<h3 style='text-align: center; color: white;'>Incident Alerts</h3>",
    unsafe_allow_html=True,
)

st.dataframe(incidents)
