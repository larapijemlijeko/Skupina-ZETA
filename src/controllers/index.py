from flask import request, render_template

def home():
    return render_template("index.html")
