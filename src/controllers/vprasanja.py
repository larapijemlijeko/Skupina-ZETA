from flask import render_template
import db

def vprasanja():
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT question, answer FROM faq ORDER BY id;")
        faq_items = cur.fetchall()
    except Exception as e:
        print("Napaka pri pridobivanju vprašanj:", e)
        faq_items = []
    finally:
        cur.close()
        conn.close()

    return render_template('vprasanja.html', faq_items=faq_items)