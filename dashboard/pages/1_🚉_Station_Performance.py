from datetime import timedelta, date

import streamlit as st
import data_access as data
import altair as alt

st.set_page_config(
    page_title="RailGuard: CheckUrChoo",
    page_icon="🚆",
)

stations = data.get_station_names()

selected_station = st.selectbox("Select Station", options=stations)

st.header(f"Performance metrics for ({date.today() - timedelta(days=1)})")

n_arrivals = data.get_total_arrivals_for_station(selected_station)

n_cancelled = data.get_total_cancellations_for_station(selected_station)

pct_cancelled = (100 * n_cancelled) / (n_arrivals + n_cancelled)

st.header(f"{pct_cancelled:.2f}% cancelled")

thresold = 5
n_delayed = data.get_total_delays_for_station(thresold, selected_station)

pct_delayed = (100 * n_delayed) / (n_arrivals + n_cancelled)

st.header(f"{pct_delayed:.2f}% delayed by at least {thresold} mins.")
