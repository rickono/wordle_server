import csv
import psycopg2
from config import config


def connect():
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
    except psycopg2.Error as err:
        print(err)
        return None

    return conn
