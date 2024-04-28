from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from datetime import date
import os


import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
from xhtml2pdf import pisa
from boto3 import client
from dotenv import load_dotenv


def average_delay_per_hour_graph(conn: psycopg2.extensions.connection, station_crs: str) -> None:
    """This function creates a matplotlib plot of the average delay time (for delayed trains)
    per hour for a station, given it's crs code.
    This function saves a jpg image to the current directory named 'average_delay_per_hour_graph.jpg'.
    """

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
    plt.title("Average Delay Time for Delayed Trains")

    plt.savefig("average_delay_per_hour_graph.jpg")


def get_station_name(conn: psycopg2.extensions.connection, station_crs: str) -> str:
    """This functions returns the name of a station given it's crs code."""

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
                        AND 
                        arrivals.actual_arrival > arrivals.scheduled_arrival
                        ;"""

    with conn.cursor() as cur:
        cur.execute(avg_delay_query)
        average_delay = cur.fetchone()[0]

    return average_delay


def get_most_common_cancellation_reasons(conn: psycopg2.extensions.connection, station_crs: str) -> list[tuple]:
    """This function returns a list of tuples, where each tuple has information on a specific
    type of cancellation and the number of cancellations at the station (inputted via it's
    crs code) due to that cancellation type. """

    cancellation_reasons_query = f"""SELECT ct.cancellation_code, ct.description, COUNT(*) FROM cancellations
                INNER JOIN cancellation_types AS ct
                ON ct.cancellation_type_id=cancellations.cancellation_type_id
                INNER JOIN stations 
                ON stations.station_id=cancellations.station_id
                WHERE stations.crs_code='{station_crs}'
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


def generate_html(conn: psycopg2.extensions.connection, station_crs: str, html_path: str):

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
            <h1>Station Performance Report: {station_name}</h1>
            <h2>Delay Information</h2>
            <p><b>Percentage of Delays</b>: {delay_and_cancellation_percentages["delay_percentage"]}%      |       <b>Average Delay Time</b>: {average_delay} Minutes</p>
            <img  src="average_delay_per_hour_graph.jpg" alt="seaborn plot" style="width:400px;height:300px;">
            <h2>Cancellation Information</h2>
            <p><b>Percentage of Cancellations</b>: {delay_and_cancellation_percentages["cancellation_percentage"]}%      |       <b>Most Common Cancellation Reason</b>: {cancellation_reasons[0][0]}</p>

            <img  src="cancellation_reason_pie_chart.jpg" alt="seaborn plot" style="width:400px;height:300px;">

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

    with open(html_path, "w") as f:
        f.write(html)

    return html


def convert_html_to_pdf(source_html, output_filename):

    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        # the HTML to convert
        src=source_html,
        dest=result_file)           # file handle to recieve result

    # close output file
    result_file.close()                 # close output file

    # return False on success and True on errors
    return pisa_status.err


def generate_email_object(subject: str, body: str, attachment_file_path: str):

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg.attach(MIMEText(body))

    file = MIMEApplication(
        open(attachment_file_path, "rb").read(),
        name=os.path.basename(attachment_file_path))

    file['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_file_path)}"'

    msg.attach(file)

    return msg


def email_sender(email: MIMEMultipart, email_destinations: list[str]):

    ses_client = client("ses",
                        region_name="eu-west-2",
                        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])

    ses_client.send_raw_email(
        Source='trainee.isaac.schaessens.coleman@sigmalabs.co.uk',
        Destinations=email_destinations,
        RawMessage={
            'Data': email.as_string()
        }
    )


if __name__ == "__main__":
    load_dotenv()

    db_conn = psycopg2.connect(
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
    )

    # email_destinations = [
    # "trainee.isaac.schaessens.coleman@sigmalabs.co.uk", "trainee.saniya.shaikh@sigmalabs.co.uk", "trainee.adam.osullivan@sigmalabs.co.uk",
    # "trainee.ariba.syeda@sigmalabs.co.uk"]

    email_destinations = ["trainee.isaac.schaessens.coleman@sigmalabs.co.uk"]

    station_crs = "HML"

    station_name = get_station_name(db_conn, station_crs)
    html_file_name = f"{station_crs}_{date.today()}.html"

    html = generate_html(db_conn, station_crs, html_file_name)

    source_html = open(html_file_name, "r").read()
    pdf_filepath = f"{station_crs}_{date.today()}.pdf"

    convert_html_to_pdf(source_html, pdf_filepath)

    subject = f"[TEST] {station_name} Station Performance Report"
    body = f"Attached to this email is a report on the performance of {station_name} station."

    print(station_name)

    email_obj = generate_email_object(subject, body, pdf_filepath)

    email_sender(email_obj, email_destinations)
    print('email sent')

    db_conn.close()
