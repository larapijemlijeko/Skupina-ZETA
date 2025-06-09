from flask import request, render_template
import db
import random
def get_random_tip():
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT tip FROM cooking_tips;")
        tips = cur.fetchall()
        cur.close()
        conn.close()

        if tips:
            return random.choice(tips)[0]
        else:
            return "Ni nasvetov v bazi."
    except Exception as e:
        return f"Napaka pri povezavi z bazo: {e}"



def home():
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT navedek, avtor FROM navedki ORDER BY datum_kreiranja ASC")
    quotes = cur.fetchall()
    conn.close()
    tip = get_random_tip()
    quote_list = [{"navedek": q[0], "avtor": q[1]} for q in quotes]
    
    return render_template("index.html", quotes=quote_list, tip=tip)
