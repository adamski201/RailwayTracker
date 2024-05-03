"""Streamlit page for report subscription form."""

from __future__ import annotations
from os import environ as ENV

import psycopg2
from dotenv import load_dotenv

import streamlit as st
from psycopg2._psycopg import cursor
from data_access import get_station_names


def get_user(cur: cursor, first_name: str, last_name: str, email: str) -> int | None:
    cur.execute(
        """
        SELECT user_id
        FROM users
        WHERE email = %s
        AND first_name = %s
        AND last_name = %s;
        """,
        (email, first_name, last_name),
    )

    res = cur.fetchone()

    return res[0] if res else None


def upload_user(cur: cursor, first_name: str, last_name: str, email: str) -> int:
    sql = """
    INSERT INTO users
        ("first_name", "last_name", "email")
    VALUES 
        (%s, %s, %s)
    RETURNING user_id;
      """

    params = (first_name, last_name, email)

    cur.execute(sql, params)

    conn.commit()

    return cur.fetchone()[0]


def get_station_id(cur: cursor, station_name: str):
    """
    Attempts to match the station object to an existing entity in the database and extract
    its primary key. Otherwise, returns None.
    """
    cur.execute(
        """
        SELECT station_id
        FROM stations
        WHERE station_name = %s;
        """,
        (station_name,),
    )

    res = cur.fetchone()

    return res[0] if res else None


def upload_subscription(cur: cursor, user_id, station_id) -> None:
    sql = """
        INSERT INTO station_subscriptions
            ("is_active", "user_id", "station_id")
        VALUES 
            (%s, %s, %s)
        RETURNING user_id;
          """

    params = (True, user_id, station_id)

    cur.execute(sql, params)

    conn.commit()

    return cur.fetchone()[0]


if __name__ == "__main__":
    st.set_page_config(
        page_title="Reports",
        page_icon="🔔",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items=None,
    )

    with st.sidebar:
        st.image("logo.png", use_column_width=True)

    load_dotenv()

    conn = psycopg2.connect(
        database=ENV["DB_NAME"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASS"],
        host=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
    )

    cur = conn.cursor()

    load_dotenv()

    cont1, cont2, cont3 = st.columns((0.1, 1, 0.1))

    with cont2:

        with st.container(border=True, height=650):

            st.markdown(
                "<h2 style='text-align: center;'>Subscribe for weekly reports</h2>",
                unsafe_allow_html=True,
            )
            st.markdown(
                """<p style='text-align: center;
                '>Enter your details below to receive
                weekly summary reports for your station.</p>""",
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns((0.4, 2.8, 0.4))

            with col2:
                st.write("")
                first_name = st.text_input("Enter first name:")

                st.write("")
                last_name = st.text_input("Enter last name:")

                st.write("")
                email = st.text_input("Enter email:")

                st.write("")

                selected_station = st.selectbox(
                    "Select station: ",
                    options=get_station_names(cur),
                )

                st.write("")

                st.button(
                    "Submit Form",
                    key="submit_button",
                    on_click=lambda: subscribe(
                        cur, first_name, last_name, email, selected_station
                    ),
                )


def subscribe(
    cur: cursor, first_name: str, last_name: str, email: str, station_name: str
) -> None:

    if not first_name or not last_name or not email or not station_name:
        st.markdown(
            "<h5 style='text-align: center; color: crimson'>Invalid input: please make sure every field is filled in.</h5>",
            unsafe_allow_html=True,
        )
        return

    station_id = get_station_id(cur, station_name)

    user_id = get_user(cur, first_name, last_name, email)
    if user_id is None:
        user_id = upload_user(cur, first_name, last_name, email)

    upload_subscription(cur, user_id, station_id)
