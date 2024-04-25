from os import environ as ENV

from boto3 import client
from botocore import client as boto3_client
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
import pandas as pd


def get_db_connection(config) -> connection:
    """Returns a connection to a database."""

    return connect(
        host=config["DB_HOST"],
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        dbname=config["DB_NAME"],
        port=config["DB_PORT"],
        cursor_factory=RealDictCursor
    )


def get_s3_client(config) -> boto3_client:
    """Returns an S3 client with the provided credentials."""

    print(type(config))

    return client("s3",
                  aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                  aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])


def retrieve_old_data(conn: connection) -> pd.DataFrame:
    """Retrieves data older than 24 hours."""

    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM recordings WHERE recording_taken < GETDATE()-1;")
        rows = cur.fetchall()
        cur.execute(
            "DELETE FROM recordings WHERE recording_taken < GETDATE()-1;")

    conn.commit()

    print(rows)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    load_dotenv()

    conn = get_db_connection(ENV)
    s3_client = get_s3_client(ENV)
