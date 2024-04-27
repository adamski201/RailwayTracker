from dotenv import load_dotenv
from os import environ as ENV

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import psycopg2

operator_delays_sql_query = """SELECT operators.operator_name, operators.operator_code,  COUNT(*) AS number_of_delays FROM arrivals
                INNER JOIN services
                ON arrivals.service_id=services.service_id
                INNER JOIN operators
                ON services.operator_id=operators.operator_id
                WHERE arrivals.actual_arrival>arrivals.scheduled_arrival
                GROUP BY operators.operator_name, operators.operator_code
                ORDER BY operators.operator_name ASC
                ;"""

operator_arrivals_sql_query = """SELECT operators.operator_name, COUNT(*) AS total_arrivals FROM arrivals
                                INNER JOIN services
                                ON arrivals.service_id=services.service_id
                                INNER JOIN operators
                                ON services.operator_id=operators.operator_id
                                GROUP BY operators.operator_name
                                ORDER BY operators.operator_name ASC
                                ;"""

operator_cancellations_sql_query = """SELECT operators.operator_name, COUNT(*) AS total_cancellations FROM cancellations
                                    INNER JOIN services
                                    ON cancellations.service_id=services.service_id
                                    INNER JOIN operators
                                    ON services.operator_id=operators.operator_id
                                    GROUP BY operators.operator_name
                                    ORDER BY operators.operator_name ASC
                                    ;"""


def average_delay_per_hour_graph(conn: psycopg2.extensions.connection, station_crs: str) -> None:
    """This function creates a matplotlib plot of the average delay time per hour for a 
    station, given it's crs code.
    This function saves a jpg image to the current directory named 'average_delay_per_hour_graph.jpg'.

    _______"""

    sql_query = f"""SELECT  
                    EXTRACT(HOUR FROM arrivals.scheduled_arrival) AS hour, 
                    (ROUND(AVG((EXTRACT(EPOCH FROM (arrivals.actual_arrival - arrivals.scheduled_arrival)) / 60)), 2)) AS average_delay_minutes
                    FROM arrivals
                    INNER JOIN stations
                    ON stations.station_id=arrivals.station_id
                    WHERE stations.crs_code='{station_crs}'
                    AND
                    arrivals.actual_arrival > arrivals.scheduled_arrival
                    GROUP BY hour
                    ; """

    with conn.cursor() as cur:
        cur.execute(sql_query)
        delays_per_hour_data = cur.fetchall()

    plt.clf()
    sns.barplot(x=[i[0] for i in delays_per_hour_data],
                y=[i[1] for i in delays_per_hour_data])
    plt.xlabel("Hour of the Day")
    plt.ylabel("Average Delay Time")

    plt.savefig("average_delay_per_hour_graph.jpg")


def get_station_name(conn: psycopg2.extensions.connection, station_crs: str):

    with conn.cursor() as cur:
        cur.execute(f"""SELECT station_name FROM stations
                    WHERE crs_code='{station_crs}'""")
        station_name = cur.fetchone()

        if station_name:
            return station_name[0]


def get_delay_and_cancellation_percentages(conn: psycopg2.extensions.connection, station_crs: str) -> dict:
    """This function returns the delay and cancellation percentages for a station, given its
    station's crs code."""

    delay_num_query = f"""SELECT COUNT(*) FROM arrivals
                        INNER JOIN stations
                        ON arrivals.station_id=stations.station_id
                        WHERE arrivals.actual_arrival>arrivals.scheduled_arrival
                        AND
                        stations.crs_code='{station_crs}'
                        ;"""

    arrivals_num_query = f"""SELECT COUNT(*) FROM arrivals
                        INNER JOIN stations
                        ON arrivals.station_id=stations.station_id
                        WHERE stations.crs_code='{station_crs}'
                        ;"""

    cancellations_num_query = f"""SELECT COUNT(*) FROM cancellations
                                INNER JOIN stations
                                ON cancellations.station_id=stations.station_id
                                WHERE stations.crs_code='{station_crs}'
                                ;"""

    with conn.cursor() as cur:
        cur.execute(delay_num_query)
        num_of_delays = cur.fetchone()
        cur.execute(arrivals_num_query)
        num_of_arrivals = cur.fetchone()
        cur.execute(cancellations_num_query)
        num_of_cancellations = cur.fetchone()

    delay_percentage = round(int(
        num_of_delays[0])/(int(num_of_arrivals[0]+int(num_of_cancellations[0])))*100, 2)

    cancellation_percentage = round(int(
        num_of_cancellations[0])/(int(num_of_arrivals[0]+int(num_of_cancellations[0])))*100, 2)

    return {"delay_percentage": delay_percentage, "cancellation_percentage": cancellation_percentage}


