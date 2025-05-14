from flask import request, render_template
from models.zaBazo import create_tables

def home():
    create_tables()
    return render_template("index.html")
