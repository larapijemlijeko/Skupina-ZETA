from flask import render_template, request, redirect, url_for
import db
import controllers.index
import os
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = "static/uploads"  # ali kamor želiš shraniti slike
ALLOWED_EXTENSIONS = {"png", "jpg", "gif"}


def dovoljeno_ime(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def oddajrecept():
    if request.method == "POST":
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            # --- podatki o receptu ---
            naslov = request.form["naslov"]
            opis = request.form["opis"]
            priprava = request.form["priprava"]
            cas = request.form.get("cas_priprave")
            tezavnost = request.form.get("tezavnost")
            uporabnik_id = 1  # začasno fiksno

             # 🟩 Dopolnjeno: polje drzava
            drzava = request.form.get("drzava")

            # --- vstavi recept ---
            cur.execute("""
                INSERT INTO recepti (naslov, opis, priprava, cas_priprave, tezavnost, uporabnik_id, drzava)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """, (naslov, opis, priprava, cas, tezavnost, uporabnik_id, drzava))
            recept_id = cur.fetchone()[0]

            

            # 🟩 Dopolnjeno: regija_id
            regija_id = request.form.get("regija")
            if regija_id:
                cur.execute("""
                    INSERT INTO recepti_regije (recept_id, regija_id)
                    VALUES (%s, %s);
                """, (recept_id, regija_id))

            

            # --- podatki o sestavinah (seznami) ---
            imena = request.form.getlist("sestavina_ime[]")
            kolicine = request.form.getlist("sestavina_kolicina[]")
            enote = request.form.getlist("sestavina_enota[]")
            st_oseb = request.form.get("st_oseb", 1)  # default 1 če ni podano

            for ime, kolicina, enota in zip(imena, kolicine, enote):
                if ime.strip():  # preveri da ime ni prazno
                    cur.execute("""
                        INSERT INTO sestavine (recept_id, ime, kolicina, enota, st_oseb)
                        VALUES (%s, %s, %s, %s, %s);
                    """, (recept_id, ime, kolicina, enota, st_oseb))
            
            # --- PRIDOBI ID-je vseh sestavin tega recepta ---
            cur.execute("""
                SELECT id FROM sestavine WHERE recept_id = %s;
            """, (recept_id,))
            sestavina_ids = [row[0] for row in cur.fetchall()]

            # --- oznaka ---
            oznaka = request.form.get("oznaka", "").strip()
            if oznaka:
                cur.execute("""
                    INSERT INTO oznake (recept_id, oznaka)
                    VALUES (%s, %s);
                """, (recept_id, oznaka))

            # --- slike ---
            slike = request.files.getlist("slike")
            if slike:
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                for slika in slike:
                    if slika and slika.filename and dovoljeno_ime(slika.filename):
                        filename = secure_filename(slika.filename)
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        unique_filename = f"{timestamp}_{filename}"
                        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                        slika.save(filepath)
                        
                        cur.execute("""
                            INSERT INTO recept_slike (recept_id, slika_pot)
                            VALUES (%s, %s);
                        """, (recept_id, filepath))

            # --- alergeni ---
            alergeni_id = request.form.getlist("alergeni[]")
            for alergen_id in alergeni_id:
                for sestavina_id in sestavina_ids:
                    cur.execute("""
                        INSERT INTO sestavine_alergeni (sestavina_id, alergen_id)
                        VALUES (%s, %s)
                    """, (sestavina_id, alergen_id))

            conn.commit()
            print("Recept uspešno shranjen!")
            return controllers.index.home()

        except Exception as e:
            conn.rollback()
            print("Napaka:", e)
            # Dodaj več informacij o napaki
            import traceback
            traceback.print_exc()
        finally:
            cur.close()
            conn.close()

     # GET zahteva: naloži alergene za seznam v obrazcu
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, ime FROM alergeni ORDER BY ime;")
    alergeni = cur.fetchall()
    
    

     # 🟩 Dopolnjeno: naloži regije
    cur.execute("SELECT id, ime FROM regije ORDER BY ime;")
    regije = cur.fetchall()

    cur.close()
    conn.close()

    # If GET request or if POST failed, render the form template
    return render_template("oddajrecept.html", alergeni=alergeni, regije=regije)