def get_average_delay_time(conn: psycopg2.extensions.connection, station_crs: str) -> float:
    """This function returns the average delay time for a station given the station's
    crs code."""

    avg_delay_query = f"""SELECT 
                        ROUND(AVG((EXTRACT(EPOCH FROM (arrivals.actual_arrival - arrivals.scheduled_arrival)) / 60)), 2) AS average_delay_minutes 
                        FROM arrivals
                        INNER JOIN stations
                        ON stations.station_id=arrivals.station_id
                        WHERE stations.crs_code='{station_crs}'
                        ;"""

    with conn.cursor() as cur:
        cur.execute(avg_delay_query)
        average_delay = cur.fetchone()[0]

    return average_delay


def get_most_common_cancellation_reasons(conn: psycopg2.extensions.connection, station_crs: str) -> list[tuple]:
    """This function returns a list of tuples, where each tuple has information on a specific
    type of cancellation and the number of cancellations at the station (inputted via it's
    crs code) due to that cancellation type. """

    cancellation_reasons_query = """SELECT ct.cancellation_code, ct.description, COUNT(*) FROM cancellations
                INNER JOIN cancellation_types AS ct
                ON ct.cancellation_type_id=cancellations.cancellation_type_id
                GROUP BY ct.cancellation_code, ct.description
                ORDER BY COUNT(*) DESC
                LIMIT 5
                ;"""

    with conn.cursor() as cur:
        cur.execute(cancellation_reasons_query)
        cancellation_reasons = cur.fetchall()

    return cancellation_reasons


def cancellation_types_pie_chart(conn: psycopg2.extensions.connection, station_crs: str):
    """"""

    cancellation_data = get_most_common_cancellation_reasons(conn, station_crs)

    palette_color = sns.color_palette('dark')

    # plotting data on chart
    plt.clf()
    plt.title("Most Common Cancellation Reasons")
    plt.pie([i[2] for i in cancellation_data], labels=[i[0]
            for i in cancellation_data], colors=palette_color, autopct='%1.1f%%')

    plt.savefig("cancellation_reason_pie_chart.jpg")


def generate_html(conn: psycopg2.extensions.connection, station_crs: str):

    delay_and_cancellation_percentages = get_delay_and_cancellation_percentages(
        conn, station_crs)

    average_delay = get_average_delay_time(conn, station_crs)

    station_name = get_station_name(conn, station_crs)

    average_delay_per_hour_graph(conn, station_crs)
    cancellation_types_pie_chart(conn, station_crs)

    cancellation_reasons = get_most_common_cancellation_reasons(
        conn, station_crs)

    table_html = ""
    for reason in cancellation_reasons:
        table_html += f"""<tr>
        <td>{reason[0]}</td>
        <td>{reason[1]}</td>
        <td>{reason[2]}</td>
        </tr>"""

    html = f"""<html> 
    <head>
        <title>Station Performance Report: {station_name}</title>
    </head>
    <body>
        <center>
            <h1>Station Performance Report: : {station_name}</h1>
            <h2>Delay Information</h2>
            <p><b>Percentage of Delays</b>: {delay_and_cancellation_percentages["delay_percentage"]}%      |       <b>Average Delay Time</b>: {average_delay} Minutes</p>
            <image><img  src="average_delay_per_hour_graph.jpg" alt="seaborn plot" style="width:400px;height:300px;"></image>
            <h2>Cancellation Information</h2>
            <p><b>Percentage of Cancellations</b>: {delay_and_cancellation_percentages["cancellation_percentage"]}%      |       <b>Most Common Cancellation Reason</b>: {cancellation_reasons[0][0]}</p>

            <image><img  src="cancellation_reason_pie_chart.jpg" alt="seaborn plot" style="width:400px;height:300px;"></image>

            <table>
                <tr>
                    <th>Cancellation Code</th>
                    <th>Cancellation Reason</th>
                    <th>Number of Cancellations</th>
                </tr>
                {table_html}
            </table>

        </center>
    </body>
</html>"""

    with open("pdf.html", "w") as f:
        f.write(html)

    return html


if __name__ == "__main__":
    load_dotenv()

    db_conn = psycopg2.connect(
        database=ENV["DB_NAME"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASS"],
        host=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
    )

    station_crs = 'KTN'

    html = generate_html(db_conn, station_crs)

    print(generate_html(db_conn, station_crs))

    db_conn.close()
