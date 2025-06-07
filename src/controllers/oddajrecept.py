from flask import render_template, request, redirect, url_for
import db
import controllers.index

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
            slika_url = request.form["slika_url"]
            uporabnik_id = 244  # začasno fiksno

            # --- vstavi recept ---
            cur.execute("""
                INSERT INTO recepti (naslov, opis, priprava, cas_priprave, tezavnost, slika_url, uporabnik_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """, (naslov, opis, priprava, cas, tezavnost, slika_url, uporabnik_id))
            recept_id = cur.fetchone()[0]

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
    cur.close()
    conn.close()

    # If GET request or if POST failed, render the form template
    return render_template("oddajrecept.html", alergeni=alergeni)