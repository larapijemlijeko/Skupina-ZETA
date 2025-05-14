import subprocess
import os
from datetime import datetime
import db
import psycopg2
import csv
from apscheduler.schedulers.background import BackgroundScheduler

def initializeScheduler():
    print('Starting backup scheduler')
    scheduler = BackgroundScheduler()
    # Run every hour, for example
    scheduler.add_job(createBackup, 'interval', hours=1)
    #scheduler.add_job(createBackup, 'interval', seconds=10) # For testing purposes only
    scheduler.start()

def createBackup():
    print('Starting backup')
    #Backup tabele uporabniki v csv
    backupTableToCsv("uporabniki")

    #Backup tabele recepti v csv
    backupTableToCsv("recepti")

    print('Backup done')

        


def backupTableToCsv(table_name):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM public." + table_name)
    with open(table_name + '_backup.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([desc[0] for desc in cursor.description])
        writer.writerows(cursor.fetchall())
