import subprocess
import os
from datetime import datetime
import db
import psycopg2

def createBackup():
    # Database credentials (can come from .env or your app config)
    db_name = os.environ["DBNAME"]
    db_user = os.environ["DBUSER"]
    db_host = "db"  # or 'localhost' or 'db' if running inside Docker
    db_port = "5432"
    db_pass = os.environ["DBPASS"]

    # Output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"postgres_backup_{timestamp}.sql"

    # Set password for pg_dump
    env = os.environ.copy()
    env["PGPASSWORD"] = db_pass

    # Run pg_dump command
    try:
        subprocess.run(
            [
                "pg_dump",
                "-h", db_host,
                "-p", db_port,
                "-U", db_user,
                "-F", "c",          # custom format, you can use "plain" too
                "-b",               # include blobs
                "-f", backup_file,  # output file
                db_name
            ],
            env=env,
            check=True
        )
        print(f"Backup successful: {backup_file}")
    except subprocess.CalledProcessError as e:
        print("Backup failed:", e)
