import os
import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname=os.environ["DBNAME"],
        user=os.environ["DBUSER"],
        password=os.environ["DBPASS"],
        host=os.environ["DBHOST"]
    )
