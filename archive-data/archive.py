"""This file is responsible for moving the historical data from
the short-term storage (AWS RDS) to the long-term storage (S3 bucket)"""

from datetime import datetime
from os import environ as ENV

from boto3 import client
from botocore import client as boto3_client
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
import pandas as pd

STATIONS_FILENAME = f"stations-archived-data-{datetime.now().date()}.csv"
OPERATOR_FILENAME = f"operator-archived-data-{datetime.now().date()}.csv"

def get_db_connection(config: dict[str, str]) -> connection:
    """Returns a connection to a database"""

    return connect(
        host=config["DB_HOST"],
        user=config["DB_USER"],
        password=config["DB_PASS"],
        dbname=config["DB_NAME"],
        port=config["DB_PORT"],
        cursor_factory=RealDictCursor
    )


def get_s3_client(config: dict[str, str]) -> boto3_client:
    """Returns an S3 client with the provided credentials."""

    return client("s3",
                  aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                  aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])


def query_database(conn: connection, query: str) -> pd.DataFrame:
    """Fetches historical older than a week from the database
    and resets the table"""

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        # reset tables

    conn.commit()

    return pd.DataFrame(rows)


def get_stations_data():
    pass


def get_operators_data():
    pass


def add_csv_to_bucket(aws_client: boto3_client, filename: str, bucket: str, object_name: str) -> None:
    """Uploads csv into an S3 bucket"""

    aws_client.upload_file(filename, bucket, object_name)


if __name__ == "__main__":
    load_dotenv()

    conn = get_db_connection(ENV)

    s3_client = get_s3_client(ENV)

    # query the database
    historical_data_df_1 = query_database(conn, "select * from operators")
    historical_data_df_2 = query_database(conn, "select * from services")

    # combine the dataframes
    combined_df = pd.merge(historical_data_df_1, historical_data_df_2, on=['station_name'], how='outer')

    # fixme - check for and fill missing values with 0??
    combined_df.fillna(0, inplace=True)

    # Save to csv
    file = 'combined_station_delays.csv'
    if not combined_df.empty:
        combined_df.to_csv(file, index=False)

    # Upload to s3
    # add_csv_to_bucket(s3_client, file, ENV["S3_BUCKET"], file)
