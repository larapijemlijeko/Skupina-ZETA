from flask import request, render_template
from models.zaBazo import create_tables
from models.dbBackup import createBackup

def home():
    create_tables()
    return render_template("index.html")
