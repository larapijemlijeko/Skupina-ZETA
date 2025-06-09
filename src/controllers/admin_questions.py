from flask import Blueprint, render_template, request, redirect, url_for, flash
import db

admin_questions_bp = Blueprint('admin_questions', __name__)

@admin_questions_bp.route('/admin_questions', methods=['GET', 'POST'])
def admin_questions_site():
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        email = request.form.get('email', '').strip()
        if not question or not email:
            flash('Vsa polja so obvezna.', 'danger')
        else:
            try:
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO admin_questions (question, email) VALUES (%s, %s)",
                    (question, email)
                )
                conn.commit()
                cur.close()
                conn.close()
                flash('Vprašanje uspešno poslano!', 'success')
                return redirect(url_for('admin_questions.admin_questions_site'))
            except Exception as e:
                print(f"Napaka pri pošiljanju vprašanja: {e}")
                flash('Napaka pri pošiljanju vprašanja.', 'danger')
    return render_template('admin_questions_site.html')