from flask import Blueprint, render_template, request, jsonify
import db

admin_bp = Blueprint('forums', __name__)

@admin_bp.route('/forums')
def forum_site():
    return render_template('forum_site.html')

@admin_bp.route('/api/forums')
def get_all_forums():
    try:
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 5))
        forums = get_db_all_forums(offset=offset, limit=limit)
    except Exception as e:
        return jsonify({"error": str(e)}), 500    
    if not forums:
        return jsonify({"message": "No forums found"}), 404
    return jsonify(forums), 200

def get_db_all_forums(offset=0, limit=5):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, naslov, vsebina, datum_objave FROM forum ORDER BY datum_objave DESC OFFSET %s LIMIT %s",
        (offset, limit)
    )
    forums = [
        {"id": row[0], "title": row[1], "content": row[2], "date": row[3].isoformat()}
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return forums

@admin_bp.route('/forum/<int:forum_id>')
def forum_display(forum_id):
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, naslov, vsebina, datum_objave FROM forum WHERE id = %s",
            (forum_id,)
        )
        forum = cur.fetchone()
        if not forum:
            cur.close()
            conn.close()
            return render_template('404.html'), 404

        forum_data = {
            "id": forum[0],
            "title": forum[1],
            "content": forum[2],
            "date": forum[3].isoformat()
        }

        cur.execute(
            "SELECT id, uporabnik_id, vsebina, datum_objave FROM komentarji WHERE forum_id = %s ORDER BY datum_objave ASC",
            (forum_id,)
        )
        comments = [
            {
                "id": row[0],
                "user_id": row[1],
                "content": row[2],
                "date": row[3].isoformat()
            }
            for row in cur.fetchall()
        ]
        cur.close()
        conn.close()
        return render_template('forum_display.html', forum=forum_data, comments=comments)
    except Exception as e:
        print(f"Error in forum_display: {e}")
        return jsonify({"error": str(e)}), 500