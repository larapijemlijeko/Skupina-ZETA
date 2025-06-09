from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
import db

forum_bp = Blueprint('forums', __name__)

@forum_bp.route('/forums', methods=['GET', 'POST'])
@login_required
def forum_site():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        try:
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO forum (uporabnik_id, naslov, vsebina) VALUES (%s, %s, %s)",
                (current_user.id, title, content)
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('forums.forum_site'))
        except Exception as e:
            print(f"Error in forum_site (POST): {e}")
    return render_template('forum_site.html')

@forum_bp.route('/api/forums')
def get_all_forums():
    try:
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 10))
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

@forum_bp.route('/forum/<int:forum_id>')
def forum_display(forum_id):
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT f.id, f.naslov, f.vsebina, f.datum_objave, u.uporabnisko_ime, f.uporabnik_id
            FROM forum f
            LEFT JOIN uporabniki u ON f.uporabnik_id = u.id
            WHERE f.id = %s
        """, (forum_id,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return render_template('404.html'), 404

        forum_data = {
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "date": row[3].isoformat(),
            "author": row[4] or "System",
            "user_id": row[5]
        }

        cur.execute("""
            SELECT k.id, k.uporabnik_id, u.uporabnisko_ime, k.vsebina, k.datum_objave
            FROM komentarji_forum k
            LEFT JOIN uporabniki u ON k.uporabnik_id = u.id
            WHERE k.forum_id = %s
            ORDER BY k.datum_objave ASC
        """, (forum_id,))
        comments = [
            {
                "id": row[0],
                "user_id": row[1],
                "username": row[2] or "System",
                "content": row[3],
                "date": row[4].isoformat()
            }
            for row in cur.fetchall()
        ]
        cur.close()
        conn.close()
        return render_template('forum_display.html', forum=forum_data, comments=comments)
    except Exception as e:
        print(f"Error in forum_display: {e}")
        return jsonify({"error": str(e)}), 500

@forum_bp.route('/api/forums', methods=['POST'])
@login_required
def create_forum():
    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    if not title or not content:
        return jsonify({'error': 'Naslov in vsebina sta obvezna.'}), 400
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO forum (uporabnik_id, naslov, vsebina) VALUES (%s, %s, %s) RETURNING id",
            (current_user.id, title, content)
        )
        forum_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Forum uspešno ustvarjen.', 'id': forum_id}), 201
    except Exception as e:
        print(f"Error in create_forum: {e}")
        # Vrni tudi napako v JSON odgovoru za lažje debugiranje na frontendu
        return jsonify({'error': f'Napaka pri ustvarjanju foruma: {e}'}), 500

@forum_bp.route('/forum/<int:forum_id>/delete', methods=['POST'])
@login_required
def delete_forum(forum_id):
    conn = db.get_connection()
    cur = conn.cursor()
    # Preveri, če je trenutni uporabnik lastnik foruma
    cur.execute("SELECT uporabnik_id FROM forum WHERE id = %s", (forum_id,))
    row = cur.fetchone()
    if not row or row[0] != current_user.id:
        cur.close()
        conn.close()
        return redirect(url_for('forums.forum_display', forum_id=forum_id))
    try:
        cur.execute("DELETE FROM forum WHERE id = %s", (forum_id,))
        conn.commit()
    except Exception as e:
        print(f"Napaka pri brisanju foruma: {e}")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('forums.forum_site'))

@forum_bp.route('/forum/<int:forum_id>/comment', methods=['POST'])
@login_required
def add_comment(forum_id):
    content = request.form.get('comment', '').strip()
    if not content:
        return redirect(url_for('forums.forum_display', forum_id=forum_id))
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO komentarji_forum (forum_id, uporabnik_id, vsebina) VALUES (%s, %s, %s)",
            (forum_id, current_user.id, content)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Napaka pri dodajanju komentarja: {e}")
    return redirect(url_for('forums.forum_display', forum_id=forum_id))
