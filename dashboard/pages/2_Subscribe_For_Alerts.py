import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="RailWatch",
    page_icon="🚆",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.image("logo.png", use_column_width=True)


# Dummy data for demonstration
data = {
    "Station": ["Birmingham New Street", "Hemel Hempstead", "Euston"],
    "Cancelled Trains": [10, 5, 3],
    "Delayed Trains": [20, 15, 8],
    "Average Delay (min)": [3.5, 4.0, 2.8],
    "Incident Time": ["08:00", "10:30", "13:45"],
    "Incident Description": ["Signal issue", "Track maintenance", "Power outage"],
}
df = pd.DataFrame(data)

st.header("Alert Subscription")

# Subscription form
st.subheader("Enter your details here")
name = st.text_input("Enter your first name")
email = st.text_input("Enter your email")
phone_number = st.text_input("Enter your phone number")
subscribed_station = st.selectbox("Select Station", options=df["Station"], index=None)
subscribed_operator = st.selectbox(
    "Select Operator",
    options=["Southeastern", "Great Western Railway", "East Midlands Railway"],
    index=None,
)

st.markdown("#")

# Subscribe button
if st.button("Subscribe", use_container_width=True):
    # Placeholder for subscription logic (e.g., saving to database)
    st.success("Subscription successful!")
