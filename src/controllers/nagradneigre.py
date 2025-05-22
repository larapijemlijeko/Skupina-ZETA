from flask import Blueprint, request, redirect, flash
import db

bp_nagradneigre = Blueprint("nagradneigre", __name__)

@bp_nagradneigre.route("/nagradneigre", methods=["GET", "POST"])
def nagradne_igre():
    if request.method == "POST":
        email = request.form.get("email")
        if email:
            try:
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO nagradne_prijave (email) VALUES (%s)", (email,))
                conn.commit()
                flash("Uspešno si se prijavil na nagradno igro!", "success")
            except Exception as e:
                flash("Napaka: Ta e-mail je morda že prijavljen.", "danger")
            return redirect("/")
    return redirect("/")

