from flask import request, render_template
from models.zaBazo import create_tables
from models.dbBackup import initializeScheduler

def home():
    create_tables()
    initializeScheduler()
    return render_template("index.html")
