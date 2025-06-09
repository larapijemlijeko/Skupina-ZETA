from flask import Blueprint, render_template, redirect, url_for
from models.dbBackup import createBackup
import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin_panel():
    return render_template('admin.html')
@admin_bp.route('/admin/dodaj')

@admin_bp.route('/admin/dodaj')
def dodaj_testne_podatke():
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        # 1. Uporabnik
        cur.execute("SELECT id FROM uporabniki WHERE uporabnisko_ime = 'adminuser'")
        uporabnik = cur.fetchone()
        if uporabnik:
            uporabnik_id = uporabnik[0]
        else:
            cur.execute("""
                INSERT INTO uporabniki (uporabnisko_ime, email, geslo)
                VALUES ('adminuser', 'admin@example.com', 'admin123')
                RETURNING id;
            """)
            uporabnik_id = cur.fetchone()[0]

        # 2. Recepti
        recepti = [
            ("Testni recept 1", "Opis Testni recept 1", "Navodila za pripravo Testni recept 1", 15, 1, "", "soli", "1", "žlička", 2, "Testna1"),
            ("Testni recept 2", "Opis Testni recept 2", "Navodila za pripravo Testni recept 2", 25, 2, "", "popra", "2", "žlički", 3, "Testna2"),
            ("Testni recept 3", "Opis Testni recept 3", "Navodila za pripravo Testni recept 3", 30, 3, "", "moke", "100", "g", 4, "Testna3"),
            ("Testni recept 4", "Opis Testni recept 4", "Navodila za pripravo Testni recept 4", 10, 1, "", "vode", "2", "dl", 1, "Testna4"),
        ]

        for naslov, opis, priprava, cas, tezavnost, slika, sest_ime, kolicina, enota, st_oseb, oznaka in recepti:
            cur.execute("""
                INSERT INTO recepti (naslov, opis, priprava, cas_priprave, tezavnost, slika_url, uporabnik_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (naslov, opis, priprava, cas, tezavnost, slika, uporabnik_id))
            recept_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO sestavine (recept_id, ime, kolicina, enota, st_oseb)
                VALUES (%s, %s, %s, %s, %s);
            """, (recept_id, sest_ime, kolicina, enota, st_oseb))

            cur.execute("""
                INSERT INTO oznake (recept_id, oznaka)
                VALUES (%s, %s);
            """, (recept_id, oznaka))
            # Tukaj dodaš alergene za "moke"
            if sest_ime == "moke":
                cur.execute("""
                    INSERT INTO alergeni (ime) VALUES ('Gluten')
                    ON CONFLICT (ime) DO NOTHING;
                """)
                cur.execute("SELECT id FROM alergeni WHERE ime = 'Gluten'")
                alergen_id = cur.fetchone()[0]

                cur.execute("""
                    SELECT id FROM sestavine WHERE recept_id = %s AND ime = %s
                """, (recept_id, sest_ime))
                sestavina_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO sestavine_alergeni (sestavina_id, alergen_id)
                    VALUES (%s, %s);
                """, (sestavina_id, alergen_id))

        # 3. FAQ
        faq_data = [
            ("Kako lahko dodam svoj recept?", "Za dodajanje recepta se prijavite in kliknite 'Oddaj recept'."),
            ("Ali lahko uporabljam recepte brez registracije?", "Da, brskanje po receptih je omogočeno tudi brez prijave."),
            ("Kaj je scraper funkcionalnost?", "To je funkcija, ki omogoča uvoz receptov iz drugih spletnih strani."),
        ]

        for question, answer in faq_data:
            cur.execute("""
                INSERT INTO faq (question, answer)
                VALUES (%s, %s)
                ON CONFLICT (question) DO NOTHING;
            """, (question, answer))

        # 4. Navedki (citati)
        quotes = [
            {"navedek": "One cannot think well, love well, sleep well, if one has not dined well.", "avtor": "Virginia Woolf"},
            {"navedek": "Let food be thy medicine and medicine be thy food.", "avtor": "Hippocrates"},
            {"navedek": "People who love to eat are always the best people.", "avtor": "Julia Child"},
            {"navedek": "The only way to get rid of a temptation is to yield to it.", "avtor": "Oscar Wilde"},
            {"navedek": "Food is our common ground, a universal experience.", "avtor": "James Beard"},
            {"navedek": "Life is uncertain. Eat dessert first.", "avtor": "Ernestine Ulmer"},
            {"navedek": "All you need is love. But a little chocolate now and then doesn't hurt.", "avtor": "Charles M. Schulz"},
            {"navedek": "Tell me what you eat, and I will tell you what you are.", "avtor": "Jean Anthelme"}
        ]

        for quote in quotes:
            cur.execute("""
                SELECT 1 FROM navedki WHERE navedek = %s AND avtor = %s
            """, (quote['navedek'], quote['avtor']))
            exists = cur.fetchone()
            if not exists:
                cur.execute("""
                    INSERT INTO navedki (navedek, avtor)
                    VALUES (%s, %s)
                """, (quote['navedek'], quote['avtor']))

        conn.commit()
        print("✅ Testni podatki uspešno dodani.")
    except Exception as e:
        conn.rollback()
        print("❌ Napaka pri dodajanju testnih podatkov:", e)
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/admin/izbrisi_podatke')
def izbrisi_vse_podatke():
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM oznake;")
        cur.execute("DELETE FROM sestavine;")
        cur.execute("DELETE FROM recepti;")
        cur.execute("DELETE FROM uporabniki;")
        cur.execute("DELETE FROM vsecki;")
        cur.execute("DELETE FROM favourite;")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Napaka:", e)
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/admin/izbrisi_tabele')
def izbrisi_tabele():
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DROP TABLE IF EXISTS oznake CASCADE;")
        cur.execute("DROP TABLE IF EXISTS sestavine CASCADE;")
        cur.execute("DROP TABLE IF EXISTS recepti CASCADE;")
        cur.execute("DROP TABLE IF EXISTS uporabniki CASCADE;")
        cur.execute("DROP TABLE IF EXISTS favourite CASCADE;")
        cur.execute("DROP TABLE IF EXISTS vsecki CASCADE;")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Napaka:", e)
    finally:
        cur.close()
        conn.close()


    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/admin/backup_podatki')
def backup_podatki():
    createBackup()

    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/admin/questions')
def admin_questions_showed():
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT email, question, date FROM admin_questions ORDER BY date DESC")
    questions = [
        {"email": row[0], "question": row[1], "date": row[2].strftime("%Y-%m-%d %H:%M")}
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return render_template('admin_questions_showed.html', questions=questions)