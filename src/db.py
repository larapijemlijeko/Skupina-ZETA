import os
import psycopg2
from dotenv import load_dotenv

def get_connection():
    load_dotenv()
    conn = psycopg2.connect(
        dbname = os.environ["DBNAME"],
        user = os.environ["DBUSER"],
        password = os.environ["DBPASS"],
        host = os.environ["DBHOST"]
    )
    return conn
