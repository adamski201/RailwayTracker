"""Contains functions for creating graphs for a streamlit dashboard."""

import pandas as pd
import altair as alt

scale = alt.Scale(
    domain=[0, 0.10, 0.25, 1],
    range=["green", "yellow", "red", "red"],  # Red for values above 20%
)


def make_donut(input_response: float, input_text: str, input_color: str) -> alt.Chart:
    """Creates a donut chart."""
    if input_color == "blue":
        chart_color = ["#29b5e8", "#155F7A"]
    elif input_color == "green":
        chart_color = ["#27AE60", "#12783D"]
    elif input_color == "orange":
        chart_color = ["#F39C12", "#875A12"]
    else:
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


def make_delay_per_hour_chart(df: pd.DataFrame) -> alt.Chart:
    """Creates a bar chart showing delays per hour of the day."""
    return (
        alt.Chart(df)
        .mark_bar(cornerRadius=10)
        .encode(
            alt.X(
                "interval_start:T",
                axis=alt.Axis(title="Time of day", format="%I%p"),
            ),
            alt.Y(
                "pct_delayed:Q",
                axis=alt.Axis(title="Percentage delayed", format=".0%"),
                scale=alt.Scale(domain=(0, 0.6)),
            ),
            alt.Color("pct_delayed", legend=None, scale=scale),
        )
        .properties(width=450, height=320)
        .configure_axis(grid=False, domain=True)
    )


def make_delay_historical_chart(df: pd.DataFrame):
    """Creates a bar chart showing historical trends for delays at a station."""
    return (
        alt.Chart(df)
        .mark_bar(cornerRadius=3, size=20, color="orange")
        .encode(
            alt.X(
                "date:O",
                timeUnit="yearmonthdate",
                axis=alt.Axis(title="Date", format="%d %b"),
            ),
            alt.Y("delays:Q", axis=alt.Axis(title="Volume of delays")),
        )
        .properties(width=400, height=300)
        .configure_axis(grid=False, domain=True)
    )


def make_cancellation_historical_chart(df: pd.DataFrame) -> alt.Chart:
    """Creates a bar chart showing historical trends for cancellations at a station."""
    return (
        alt.Chart(df)
        .mark_bar(cornerRadius=3, size=20, color="orange")
        .encode(
            alt.X(
                "date:O",
                timeUnit="yearmonthdate",
                axis=alt.Axis(title="Date", format="%d %b"),
            ),
            alt.Y("cancellations:Q", axis=alt.Axis(title="Volume of cancellations")),
        )
        .properties(width=400, height=300)
        .configure_axis(grid=False, domain=True)
    )
