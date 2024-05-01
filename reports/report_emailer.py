"""A script that sends emails to all station subscribers."""

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from datetime import date
from os import makedirs, path, environ as ENV
import logging

import seaborn as sns
import matplotlib.pyplot as plt
from psycopg2 import connect
from psycopg2.extensions import connection
from xhtml2pdf import pisa
from boto3 import client
from dotenv import load_dotenv

S3_BUCKET = 'railway-tracker'


def setup_logging() -> None:
    """Sets up the logging configuration."""

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')


def get_db_connection(config: dict[str, str]) -> connection:
    """Returns a connection to a database."""

    return connect(
        host=config["DB_HOST"],
        user=config["DB_USER"],
        password=config["DB_PASS"],
        dbname=config["DB_NAME"],
        port=config["DB_PORT"],
    )


def get_s3_connection(config: dict[str, str]):
    """Returns a connection to a s3 client."""

    return client(
        "s3", aws_access_key_id=config["ACCESS_KEY_ID"], aws_secret_access_key=config["SECRET_ACCESS_KEY"])


def average_delay_per_hour_graph(conn: connection, station_crs: str) -> None:
    """This function creates a matplotlib plot of the average delay time (for delayed trains)
    per hour for a station, given it's crs code.
    This function saves a jpg image to the current directory named
    'average_delay_per_hour_graph.jpg'.
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
                    AND 
                    arrivals.scheduled_arrival >= DATE_TRUNC('day', NOW() - INTERVAL '7 day')
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

    plt.title("Average Delay Time for Delayed Trains (Past Week)")

    plt.savefig(f"{ENV['LOCAL_FOLDER']}/average_delay_per_hour_graph.jpg")


def get_station_name(conn: connection, station_crs: str) -> str:
    """This functions returns the name of a station given it's crs code."""

    with conn.cursor() as cur:
        cur.execute(f"""SELECT station_name FROM stations
                    WHERE crs_code='{station_crs}'""")
        station_name = cur.fetchone()

    if station_name:
        return station_name[0]

    return None


def get_delay_and_cancellation_percentages(conn: connection,
                                           station_crs: str) -> dict:
    """This function returns the delay and cancellation percentages for a station, given its
    station's crs code."""

    delay_num_query = f"""SELECT COUNT(*) FROM arrivals
                        INNER JOIN stations
                        ON arrivals.station_id=stations.station_id
                        WHERE arrivals.actual_arrival>arrivals.scheduled_arrival
                        AND
                        stations.crs_code='{station_crs}'
                        AND
                        arrivals.scheduled_arrival >= DATE_TRUNC('day', NOW() - INTERVAL '7 day')
                        ;"""

    arrivals_num_query = f"""SELECT COUNT(*) FROM arrivals
                        INNER JOIN stations
                        ON arrivals.station_id=stations.station_id
                        WHERE stations.crs_code='{station_crs}'
                        AND
                        arrivals.scheduled_arrival >= DATE_TRUNC('day', NOW() - INTERVAL '7 day')
                        ;"""

    cancellations_num_query = f"""SELECT COUNT(*) FROM cancellations
                                INNER JOIN stations
                                ON cancellations.station_id=stations.station_id
                                WHERE stations.crs_code='{station_crs}'
                                AND
                                cancellations.scheduled_arrival >= DATE_TRUNC('day', NOW() - INTERVAL '7 day')
                                ;"""

    with conn.cursor() as cur:
        cur.execute(delay_num_query)
        num_of_delays = cur.fetchone()
        cur.execute(arrivals_num_query)
        num_of_arrivals = cur.fetchone()
        cur.execute(cancellations_num_query)
        num_of_cancellations = cur.fetchone()

    delay_percentage = round(int(
        num_of_delays[0]) / (int(num_of_arrivals[0] + int(num_of_cancellations[0]))) * 100, 2)

    cancellation_percentage = round(int(
        num_of_cancellations[0]) / (int(num_of_arrivals[0] + int(num_of_cancellations[0]))) * 100,
                                    2)

    return {"delay_percentage": delay_percentage,
            "cancellation_percentage": cancellation_percentage}


