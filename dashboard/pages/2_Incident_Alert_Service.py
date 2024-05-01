"""Streamlit app for incidents subscription form"""

from os import environ as ENV
from dotenv import load_dotenv

import streamlit as st
from boto3 import client

from subscribe import on_submit


OPERATORS = {
    "VT": "Avanti West Coast",
    "CC": "c2c",
    "CS": "Caledonian Sleeper",
    "CH": "Chiltern Railways",
    "XC": "CrossCountry",
    "EM": "East Midlands Railway",
    "XR": "Elizabeth Line",
    "ES": "Eurostar",
    "GC": "Grand Central",
    "LF": "Grand Union Trains",
    "GN": "Great Nothern",
    "GW": "Great Western Railway",
    "LE": "Greater Anglia",
    "HX": "Heathrow Express",
    "HT": "Hull Trains",
    "IL": "Island Lines",
    "LO": "London Overground",
    "LT": "London Underground",
    "LN": "London Northwestern Railway",
    "GR": "LNER",
    "LD": "Lumo",
    "ME": "Merseyrail",
    "NT": "Northern Trains",
    "SR": "ScotRail",
    "SE": "Southeastern",
    "SN": "Southern",
    "SW": "South Western Railway",
    "SP": "Swanage Railway",
    "SX": "Stansted Express",
    "TP": "TransPennine Express",
    "AW": "Transport for Wales",
    "TL": "Thameslink",
    "WR": "West Coast Railways",
    "LM": "West Midlands Trains",
    "GX": "Gatwick Express",
    "WM": "West Midlands Railway",
}


if __name__ == "__main__":

    st.set_page_config(
        page_title="Incident Alerts",
        page_icon="🔔",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items=None,
    )

    with st.sidebar:
        st.image("logo.png", use_column_width=True)

    load_dotenv()

    sns = client("sns")
    TOPIC = ENV["TOPIC_ARN"]

    cont1, cont2, cont3 = st.columns((0.1, 1, 0.1))

    with cont2:

        with st.container(border=True, height=650):

            st.markdown(
                "<h2 style='text-align: center;'>Subscribe for alerts &#x1F514;</h2>",
                unsafe_allow_html=True,
            )
            st.markdown(
                """<p style='text-align: center;
                '>Enter your details below to receive
                live alerts and updates for service disruptions.</p>""",
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns((0.4, 2.8, 0.4))

            with col2:
                st.write("")
                st.write("Select train operator/s: ")
                selected_operators = st.multiselect(
                    "Select Train Operator/s: ",
                    options=OPERATORS.values(),
                    label_visibility="collapsed",
                )
                st.write("")
                st.write("Receive alerts via:")
                email_checkbox = st.checkbox("Email")

                if email_checkbox:
                    email = st.text_input("Enter email")
                else:
                    st.text_input("Enter email", disabled=True)
                    email = None

                phone_checkbox = st.checkbox("Mobile")

                if phone_checkbox:
                    phone_number = st.text_input("Enter mobile number")
                else:
                    st.text_input("Enter mobile number", disabled=True)
                    phone_number = None

                st.write("")

                st.button(
                    "Submit Form",
                    key="submit_button",
                    on_click=lambda: on_submit(
                        sns, TOPIC, selected_operators, email, phone_number
                    ),
                )
