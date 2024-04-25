import psycopg2
from psycopg2._psycopg import connection, cursor
from dotenv import load_dotenv
from os import environ as ENV
import psycopg2.extras

load_dotenv()

conn = psycopg2.connect(
    database=ENV["DB_NAME"],
    user=ENV["DB_USER"],
    password=ENV["DB_PASS"],
    host=ENV["DB_HOST"],
    port=ENV["DB_PORT"],
)


cur = conn.cursor()


def get_station_names() -> list[str]:
    cur.execute(
        """
        SELECT station_name
        FROM stations
        """
    )

    return [x[0] for x in cur.fetchall()]
