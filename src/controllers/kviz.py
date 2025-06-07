from flask import Blueprint, jsonify
import db

bp_kviz = Blueprint('kviz', __name__)

@bp_kviz.route('/kviz')
def get_kviz_questions():
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT question, options, answer FROM quiz_questions;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    questions = [
        {"question": q, "options": opts, "answer": ans}
        for q, opts, ans in rows
    ]

    return jsonify(questions)