from flask import Blueprint, render_template
from datetime import datetime
import db

reported_content_bp = Blueprint('reported_content', __name__)

@reported_content_bp.route('/admin/reported_content', methods=['GET'])
def reported_content_site():
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, content_type, content_id, reason, reported_by, date_reported
        FROM reported_content
        ORDER BY date_reported DESC
    """)
    reported = [
        {
            "id": row[0],
            "content_type": row[1],
            "content_id": row[2],
            "reason": row[3],
            "reported_by": row[4],
            "date_reported": row[5].strftime("%Y-%m-%d %H:%M")
        }
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return render_template('reported_content.html', reported=reported)