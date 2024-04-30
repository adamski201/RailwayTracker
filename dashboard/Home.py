import streamlit as st

st.set_page_config(
    page_title="RailWatch",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.image("logo.png", use_column_width=True)


# Page title
st.title("RailWatch: The Train Station Tracker")

# Main section
st.header("Welcome!")

st.markdown(
    """
    RailWatch (final name TBD!) uses a combination of real-time public data sources to provide
    automated cancellation and delay tracking. You can use RailWatch to track changes in performance
    at a station over time, see which hour of the day has the most delays, 
    find disruption and maintenance info at a glance, and more. You can also sign up to our email 
    and SMS alerting system to receive automated alerts the moment an incident occurs for your 
    chosen operator and/or station.

    ### Where do we source our data?
    - [The Realtime Trains API](https://api.rtt.io/)
    - [The National Rail Knowledgebase Feed](https://www.nationalrail.co.uk/developers/)
    ### Find out more
    - Check out our development progress on [GitHub](https://github.com/adamski201/Railway-Tracker).
"""
)
