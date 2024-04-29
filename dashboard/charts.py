import pandas as pd
import altair as alt
import vega

colour_scale = alt.Scale(range=["#12783D", "#FFA500", "#DC143C"])


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


def make_delay_per_hour_chart(df: pd.DataFrame):
    return (
        alt.Chart(df)
        .mark_bar(cornerRadius=10)
        .encode(
            alt.X(
                "interval_start:T",
                axis=alt.Axis(title="Time of day", format="%I%p"),
            ),
            alt.Y(
                "pct_delayed:Q", axis=alt.Axis(title="Percentage delayed", format=".0%")
            ),
            alt.Color("pct_delayed", legend=None, scale=colour_scale),
        )
        .properties(width=450, height=400)
        .configure_axis(grid=False, domain=True)
    )


def make_disruption_chart(df: pd.DataFrame, disruption_type: str):
    if disruption_type == "Delay":
        return (
            alt.Chart(df)
            .mark_bar(cornerRadius=3, size=20)
            .encode(
                alt.X(
                    "date:O",
                    timeUnit="yearmonthdate",
                    axis=alt.Axis(title="Date", format="%d %b"),
                ),
                alt.Y("delays:Q", axis=alt.Axis(title="Volume of delays")),
                alt.Color(
                    "delays",
                    legend=None,
                    scale=alt.Scale(scheme="goldorange"),
                ),
            )
            .properties(width=400, height=375)
            .configure_axis(grid=False, domain=True)
        )
    else:
        return (
            alt.Chart(df)
            .mark_bar(size=20)
            .encode(
                alt.X(
                    "date:O",
                    timeUnit="yearmonthdate",
                    axis=alt.Axis(title="Date", format="%d %b"),
                ),
                alt.Y(
                    "cancellations:Q", axis=alt.Axis(title="Volume of cancellations")
                ),
                alt.Color(
                    "cancellations",
                    legend=None,
                    scale=alt.Scale(scheme="goldorange"),
                ),
            )
            .properties(width=400, height=375)
            .configure_axis(grid=False, domain=True)
        )
