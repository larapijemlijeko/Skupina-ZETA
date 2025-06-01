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
        # Preveri ali uporabnik že obstaja
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

        # Podatki za 4 recepte
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

        # DODAJ VPRAŠANJA V TABELO FAQ
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
       