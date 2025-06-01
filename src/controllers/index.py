from flask import request, render_template
import db


def home():
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT navedek, avtor FROM navedki ORDER BY datum_kreiranja ASC")
    quotes = cur.fetchall()
    conn.close()

    quote_list = [{"navedek": q[0], "avtor": q[1]} for q in quotes]
    
    return render_template("index.html", quotes=quote_list)
