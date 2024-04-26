from datetime import timedelta, date

import streamlit as st
import data_access as data
import altair as alt
import pandas as pd

st.set_page_config(
    page_title="RailGuard: CheckUrChoo",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

alt.themes.enable("dark")

with st.sidebar:
    st.title("🚉 Station Performance Dashboard")

    stations = data.get_station_names()

    selected_station = st.selectbox("Select a station", stations, index=0)

    color_theme_list = [
        "blues",
        "cividis",
        "greens",
        "inferno",
        "magma",
        "plasma",
        "reds",
        "rainbow",
        "turbo",
        "viridis",
    ]
    selected_color_theme = st.selectbox("Select a color theme", color_theme_list)

    df_arrivals = data.get_arrivals_for_station(selected_station)


def make_donut(input_response, input_text, input_color):
    if input_color == "blue":
        chart_color = ["#29b5e8", "#155F7A"]
    elif input_color == "green":
        chart_color = ["#27AE60", "#12783D"]
    elif input_color == "orange":
        chart_color = ["#F39C12", "#875A12"]
    elif input_color == "red":
        chart_color = ["#E74C3C", "#781F16"]

    source = pd.DataFrame(
        {"Topic": ["", input_text], "% value": [100 - input_response, input_response]}
    )
    source_bg = pd.DataFrame({"Topic": ["", input_text], "% value": [100, 0]})

    plot = (
        alt.Chart(source)
        .mark_arc(innerRadius=45, cornerRadius=25)
        .encode(
            theta="% value",
            color=alt.Color(
                "Topic:N",
                scale=alt.Scale(
                    # domain=['A', 'B'],
                    domain=[input_text, ""],
                    # range=['#29b5e8', '#155F7A']),  # 31333F
                    range=chart_color,
                ),
                legend=None,
            ),
        )
        .properties(width=130, height=130)
    )

    text = plot.mark_text(
        align="center",
        color="#29b5e8",
        font="",
        fontSize=32,
        fontWeight=700,
        fontStyle="",
    ).encode(text=alt.value(f"{input_response:.0f}%"))
    plot_bg = (
        alt.Chart(source_bg)
        .mark_arc(innerRadius=45, cornerRadius=20)
        .encode(
            theta="% value",
            color=alt.Color(
                "Topic:N",
                scale=alt.Scale(
                    # domain=['A', 'B'],
                    domain=[input_text, ""],
                    range=chart_color,
                ),  # 31333F
                legend=None,
            ),
        )
        .properties(width=130, height=130)
    )

    return plot_bg + plot + text


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


col = st.columns((1.5, 4.5, 2), gap="medium")
with col[0]:
    st.subheader("Daily")

    st.markdown("---")

    st.subheader("Weekly")

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
    st.subheader(f"{selected_station}")
    line_chart = (
        alt.Chart(df_arrivals)
        .mark_line()
        .encode(x="scheduled_arrival:T", y="delay:Q")
        .properties(width=800, height=400, title="Train Performance")
    )
