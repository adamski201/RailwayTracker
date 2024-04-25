import streamlit as st
from data_access import get_station_names

st.set_page_config(
    page_title="RailGuard: CheckUrChoo",
    page_icon="🚆",
)

stations = get_station_names()

selected_station = st.selectbox("Select Station", options=stations)