def get_average_delay_time(conn: connection, station_crs: str) -> float:
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
                        AND
                        arrivals.scheduled_arrival >= DATE_TRUNC('day', NOW() - INTERVAL '7 day')
                        ;"""

    with conn.cursor() as cur:
        cur.execute(avg_delay_query)
        average_delay = cur.fetchone()[0]

    return average_delay


def get_most_common_cancellation_reasons(conn: connection,
                                         station_crs: str) -> list[tuple]:
    """This function returns a list of tuples, where each tuple has information on a specific
    type of cancellation and the number of cancellations at the station (inputted via it's
    crs code) due to that cancellation type. """

    cancellation_reasons_query = f"""SELECT ct.cancellation_code, ct.description, COUNT(*)
                FROM cancellations
                INNER JOIN cancellation_types AS ct
                ON ct.cancellation_type_id=cancellations.cancellation_type_id
                INNER JOIN stations 
                ON stations.station_id=cancellations.station_id
                WHERE stations.crs_code='{station_crs}'
                AND
                cancellations.scheduled_arrival >= DATE_TRUNC('day', NOW() - INTERVAL '7 day')
                GROUP BY ct.cancellation_code, ct.description
                ORDER BY COUNT(*) DESC
                LIMIT 5
                ;"""

    with conn.cursor() as cur:
        cur.execute(cancellation_reasons_query)
        cancellation_reasons = cur.fetchall()

    return cancellation_reasons


def cancellation_types_pie_chart(conn: connection, station_crs: str) -> None:
    """This function creates a pie chart of the station's most common cancellation
    reasons. The function saves an image to the current directory with the file name
    'cancellation_reason_pie_chart.jpg'. """

    cancellation_data = get_most_common_cancellation_reasons(conn, station_crs)

    palette_color = sns.color_palette('dark')

    # plotting data on chart
    plt.clf()

    plt.title("Most Common Cancellation Reasons (Past Week)")

    plt.pie([i[2] for i in cancellation_data],
            labels=[i[0] for i in cancellation_data], colors=palette_color,
            autopct='%1.1f%%')

    plt.savefig(f"{ENV['LOCAL_FOLDER']}/cancellation_reason_pie_chart.jpg")


def generate_html(conn: connection, station_crs: str, html_path: str, folder: str) -> None:
    """Given a station_crs code, this function saves a html file locally which produces a
    report on the corresponding station's delays and cancellations.
    It is saved to the specified html_path."""

    delay_and_cancellation_percentages = get_delay_and_cancellation_percentages(
        conn, station_crs)

    average_delay = get_average_delay_time(conn, station_crs)

    station_name = get_station_name(conn, station_crs)

    average_delay_per_hour_graph(conn, station_crs)

    cancellation_types_pie_chart(conn, station_crs)

    cancellation_reasons = get_most_common_cancellation_reasons(conn, station_crs)

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
            <img  src="{folder}/average_delay_per_hour_graph.jpg" alt="seaborn plot" style="width:400px;height:300px;">
            <h2>Cancellation Information</h2>
            <p><b>Percentage of  Cancellations</b>: {delay_and_cancellation_percentages["cancellation_percentage"]}%      |       <b>Most Common Cancellation Reason</b>: {cancellation_reasons[0][0]}</p>

            <img  src="{folder}/cancellation_reason_pie_chart.jpg" alt="seaborn plot" style="width:400px;height:300px;">

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


def convert_html_to_pdf(source_html: str, output_filename: str) -> None:
    """This function converts a html string into a pdf
    file saved in the current directory with the file name
    assigned by the 'output_filename' argument."""

    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        # the HTML to convert
        src=source_html,
        dest=result_file)  # file handle to receive result

    # close output file
    result_file.close()  # close output file

    # return False on success and True on errors
    return pisa_status.err


def generate_email_object(subject: str, body: str, attachment_file_path: str) -> MIMEMultipart:
    """This function generates an email object given a subject, body,
    and attachment file path."""

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg.attach(MIMEText(body))

    file = MIMEApplication(
        open(attachment_file_path, "rb").read(),
        name=path.basename(attachment_file_path))

    file['Content-Disposition'] = f'attachment; filename="{path.basename(attachment_file_path)}"'

    msg.attach(file)

    return msg


def email_sender(email: MIMEMultipart, email_destinations: list[str]) -> None:
    """This function sends an email via AWS SES. It accepts an email object (
    i.e. what to email) and the addresses to email to."""

    ses_client = client("ses",
                        region_name="eu-west-2",
                        aws_access_key_id=ENV["ACCESS_KEY_ID"],
                        aws_secret_access_key=ENV["SECRET_ACCESS_KEY"])

    ses_client.send_raw_email(
        Source=ENV["SOURCE_EMAIL"],
        Destinations=email_destinations,
        RawMessage={
            'Data': email.as_string()
        }
    )


def group_email_subscribers(conn: connection) -> dict:
    """This function returns a dictionary with station crs codes
    as keys and a list of the email addresses of weekly email
    report subscriber to that particular station as a values."""

    with conn.cursor() as cur:
        cur.execute("""SELECT users.email, stations.crs_code FROM station_subscriptions AS ss
                        INNER JOIN users ON
                        ss.user_id=users.user_id
                        INNER JOIN stations
                        ON ss.station_id=stations.station_id
                        """)
        recipient_details = cur.fetchall()

    crs_address_dict = {}

    for recipient in recipient_details:
        crs_address_dict[recipient[1]] = crs_address_dict.get(
            recipient[1], []) + [recipient[0]]

    return crs_address_dict


def add_report_to_bucket(aws_client, filename: str, bucket: str, object_name: str):
    """
    Uploads the pdf report into the bucket.
    """
    aws_client.upload_file(filename, bucket, object_name)


def handler(event: dict = None, context: dict = None) -> dict:
    """
    Adds logic from main into handler to be used in lambda.
    """

    setup_logging()

    load_dotenv()

    s3_client = get_s3_connection(ENV)

    db_conn = get_db_connection(ENV)

    local_folder = ENV['LOCAL_FOLDER']

    if not path.exists(f"{local_folder}/"):
        makedirs(f"{local_folder}/")

    subscriber_groups = group_email_subscribers(db_conn)

    for station_crs in subscriber_groups.keys():
        email_destinations = subscriber_groups[station_crs]
        logging.info("Email address extracted")

        station_name = get_station_name(db_conn, station_crs)
        logging.info("Station name extracted")

        html_file_name = f"{local_folder}/{station_crs}_{date.today()}.html"

        generate_html(db_conn, station_crs, html_file_name, local_folder)
        logging.info("HTML Generated")

        source_html = open(html_file_name, "r").read()
        pdf_filepath = f"{local_folder}/{station_crs}_{date.today()}.pdf"

        convert_html_to_pdf(source_html, pdf_filepath)
        logging.info("PDF Generated")

        subject = f"{station_name} Station Performance Report"
        body = f"Attached to this email is a report on the performance of {station_name} station."

        email_obj = generate_email_object(subject, body, pdf_filepath)
        logging.info("Email object created")

        email_sender(email_obj, email_destinations)
        logging.info("Email sent!")

        add_report_to_bucket(s3_client, pdf_filepath,
                             S3_BUCKET, f"{station_crs}/{pdf_filepath}")
        logging.info("Added report to bucket")

    db_conn.close()
    logging.info("Connection closed")

    return {
        "status": "Success!"
    }


if __name__ == "__main__":
    handler()
